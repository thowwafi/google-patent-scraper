from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
import os
from utils.utils import make_dir_if_not_exists


home = os.getcwd()
outputs = os.path.join(home, 'output_excel')
output_citations = os.path.join(home, 'output_citations')
make_dir_if_not_exists(output_citations)
citation_csv = os.path.join(home, 'citation_csv')


def get_data_tables(soup, number, div_id):
    h3_pc = soup.find('h3', id=div_id)
    if not h3_pc:
        return []
    pc_table = h3_pc.find_next('div', class_='responsive-table')
    data = []
    for tr in pc_table.find_all('div', class_='tr'):
        if tr.text.strip().startswith("Publication") or tr.text.strip().startswith("Family"):
            continue
        citation_number = tr.find_all("span", class_="td")[0].text.replace(" ", "").replace("\n", "")
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
            "cited_by": cited_by
        }
        data.append(citation)
    return data

def get_citations(df):
    """
    Returns a list of citations in the given file.
    """
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    patent_datas = []
    patent_citations = []
    non_patent_citations = []
    data_cited_by = []

    timeouts_data = []
    for index, row in df.iterrows():
        # if index > 100:
        #     continue
        print(f"{index}/{df.shape[0]}")
        number = f"NL{int(row['appln_nr_original'])}"
        url = f"https://patents.google.com/patent/{number}/en?oq={number}"
        try:
            driver.get(url)
        except TimeoutException:
            print('timeout')
            timeouts_data.append(number)
            continue
        except WebDriverException:
            print('webdriver')
            timeouts_data.append(number)
            continue
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "footer"))
            )
        except TimeoutException:
            print('Loading took too much time!')
            continue
        except WebDriverException:
            print('webdriver')
            timeouts_data.append(number)
            continue

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        abstract_div = soup.find('div', class_='abstract style-scope patent-text')
        total_cited_by = 0
        total_patent_citations = 0

        patent_title = soup.find('h1', id='title').text.strip()
        cited_by_text = soup.find('a', href='#citedBy').text
        if cited_by_text:
            total_cited_by = int(cited_by_text.split('(')[1].split(')')[0])
        patent_citations_text = soup.find('a', href='#patentCitations').text
        if patent_citations_text:
            total_patent_citations = int(patent_citations_text.split('(')[1].split(')')[0])

        if not abstract_div:
            abstract = ""
        else:
            abstract = abstract_div.text.strip().replace(";", " ").replace("\n", " ").replace("\t", " ")

        status_div = soup.find('div', class_='legal-status style-scope application-timeline', string="Status")
        if not status_div:
            status = ""
        else:
            status = status_div.find_next('span', class_='title-text style-scope application-timeline').text.strip()

        claim_id = soup.find('section', id='claims')
        claim_text = ""
        for claim in claim_id.find_all('claim'):
            parent_span = claim.find(class_="notranslate style-scope patent-text")
            if parent_span:
                english_text = ''.join([str(child) for child in parent_span.children if isinstance(child, str)])
                claim_text += english_text
                claim_text.strip().replace(";", " ").replace("\n", " ").replace("\t", " ")
        total_claims = len(claim_id.find_all('claim'))

        patent_data = {
            "publication_number": number,
            "appln_nr_original": row['appln_nr_original'],
            "patent_title": patent_title,
            "abstract": abstract,
            "description": "",
            "claims": claim_text,
            "total_number_of_claims": total_claims,
            "total_cited_by": total_cited_by,
            "total_patent_citations": total_patent_citations,
            "status": status,
        }
        patent_datas.append(patent_data)

        if not soup.find('h3', id='patentCitations'):
            citation = {
                "publication_number": number,
                "patent_citation": 0,
                "publication_date": 0,
                "assignee": 0,
                "title": 0
            }
            patent_citations.append(citation)
        else:
            citations = get_data_tables(soup, number, 'patentCitations')
            patent_citations.extend(iter(citations))

        if not soup.find('h3', id='citedBy'):
            citation = {
                "publication_number": number,
                "patent_citation": 0,
                "publication_date": 0,
                "assignee": 0,
                "title": 0
            }
            data_cited_by.append(citation)
        else:
            cited_bys = get_data_tables(soup, number, 'citedBy')
            data_cited_by.extend(iter(cited_bys))

        if not soup.find('h3', id='nplCitations'):
            citation = {
                "publication_number": number,
                "patent_citation": 0,
                "publication_date": 0,
                "assignee": 0,
                "title": 0
            }
            non_patent_citations.append(citation)
        else:
            h3_pc = soup.find('h3', id='nplCitations')
            pc_table = h3_pc.find_next('div', class_='responsive-table')
            for tr in pc_table.find_all('div', class_='tr')[1:]:
                citation = {
                    "publication_number": number,
                    "patent_citation": 0,
                    "publication_date": 0,
                    "assignee": 0,
                    "title": tr.text.replace('*', '').strip()
                }
                non_patent_citations.append(citation)
    driver.quit()

    df_patent_citations = pd.DataFrame(patent_citations)
    df_non_patent_citations = pd.DataFrame(non_patent_citations)
    df_data_cited_by = pd.DataFrame(data_cited_by)
    df_patent_data = pd.DataFrame(patent_datas)
    output_name = "all_patents"
    # output_file = os.path.join(output_citations, f"{output_name}_citations.xlsx")
    # writer = pd.ExcelWriter(output_file, engine='openpyxl')
    # df_patent_citations.to_excel(writer, sheet_name='PatentCitations', index=False)
    # df_non_patent_citations.to_excel(writer, sheet_name='NonPatentCitations', index=False)
    # df_data_cited_by.to_excel(writer, sheet_name='CitedBy', index=False)
    # df_patent_data.to_excel(writer, sheet_name='PatentData', index=False)
    # writer.save()
    # writer.close()

    if not os.path.exists(citation_csv):
        os.makedirs(citation_csv)
    year_folder = os.path.join(citation_csv, output_name)
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)
    df_patent_citations.to_csv(os.path.join(year_folder, f"{output_name}_PatentCitations.csv"), index=False, sep=';')
    df_non_patent_citations.to_csv(os.path.join(year_folder, f"{output_name}_NonPatentCitations.csv"), index=False, sep=';')
    df_data_cited_by.to_csv(os.path.join(year_folder, f"{output_name}_CitedBy.csv"), index=False, sep=';')
    df_patent_data.to_csv(os.path.join(year_folder, f"{output_name}_PatentData.csv"), index=False, sep=';')


if __name__ == '__main__':
    # Load the data
    data = pd.read_csv('source/NL_patent_raw.csv', sep=';')

    # Print the data
    print(data.head())

    get_citations(data.head())

