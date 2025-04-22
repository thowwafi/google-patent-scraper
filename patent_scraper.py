import os
import pandas as pd
import sqlite3
import time
import contextlib
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

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


def get_citation_page_source(driver, publication_number):
    url = f"https://patents.google.com/patent/{publication_number}/en?oq={publication_number}"
    max_retries = 3
    retry_delay = 5  # seconds
    is_404 = False
    for attempt in range(max_retries):
        try:
            driver.get(url)
            with contextlib.suppress(TimeoutException):
                is_404 = WebDriverWait(driver, 5).until(EC.title_contains("404"))
                if is_404:
                    return "", is_404
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "footer"))
            )
            break
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise e
    return driver.page_source, is_404


def get_data_tables(soup, number, div_id):
    h3_pc = soup.find("h3", id=div_id)
    if not h3_pc:
        return []
    pc_table = h3_pc.find_next("div", class_="responsive-table")
    data = []
    for tr in pc_table.find_all("div", class_="tr"):
        if tr.text.strip().startswith("Publication") or tr.text.strip().startswith(
            "Family"
        ):
            continue
        citation_number = (
            tr.find_all("span", class_="td")[0].text.replace(" ", "").replace("\n", "")
        )
        cited_by = ""
        if "*" in citation_number:
            cited_by = "examiner"
        elif "†" in citation_number:
            cited_by = "third_party"
        elif "‡" in citation_number:
            cited_by = "family_to_family"
        patent_citation = citation_number.strip()
        publication_date = tr.find_all("span", class_="td")[2].text.strip()
        assignee = tr.find_all("span", class_="td")[3].text.strip()
        title = tr.find_all("span", class_="td")[4].text.strip()
        citation = {
            "publication_number": number,
            "patent_citation": patent_citation,
            "publication_date": publication_date,
            "assignee": assignee,
            "title": title,
            "cited_by": cited_by,
        }
        data.append(citation)
    return data


def get_a_citation_data(html, publication_number, original_number, country_code):
    patent_citations = []
    non_patent_citations = []
    data_cited_by = []
    soup = BeautifulSoup(html, "html.parser")
    total_cited_by = 0
    total_patent_citations = 0

    patent_title = soup.find("h1", id="title").text.strip()
    cited_by_el = soup.find("a", href="#citedBy")
    if cited_by_el:
        cited_by_text = cited_by_el.text
        total_cited_by = int(cited_by_text.split("(")[1].split(")")[0])

    patent_citations_text_el = soup.find("a", href="#patentCitations")
    if patent_citations_text_el:
        patent_citations_text = patent_citations_text_el.text
        total_patent_citations = int(patent_citations_text.split("(")[1].split(")")[0])

    abstract_div = soup.find("div", class_="abstract style-scope patent-text")
    if not abstract_div:
        abstract = ""
    else:
        abstract = (
            abstract_div.text.strip()
            .replace(";", " ")
            .replace("\n", " ")
            .replace("\t", " ")
        )

    status_div = soup.find(
        "div", class_="legal-status style-scope application-timeline", string="Status"
    )
    if not status_div:
        status = ""
    else:
        status = status_div.find_next(
            "span", class_="title-text style-scope application-timeline"
        ).text.strip()

    claim_text = ""
    description_text = ""
    total_claims = 0
    claim_id = soup.find("section", id="claims")
    if country_code == "NL":
        for claim in claim_id.find_all("claim"):
            parent_span = claim.find(class_="notranslate style-scope patent-text")
            if parent_span:
                english_text = "".join(
                    [
                        str(child)
                        for child in parent_span.children
                        if isinstance(child, str)
                    ]
                )
                claim_text += english_text
                claim_text = (
                    claim_text.replace(";", " ")
                    .replace("\n", " ")
                    .replace("\t", " ")
                    .strip()
                )
        total_claims = len(claim_id.find_all("claim"))

        description = soup.find("description")
        if description:
            for desc in description.find_all("p"):
                parent_span_desc = desc.find(
                    class_="notranslate style-scope patent-text"
                )
                if parent_span_desc:
                    english_text_desc = "".join(
                        [
                            str(child)
                            for child in parent_span_desc.children
                            if isinstance(child, str)
                        ]
                    )
                    description_text += english_text_desc
                    description_text = (
                        description_text.replace(";", " ")
                        .replace("\n", " ")
                        .replace("\t", " ")
                        .strip()
                    )
    elif country_code == "US":
        claim_text = (
            soup.find("patent-text", {"name": "claims"})
            .text.replace(";", " ")
            .replace("\n", " ")
            .replace("\t", " ")
            .strip()
        )
        description_text = (
            soup.find("patent-text", {"name": "description"})
            .text.replace(";", " ")
            .replace("\n", " ")
            .replace("\t", " ")
            .strip()
        )
        claim_subtitle = claim_id.find("h3")
        if claim_subtitle:
            claim_subtitle_text = claim_subtitle.text
            match = re.search(
                r"Claims \((\d+)\)", claim_subtitle_text
            )  # get the number of claims
            if match:
                total_claims = match[1]
            else:
                print("No digit number found in the text")

    patent_data = {
        "publication_number": publication_number,
        "original_number": original_number,
        "patent_title": patent_title,
        "abstract": abstract,
        "description": description_text,
        "claims": claim_text,
        "total_number_of_claims": total_claims,
        "total_cited_by": total_cited_by,
        "total_patent_citations": total_patent_citations,
        "status": status,
    }

    if not soup.find("h3", id="patentCitations"):
        citation = {
            "publication_number": publication_number,
            "patent_citation": 0,
            "publication_date": 0,
            "assignee": 0,
            "title": 0,
            "cited_by": "",
        }
        patent_citations.append(citation)
    else:
        citations = get_data_tables(soup, publication_number, "patentCitations")
        patent_citations.extend(iter(citations))

    if not soup.find("h3", id="citedBy"):
        citation = {
            "publication_number": publication_number,
            "patent_citation": 0,
            "publication_date": 0,
            "assignee": 0,
            "title": 0,
            "cited_by": "",
        }
        data_cited_by.append(citation)
    else:
        cited_bys = get_data_tables(soup, publication_number, "citedBy")
        data_cited_by.extend(iter(cited_bys))

    if not soup.find("h3", id="nplCitations"):
        citation = {
            "publication_number": publication_number,
            "patent_citation": 0,
            "publication_date": 0,
            "assignee": 0,
            "title": 0,
        }
        non_patent_citations.append(citation)
    else:
        h3_pc = soup.find("h3", id="nplCitations")
        pc_table = h3_pc.find_next("div", class_="responsive-table")
        for tr in pc_table.find_all("div", class_="tr")[1:]:
            citation = {
                "publication_number": publication_number,
                "patent_citation": 0,
                "publication_date": 0,
                "assignee": 0,
                "title": tr.text.replace("*", "").strip(),
            }
            non_patent_citations.append(citation)

    return patent_data, patent_citations, non_patent_citations, data_cited_by


# Add more robustness with retries for each patent
def process_patent_with_retry(row_data, max_attempts=3):
    publication_number = row_data["publication_number"]
    original_number = row_data["patent_num"]

    for attempt in range(1, max_attempts + 1):
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
        html, is_404 = get_citation_page_source(driver, publication_number)
        if is_404:
            print(f"404 error for {publication_number}, skipping...")
            conn.close()
            return False

        patent_data, patent_citations, non_patent_citations, data_cited_by = (
            get_a_citation_data(html, publication_number, original_number, "US")
        )

        insert_to_patent_datas(conn, patent_data)
        for citation in patent_citations:
            insert_to_patent_citations(conn, citation)
        for citation in non_patent_citations:
            insert_to_non_patent_citations(conn, citation)
        for citation in data_cited_by:
            insert_to_data_cited_by(conn, citation)

        print(
            f"{index}/{total_data} {publication_number} processed successfully"
        )
        
        # try:
        #     test = ""
        # except Exception as e:
        #     print(
        #         f"Error processing {publication_number} (attempt {attempt}/{max_attempts}): {str(e)}"
        #     )
        #     if "conn" in locals() and conn:
        #         conn.close()
        #     if attempt < max_attempts:
        #         time.sleep(5)  # Wait before retry
        #     continue

    return False


if __name__ == "__main__":
    # Get worker information from environment
    worker_id = int(os.environ.get("WORKER_ID", 0))
    total_workers = int(os.environ.get("TOTAL_WORKERS", 1))
    
    # Load data
    path = os.path.abspath("source/data_sic_36_NA_copy.csv")
    data = pd.read_csv(path, sep=",")
    
    # Partition the data for this worker
    worker_data = data[data.index % total_workers == worker_id]
    
    print(f"Worker {worker_id}/{total_workers} processing {len(worker_data)} patents out of {len(data)} total")
    
    # Process only this worker's partition
    total_data = len(worker_data)

    # Setup database
    db_path = "patent_data.db"
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
    success_count = 0
    failure_count = 0

    for index, row in worker_data.iterrows():
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
