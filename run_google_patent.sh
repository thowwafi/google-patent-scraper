#!/bin/bash

# Define the name of the script
script_name="google_patent.py"

# Define the log files for NL and US
log_file_NL="/home/ubuntu/google-patent-scraper/output_NL.log"
log_file_US="/home/ubuntu/google-patent-scraper/output_US.log"

# Change directory to google-patent-scraper
cd /home/ubuntu/google-patent-scraper/ || exit

# Activate virtual environment
source venv/bin/activate

# Check if the script with the NL country code is already running
if pgrep -f "$script_name --country_code NL" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    # Run the Python script with nohup for NL
    nohup python -u google_patent.py --country_code NL > "$log_file_NL" 2>&1 &
fi

# Check if the script with the US country code is already running
if pgrep -f "$script_name --country_code US" > /dev/null; then
    echo "Another instance of the script with country code US is already running. Exiting."
else
    # Run the Python script with nohup for US
    nohup python -u google_patent.py --country_code US > "$log_file_US" 2>&1 &
fi
