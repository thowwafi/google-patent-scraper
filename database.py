
def create_tables(conn):
    with conn:
        # publication_number;original_number;patent_title;abstract;description;claims;total_number_of_claims;total_cited_by;total_patent_citations;status
        conn.execute('''CREATE TABLE IF NOT EXISTS patent_datas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT,
            original_number TEXT,
            patent_title TEXT,
            abstract TEXT,
            description TEXT,
            claims TEXT,
            total_number_of_claims TEXT,
            total_cited_by TEXT,
            total_patent_citations TEXT,
            status TEXT
        )''')

        # publication_number;patent_citation;publication_date;assignee;title;cited_by
        conn.execute('''CREATE TABLE IF NOT EXISTS patent_citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT,
            patent_citation TEXT,
            publication_date TEXT,
            assignee TEXT,
            title TEXT,
            cited_by TEXT
        )''')

        # publication_number;patent_citation;publication_date;assignee;title
        conn.execute('''CREATE TABLE IF NOT EXISTS non_patent_citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT,
            patent_citation TEXT,
            publication_date TEXT,
            assignee TEXT,
            title TEXT
        )''')

        # publication_number;patent_citation;publication_date;assignee;title;cited_by
        conn.execute('''CREATE TABLE IF NOT EXISTS data_cited_by (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT,
            patent_citation TEXT,
            publication_date TEXT,
            assignee TEXT,
            title TEXT,
            cited_by TEXT
        )''')

def insert_to_patent_datas(conn, patent_data):
    with conn:
        conn.execute('''INSERT INTO patent_datas (
            publication_number,
            original_number,
            patent_title,
            abstract,
            description,
            claims,
            total_number_of_claims,
            total_cited_by,
            total_patent_citations,
            status
        ) VALUES (
            :publication_number,
            :original_number,
            :patent_title,
            :abstract,
            :description,
            :claims,
            :total_number_of_claims,
            :total_cited_by,
            :total_patent_citations,
            :status
        )''', 
            patent_data
        )

def insert_to_patent_citations(conn, patent_citation):
    with conn:
        conn.execute('''INSERT INTO patent_citations (
            publication_number,
            patent_citation,
            publication_date,
            assignee,
            title,
            cited_by
        ) VALUES (
            :publication_number,
            :patent_citation,
            :publication_date,
            :assignee,
            :title,
            :cited_by
        )''',
            patent_citation
        )

def insert_to_non_patent_citations(conn, non_patent_citation):
    with conn:
        conn.execute('''INSERT INTO non_patent_citations (
            publication_number,
            patent_citation,
            publication_date,
            assignee,
            title
        ) VALUES (
            :publication_number,
            :patent_citation,
            :publication_date,
            :assignee,
            :title
        )''',
            non_patent_citation
        )

def insert_to_data_cited_by(conn, data_cited_by):
    with conn:
        conn.execute('''INSERT INTO data_cited_by (
            publication_number,
            patent_citation,
            publication_date,
            assignee,
            title,
            cited_by
        ) VALUES (
            :publication_number,
            :patent_citation,
            :publication_date,
            :assignee,
            :title,
            :cited_by
        )''',
            data_cited_by
        )
