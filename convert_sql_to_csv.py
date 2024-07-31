import argparse
import sqlite3
import pandas as pd
import os
from zip_results_folder import zip_folder


def export_table_to_csv(conn, table_name, csv_file_name):
    # Read the table into a DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    # Export the DataFrame to a CSV file
    df.to_csv(csv_file_name, index=False)

def main(from_index, to_index):
    # Connect to the SQLite database
    database_file = f'patent_data_US_{from_index}_{to_index}.db'
    print("database_file:", database_file)
    # check if the database file exists
    if not os.path.exists(database_file):
        print(f"Database file {database_file} does not exist")
        return
    try:
        conn = sqlite3.connect(database_file)
    except sqlite3.OperationalError:
        print(f"Database file {database_file} does not exist")
        return
    
    # create output directory
    output_dir = f'US_{from_index}_{to_index}'
    try:
        os.makedirs(output_dir)
        print("output_dir:", output_dir)
    except FileExistsError:
        pass
    
    try:
        # List of tables and corresponding CSV file names
        tables = [
            ('patent_datas', f'{output_dir}/patent_datas.csv'),
            ('patent_citations', f'{output_dir}/patent_citations.csv'),
            ('non_patent_citations', f'{output_dir}/non_patent_citations.csv'),
            ('data_cited_by', f'{output_dir}/data_cited_by.csv')
        ]
        
        # Export each table to CSV
        for table_name, csv_file_name in tables:
            export_table_to_csv(conn, table_name, csv_file_name)
            print(f"Exported {table_name} to {csv_file_name}")
    
    finally:
        # Close the database connection
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from_index", help="From index to get the data", type=int,
    )
    parser.add_argument(
        "--to_index", help="To index to get the data", type=int,
    )
    args = parser.parse_args()
    from_index = args.from_index
    to_index = args.to_index

    main(from_index, to_index)
    zip_folder(f'US_{from_index}_{to_index}', f'US_{from_index}_{to_index}.zip')


# example usage:
# python convert_sql_to_csv.py --from_index 0 --to_index 100
