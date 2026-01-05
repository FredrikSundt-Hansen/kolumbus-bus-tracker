# Kolumbus Bus Tracker

A lightweight Python CLI tool to fetch and monitor real-time bus departures from the Kolumbus API.

## Description

This script retrieves real-time departure information for specific bus lines from a designated stop (Quay) using the public Kolumbus API. It outputs the departure times to a text file and prints detailed information (line, destination, time) to the console.

Key features:
- **Configurable**: Easily change target stops, lines, and time windows via a `.env` file.
- **Dependency-lite**: Uses Python's standard `urllib` for API requests, keeping dependencies minimal.
- **Automated Logging**: Saves upcoming departure times to a file (e.g., `output.txt`) for easy integration with other tools or dashboards.

## Prerequisites

- Python 3.7+
- `pip` (Python package installer)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/FredrikSundt-Hansen/kolumbus-bus-tracker.git
    cd kolumbus-bus-tracker
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install python-dotenv
    ```

## Configuration

Create a `.env` file in the project root to configure the tracker. You can base it on the example below:

**File: `.env`**
```env
# The ID of the stop/quay (e.g., Alti Tasta)
# You can find these IDs via the Kolumbus API or Entur registry.
STOP_ID=NSR:Quay:49217

# Comma-separated list of bus lines to track
TARGET_LINES=5,6

# How far into the future to look for departures (in minutes)
MINUTES_AHEAD=60

# The file where departure times will be saved (semicolon-separated)
OUTPUT_FILE=output.txt
```

## Usage

Run the script from your terminal:

```bash
python3 kolumbus.py
```

### Output

**Console Output:**
The script prints detailed departure information for verification:
```text
Line 5 at 17:21
Line 6 at 17:26
Line 6 at 17:27
...
Successfully wrote 9 departures to output.txt
```

**File Output (`output.txt`):**
A simple, semicolon-separated list of departure times (HH:MM), useful for parsing by other scripts/widgets:
```text
17:21;17:26;17:27;17:35;...
```

## License

This project is open-source and available under the [MIT License](LICENSE).
