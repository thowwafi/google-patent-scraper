# google-patent-scraper

Put your CSV files in source folder:
- source/NL_patent_raw.csv
- source/US_match_patent.csv

Run the following command:
```
python google_patent.py --country_code NL --from_index 5 --to_index 10
```
or
```
python google_patent.py --country_code US --from_index 5 --to_index 10
```


docker compose build
docker compose run --rm patent-scraper /bin/bash

# Once inside, you can run your script manually
python -m pdb patent_scraper.py
docker-compose up --scale patent-scraper=3