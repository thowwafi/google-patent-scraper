#!/bin/bash

# Define the name of the script
script_name="copy_google_patent.py"

# Define the log files for NL and US
log_file_US_460000="/home/ubuntu/google-patent-scraper/output_US_460000.log"
log_file_US_470000="/home/ubuntu/google-patent-scraper/output_US_470000.log"
log_file_US_480000="/home/ubuntu/google-patent-scraper/output_US_480000.log"

# Change directory to google-patent-scraper
cd /home/ubuntu/google-patent-scraper/ || exit

# Activate virtual environment
source venv/bin/activate

if pgrep -f "$script_name --country_code US --from_index 460000 --to_index 470000" > /dev/null; then
   echo "Another instance of the script with country code US is already running. Exiting."
else
   # Run the Python script with nohup for US
   nohup python -u copy_google_patent.py --country_code US --from_index 460000 --to_index 470000 > "$log_file_US_460000" 2>&1 &
fi

if pgrep -f "$script_name --country_code US --from_index 470000 --to_index 480000" > /dev/null; then
   echo "Another instance of the script with country code US is already running. Exiting."
else
   # Run the Python script with nohup for US
   nohup python -u copy_google_patent.py --country_code US --from_index 470000 --to_index 480000 > "$log_file_US_470000" 2>&1 &
fi

if pgrep -f "$script_name --country_code US --from_index 480000 --to_index 490000" > /dev/null; then
   echo "Another instance of the script with country code US is already running. Exiting."
else
   # Run the Python script with nohup for US
   nohup python -u copy_google_patent.py --country_code US --from_index 480000 --to_index 490000 > "$log_file_US_480000" 2>&1 &
fi