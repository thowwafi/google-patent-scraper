from convert_sql_to_csv_new import main as convert_sql_to_csv
from zip_results_folder import zip_folder
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sql_to_zip.log"), logging.StreamHandler()],
)

logger = logging.getLogger("sql_to_zip")

# Check if the database file exists
database_file = "patent_data.db"
if not os.path.exists(database_file):
    logger.error(f"Database file {database_file} does not exist")

# Check if the output directory exists and zip file exists
output_dir = f"output_dir"
zip_file = f"US_patent_data.zip"
if os.path.exists(output_dir) and os.path.exists(zip_file):
    logger.info(f"{output_dir} and {zip_file} already exist")

convert_sql_to_csv()
zip_folder(f"US_patent_data", f"US_patent_data.zip")
logger.info(f"US_patent_data.zip has been created successfully")
