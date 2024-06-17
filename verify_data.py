import sqlite3
import csv
import os
import argparse

def count_table_rows(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def count_csv_rows(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        row_count = sum(1 for row in reader)
    return row_count - 1  # Subtract 1 for the header row

def verify_data(db_path, csv_dir):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        csv_file = os.path.join(csv_dir, f"{table_name}.csv")
        if not os.path.exists(csv_file):
            print(f"CSV file for table {table_name} does not exist.")
            continue
        
        db_row_count = count_table_rows(cursor, table_name)
        csv_row_count = count_csv_rows(csv_file)
        
        print(f"Table: {table_name}, DB Rows: {db_row_count}, CSV Rows: {csv_row_count}")
        if db_row_count != csv_row_count:
            print(f"Row count mismatch for table {table_name}")
        
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify that CSV exports match the SQLite database.")
    parser.add_argument("db_path", type=str, help="Path to the SQLite database file")
    parser.add_argument("csv_dir", type=str, help="Directory containing the CSV files")
    
    args = parser.parse_args()

    verify_data(args.db_path, args.csv_dir)
