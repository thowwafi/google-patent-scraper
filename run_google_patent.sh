#!/bin/bash

# Define the path to your Python script
python_script="/home/ubuntu/google-patent-scraper/google_patent.py"

# Define the path to your log file
log_file="/home/ubuntu/google-patent-scraper/output.log"

# Check if another instance of the script is already running
if pgrep -f "$python_script" > /dev/null; then
    echo "Another instance of the script is already running. Exiting."
    exit 1
fi

# Run the Python script with nohup
nohup /home/ubuntu/google-patent-scraper/venv/bin/python -u "$python_script" --country_code NL > "$log_file" 2>&1 &
