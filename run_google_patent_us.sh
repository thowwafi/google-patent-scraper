#!/bin/bash

# Define the name of the script
script_name="copy_google_patent.py"

# Define the log files for NL and US
log_file_US_00000="/home/ubuntu/google-patent-scraper/output_US_00000.log"
log_file_US_10000="/home/ubuntu/google-patent-scraper/output_US_10000.log"
log_file_US_20000="/home/ubuntu/google-patent-scraper/output_US_20000.log"
log_file_US_30000="/home/ubuntu/google-patent-scraper/output_US_30000.log"
log_file_US="/home/ubuntu/google-patent-scraper/output_US.log"

# Change directory to google-patent-scraper
cd /home/ubuntu/google-patent-scraper/ || exit

# Activate virtual environment
source venv/bin/activate

# Check if the script with the NL country code is already running
if pgrep -f "$script_name --country_code US --from_index 0 --to_index 10000" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    # Run the Python script with nohup for NL
    nohup python -u copy_google_patent.py --country_code US --from_index 10000 --to_index 20000 > "$log_file_US_10000" 2>&1 &
fi

if pgrep -f "$script_name --country_code US --from_index 10000 --to_index 20000" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    # Run the Python script with nohup for NL
    nohup python -u copy_google_patent.py --country_code US --from_index 10000 --to_index 20000 > "$log_file_US_10000" 2>&1 &
fi

if pgrep -f "$script_name --country_code US --from_index 20000 --to_index 30000" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    nohup python -u copy_google_patent.py --country_code US --from_index 20000 --to_index 30000 > "$log_file_US_20000" 2>&1 &
fi

# if pgrep -f "$script_name --country_code US --from_index 30000 --to_index 60000" > /dev/null; then
#     echo "Another instance of the script with country code NL is already running. Exiting."
# else
#     nohup python -u copy_google_patent.py --country_code US --from_index 30000 --to_index 60000 > "$log_file_US_30000" 2>&1 &
# fi