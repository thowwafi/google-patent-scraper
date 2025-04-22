import os
import pandas as pd
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from database import (
    create_tables,
    insert_to_patent_datas,
    insert_to_patent_citations,
    insert_to_non_patent_citations,
    insert_to_data_cited_by,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log")],
)


def scrape_patent_data(driver, publication_number):
    """Scrape patent data from Google Patents."""
    url = f"https://patents.google.com/patent/{publication_number}"
    driver.get(url)


# Add more robustness with retries for each patent
def process_patent_with_retry(row_data, max_attempts=3):
    publication_number = row_data["publication_number"]

    for attempt in range(1, max_attempts + 1):
        try:
            # Connect to database
            conn = sqlite3.connect(db_path, timeout=30)

            # Double-check to avoid race conditions
            cursor = conn.cursor()
            cursor.execute(
                "SELECT publication_number FROM patent_datas WHERE publication_number = ?",
                (publication_number,),
            )
            if cursor.fetchone():
                print(f"{publication_number} was added by another process")
                conn.close()
                return True

            # Scrape the patent data
            patent_info = scrape_patent_data(driver, publication_number)

            # if patent_info:
            #     # Save to database
            #     save_patent_to_db(conn, patent_info, row_data)
            #     print(f"Saved {publication_number} to database")
            #     conn.close()
            #     return True
            # else:
            #     print(
            #         f"Failed to scrape {publication_number} (attempt {attempt}/{max_attempts})"
            #     )
            #     conn.close()
            #     if attempt < max_attempts:
            #         time.sleep(5)  # Wait before retry
            #     continue

        except Exception as e:
            print(
                f"Error processing {publication_number} (attempt {attempt}/{max_attempts}): {str(e)}"
            )
            if "conn" in locals() and conn:
                conn.close()
            if attempt < max_attempts:
                time.sleep(5)  # Wait before retry
            continue

    return False


if __name__ == "__main__":
    # Configure paths for Docker environment
    path = os.path.abspath("source/data_sic_36_NA_copy.csv")
    db_path = "patent_data.db"

    # Load data
    data = pd.read_csv(path, sep=",")

    # Setup database
    conn = sqlite3.connect(db_path)
    create_tables(conn)

    # Get existing publication numbers
    cursor = conn.cursor()
    cursor.execute("SELECT publication_number FROM patent_datas")
    existing_publication_numbers = set([row[0] for row in cursor.fetchall()])
    conn.close()

    # Configure Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--window-size=1920,1080")

    # Connect to remote Selenium Grid
    selenium_url = os.environ.get("SELENIUM_REMOTE_URL", "http://chrome:4444/wd/hub")
    print(f"Connecting to Selenium at: {selenium_url}")

    # Wait for Chrome service to be ready
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        try:
            driver = webdriver.Remote(
                command_executor=selenium_url, options=chrome_options
            )
            print("Successfully connected to Chrome service")
            break
        except Exception as e:
            retry_count += 1
            print(
                f"Attempt {retry_count}/{max_retries} to connect to Chrome service failed: {str(e)}"
            )
            if retry_count >= max_retries:
                print("Failed to connect to Chrome service after maximum retries")
                exit(1)
            time.sleep(5)

    # Process each patent
    total_data = len(data)
    success_count = 0
    failure_count = 0

    for index, row in data.iterrows():
        row_data = row.to_dict()

        if process_patent_with_retry(row_data):
            success_count += 1
        else:
            failure_count += 1

        # Random delay to avoid being blocked
        delay = 2 + (index % 3)
        print(f"Waiting {delay} seconds before next patent...")
        time.sleep(delay)

    # Clean up
    driver.quit()
    print(f"Scraping completed! Success: {success_count}, Failures: {failure_count}")
