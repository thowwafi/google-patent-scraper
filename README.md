# google-patent-scraper
### deprecated

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

# Update 25 April 2025

# For debugging purpose
```
docker compose build
docker compose run --rm patent-scraper-1 /bin/bash
python -m pdb patent_scraper.py
```

# Production script
```
BATCH_NUMBER=1 docker compose up --build
BATCH_NUMBER=2 docker compose up --build
BATCH_NUMBER=3 docker compose up --build
...
```

# Check logs
```
for container in $(docker ps -q --filter name=google-patent-scraper-patent-scraper); do
  docker logs -f $container --tail=100 &
done
```