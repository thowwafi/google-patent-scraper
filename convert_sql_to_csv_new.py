import argparse
import sqlite3
import pandas as pd
import os
import logging
from zip_results_folder import zip_folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("convert_sql_to_csv.log"), logging.StreamHandler()],
)

logger = logging.getLogger("convert_sql_to_csv")


def export_table_to_csv(conn, table_name, csv_file_name):
    # Read the table into a DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    # Export the DataFrame to a CSV file
    df.to_csv(csv_file_name, index=False)


def main():
    # Connect to the SQLite database
    database_file = f"patent_data.db"
    logger.info(f"database_file: {database_file}")
    # check if the database file exists
    if not os.path.exists(database_file):
        logger.error(f"Database file {database_file} does not exist")
        return
    try:
        conn = sqlite3.connect(database_file)
    except sqlite3.OperationalError:
        logger.error(f"Database file {database_file} does not exist")
        return

    # create output directory
    output_dir = f"output/US_patent_data"
    try:
        os.makedirs(output_dir)
        logger.info(f"output_dir: {output_dir}")
    except FileExistsError:
        pass

    try:
        # List of tables and corresponding CSV file names
        tables = [
            # ("patent_datas", f"{output_dir}/patent_datas.csv"),
            # ("patent_citations", f"{output_dir}/patent_citations.csv"),
            # ("non_patent_citations", f"{output_dir}/non_patent_citations.csv"),
            ("data_cited_by", f"{output_dir}/data_cited_by.csv"),
        ]

        # Export each table to CSV
        for table_name, csv_file_name in tables:
            try:

                export_table_to_csv(conn, table_name, csv_file_name)
            except sqlite3.OperationalError as e:
                logger.error(f"Error exporting {table_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"An error occurred while exporting {table_name}: {e}")
                continue
            # Log the successful export
            logger.info(f"Exported {table_name} to {csv_file_name}")

    except Exception as e:
        logger.error(f"An error occurred while exporting tables: {e}")
        return
    finally:
        # Close the database connection
        conn.close()


if __name__ == "__main__":
    main()
    zip_folder(f"US_patent_data", f"US_patent_data.zip")
