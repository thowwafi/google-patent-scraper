import sqlite3
import pandas as pd

def export_table_to_csv(conn, table_name, csv_file_name):
    # Read the table into a DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    # Export the DataFrame to a CSV file
    df.to_csv(csv_file_name, index=False)

def main():
    # Connect to the SQLite database
    database_file = 'patent_data.db'  # Replace with your actual database file
    conn = sqlite3.connect(database_file)
    
    try:
        # List of tables and corresponding CSV file names
        tables = [
            ('patent_datas', 'NL/patent_datas.csv'),
            ('patent_citations', 'NL/patent_citations.csv'),
            ('non_patent_citations', 'NL/non_patent_citations.csv'),
            ('data_cited_by', 'NL/data_cited_by.csv')
        ]
        
        # Export each table to CSV
        for table_name, csv_file_name in tables:
            export_table_to_csv(conn, table_name, csv_file_name)
            print(f"Exported {table_name} to {csv_file_name}")
    
    finally:
        # Close the database connection
        conn.close()

if __name__ == '__main__':
    main()
