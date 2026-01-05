import urllib.request
import json
import ssl
from datetime import datetime, timedelta

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
    stop_id = "NSR:Quay:49217"
    target_lines = ["5", "6"]
    minutes_ahead = 60
    output_file = "output.txt"
    
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

        now = datetime.now()
        end_time = now + timedelta(minutes=minutes_ahead)

        valid_departures = find_departures_timslot(data, now, end_time, target_lines)

        print_departures(valid_departures)

        time_strings = [t.strftime("%H:%M") for t, _, _ in valid_departures]
        output_content = ";".join(time_strings)

        with open(output_file, "w") as f:
            f.write(output_content)
        
        print(f"Successfully wrote {len(time_strings)} departures to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
