#!/bin/bash

# Define the name of the script
script_name="google_patent.py"

# Define the log files for NL and US
log_file_NL_30000="/home/ubuntu/google-patent-scraper/output_NL_30000.log"
log_file_NL_40000="/home/ubuntu/google-patent-scraper/output_NL_40000.log"
log_file_US="/home/ubuntu/google-patent-scraper/output_US.log"

# Change directory to google-patent-scraper
cd /home/ubuntu/google-patent-scraper/ || exit

# Activate virtual environment
source venv/bin/activate

# Check if the script with the NL country code is already running
if pgrep -f "$script_name --country_code NL --from_index 30000 --to_index 40000" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    # Run the Python script with nohup for NL
    nohup python -u google_patent.py --country_code NL --from_index 30000 --to_index 40000 > "$log_file_NL_30000" 2>&1 &
fi

if pgrep -f "$script_name --country_code NL --from_index 40000 --to_index 50000" > /dev/null; then
    echo "Another instance of the script with country code NL is already running. Exiting."
else
    nohup python -u google_patent.py --country_code NL --from_index 40000 --to_index 50000 > "$log_file_NL_40000" 2>&1 &
fi
