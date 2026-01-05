import urllib.request
import json
import ssl
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def find_departures_timslot(data, now, end_time, target_lines):
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
        
            if dep_time.tzinfo and now.tzinfo is None:
                dep_time_naive = dep_time.replace(tzinfo=None)
            else:
                dep_time_naive = dep_time
                
            if now <= dep_time_naive <= end_time:
                departures.append((dep_time_naive, line_ref))
                
        except ValueError:
            continue

    departures.sort(key=lambda x: x[0])
    return departures

def print_departures(valid_departures):
    for dep in valid_departures:
        dep_time, line_ref = dep
        print(f"Line {line_ref} at {dep_time.strftime('%H:%M')}")

def main():
    stop_id = os.getenv("STOP_ID")
    target_lines_str = os.getenv("TARGET_LINES", "")
    target_lines = [line.strip() for line in target_lines_str.split(",") if line.strip()]
    minutes_ahead = int(os.getenv("MINUTES_AHEAD", "60"))
    output_file = os.getenv("OUTPUT_FILE", "output.txt")
    
    url = f"https://api.kolumbus.no/api/platforms/{stop_id}/departures"
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json;v=2')
        
        with urllib.request.urlopen(req, context=context) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
            else:
                print(f"Failed to fetch data. Status code: {response.getcode()}")
                return

        now = datetime.now()
        end_time = now + timedelta(minutes=minutes_ahead)

        valid_departures = find_departures_timslot(data, now, end_time, target_lines)

        print_departures(valid_departures)

        time_strings = [t.strftime("%H:%M") for t, _ in valid_departures]
        output_content = ";".join(time_strings)

        with open(output_file, "w") as f:
            f.write(output_content)
        
        print(f"Successfully wrote {len(time_strings)} departures to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
