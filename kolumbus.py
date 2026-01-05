import urllib.request
import json
import ssl
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from dotenv import load_dotenv

# Constants
API_URL_TEMPLATE = "https://api.kolumbus.no/api/platforms/{stop_id}/departures"

def fetch_departures(stop_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetches departure data from the Kolumbus API for a given stop ID.

    Args:
        stop_id: The ID of the stop (platform/quay).
    
    Returns:
        A list of departure dictionaries if successful, None otherwise.
    """
    url = API_URL_TEMPLATE.format(stop_id=stop_id)
    
    try:
        # Use unverified context to match environment constraints if needed
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json;v=2')
        
        with urllib.request.urlopen(req, context=context) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                raise Exception(f"Failed to fetch data. Status code: {response.getcode()}")
        
    except Exception as e:
        print(f"An error occurred fetching data: {e}")
        return None

def find_departures_in_timeslot(
    data: List[Dict[str, Any]], 
    target_lines: List[str], 
    now: datetime, 
    end_time: datetime
) -> List[Tuple[datetime, str]]:
    """
    Filters departures based on line number and time window.

    Args:
        data: List of departure data from API.
        target_lines: List of line numbers/names to include.
        now: Current time (start of window).
        end_time: End time of window.

    Returns:
        List of tuples (departure_time, line_name) sorted by time.
    """
    departures = []
    
    for dep in data:
        line_ref = dep.get('line_name')
        if line_ref not in target_lines:
            continue
        
        time_str = dep.get('expected_arrival_time')
        if not time_str:
            continue
            
        try:
            dep_time = datetime.fromisoformat(time_str)
            
            if dep_time.tzinfo is not None and now.tzinfo is None:
                dep_time_naive = dep_time.replace(tzinfo=None)
            else:
                dep_time_naive = dep_time
                
            if now <= dep_time_naive <= end_time:
                departures.append((dep_time_naive, line_ref))
                
        except ValueError:
            continue

    departures.sort(key=lambda x: x[0])
    return departures

def write_output(valid_departures: List[Tuple[datetime, str]], output_file: str) -> None:
    """
    Writes the departure times to the specified output file.

    Args:
        valid_departures: List of (time, line) tuples.
        output_file: Path to the output file.
    """
    time_strings = [t.strftime("%H:%M") for t, _ in valid_departures]
    output_content = ";".join(time_strings)

    try:
        with open(output_file, "w") as f:
            f.write(output_content)
        print(f"Successfully wrote {len(time_strings)} departures to {output_file}")
    except IOError as e:
        print(f"Failed to write output file: {e}")

def main():
    load_dotenv()
    
    stop_id = os.getenv("STOP_ID")
    if not stop_id:
        print("Error: STOP_ID not found in environment variables.")
        sys.exit(1)

    target_lines_str = os.getenv("TARGET_LINES", "")
    if not target_lines_str:
         print("Warning: TARGET_LINES is empty or missing.")
         
    target_lines = [line.strip() for line in target_lines_str.split(",") if line.strip()]
    minutes_ahead = int(os.getenv("MINUTES_AHEAD", "60"))
    output_file = os.getenv("OUTPUT_FILE", "output.txt")
    
    data = fetch_departures(stop_id)
    if not data:
        return

    now = datetime.now()
    end_time = now + timedelta(minutes=minutes_ahead)

    valid_departures = find_departures_in_timeslot(data, target_lines, now, end_time)

    write_output(valid_departures, output_file)

if __name__ == "__main__":
    main()
