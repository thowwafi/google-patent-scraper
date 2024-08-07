import argparse
import contextlib
import sqlite3
import sys
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
import os
from multiprocessing import Pool, cpu_count, Semaphore, Manager
from utils.utils import make_dir_if_not_exists, send_email
from database import (
    create_tables,
    insert_to_patent_datas,
    insert_to_patent_citations,
    insert_to_non_patent_citations,
    insert_to_data_cited_by,
)

# Initialize semaphore globally for process synchronization
semaphore = Semaphore(4)

# Get absolute paths
home = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
outputs = os.path.join(home, "output_excel")
output_citations = os.path.join(home, "output_citations")
make_dir_if_not_exists(output_citations)
citation_csv = os.path.join(home, "citation_csv")


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


def get_a_citation_data(html, publication_number, original_number, country_code):
    patent_citations = []
    non_patent_citations = []
    data_cited_by = []
    soup = BeautifulSoup(html, "html.parser")
    abstract_div = soup.find("div", class_="abstract style-scope patent-text")
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


def process_patent(index, total_data, row, country_code, existing_publication_numbers):
    with semaphore:
        if country_code == "NL":
            original_number = row["appln_nr_original"]
            publication_number = f"NL{int(row['appln_nr_original'])}"
        elif country_code == "US":
            original_number = row["patent_num"]
            publication_number = f"US{row['patent_num']}"
        else:
            return

        if publication_number in existing_publication_numbers:
            print(
                f"{index}/{total_data} {publication_number} already exists in the database"
            )
            return

        retries = 5
        while retries > 0:
            try:
                # Create a new SQLite connection and WebDriver instance within each worker process
                if country_code == "US":
                    db_path = f"patent_data_US_{from_index}_{to_index}.db"
                else:
                    db_path = "patent_data.db"
                conn = sqlite3.connect(db_path, timeout=10)  # Increase timeout
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT publication_number FROM patent_datas WHERE publication_number = ?",
                    (publication_number,),
                )
                result = cursor.fetchone()

                if result:
                    print(
                        f"{index}/{total_data} {publication_number} already exists in the database"
                    )
                    conn.close()
                    return

                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=chrome_options,
                )

                html, is_404 = get_citation_page_source(driver, publication_number)
                if is_404:
                    print(f"{index}/{total_data} {publication_number} is a 404 page")
                    driver.quit()
                    conn.close()
                    return

                patent_data, patent_citations, non_patent_citations, data_cited_by = (
                    get_a_citation_data(
                        html, publication_number, original_number, country_code
                    )
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

                # Close the WebDriver and SQLite connection
                driver.quit()
                conn.close()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    print(f"{index}/{total_data} Database is locked, retrying...")
                    retries -= 1
                    time.sleep(2)  # Wait before retrying
                else:
                    print(
                        f"{index}/{total_data} Error processing {publication_number}: {e}"
                    )
                    break
            except Exception as e:
                print(
                    f"{index}/{total_data} Error processing {publication_number}: {e}"
                )
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country_code", help="Country code of the patent")
    parser.add_argument(
        "--from_index", help="From index to get the data", type=int, default=130
    )
    parser.add_argument(
        "--to_index", help="To index to get the data", type=int, default=140
    )
    args = parser.parse_args()
    country_code = args.country_code
    from_index = args.from_index
    to_index = args.to_index

    # Load the data
    if country_code == "NL":
        path = os.path.abspath("source/NL_patent_raw.csv")
        data = pd.read_csv(path, sep=";")
    elif country_code == "US":
        path = os.path.abspath("source/US_match_patent.csv")
        data = pd.read_csv(path, sep=",")
    else:
        print("Please provide the correct country code")
        sys.exit(1)

    # Connect to the database and create tables
    if country_code == "US":
        conn = sqlite3.connect(f"patent_data_US_{from_index}_{to_index}.db")
    else:
        conn = sqlite3.connect("patent_data.db")
    create_tables(conn)

    # Filter data and remove duplicates and NaN values
    if country_code == "NL":
        data = data.drop_duplicates(subset=["appln_nr_original"])
        data = data.dropna(subset=["appln_nr_original"])
        data = data[data["appln_nr_original"] != ""]
        data["appln_nr_original"] = pd.to_numeric(
            data["appln_nr_original"], errors="coerce"
        )
        data = data.dropna(subset=["appln_nr_original"])
        data["appln_nr_original"] = data["appln_nr_original"].astype(int)
    elif country_code == "US":
        data = data.drop_duplicates(subset=["patent_num"])
        data = data.dropna(subset=["patent_num"])
        data = data[data["patent_num"] != ""]
        data["patent_num"] = pd.to_numeric(data["patent_num"], errors="coerce")
        data = data.dropna(subset=["patent_num"])
        data["patent_num"] = data["patent_num"].astype(int)
        data = data.sort_values(by="year", ascending=False)

    data = data.reset_index(drop=True)
    data = data.iloc[from_index:to_index]

    # Retrieve existing publication numbers from the database
    cursor = conn.cursor()
    cursor.execute("SELECT publication_number FROM patent_datas")
    existing_publication_numbers = [row[0] for row in cursor.fetchall()]

    # Use Manager to share the existing_publication_numbers list between processes
    manager = Manager()
    existing_publication_numbers = manager.list(existing_publication_numbers)

    # Close the initial database connection
    conn.close()

    with Pool(cpu_count()) as pool:
        pool.starmap(
            process_patent,
            [
                (index, data.shape[0], row, country_code, existing_publication_numbers)
                for index, row in data.iterrows()
            ],
        )
