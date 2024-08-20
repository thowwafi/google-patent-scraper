from convert_sql_to_csv import main as convert_sql_to_csv
from zip_results_folder import zip_folder
import os
from pprint import pprint


index_list = []
for i in range(121, 236):
    index_list.append((i * 10000, (i + 1) * 10000))

pprint(index_list)

for index in index_list:
    # check if the database file exists
    database_file = f"patent_data_US_{index[0]}_{index[1]}.db"
    if not os.path.exists(database_file):
        print(f"Database file {database_file} does not exist")
        continue
    # check if the output directory exists and zip file exists
    output_dir = f"US_{index[0]}_{index[1]}"
    zip_file = f"US_{index[0]}_{index[1]}.zip"
    if os.path.exists(output_dir) and os.path.exists(zip_file):
        print(f"{output_dir} and {zip_file} already exist")
        continue
    convert_sql_to_csv(index[0], index[1])
    zip_folder(f"US_{index[0]}_{index[1]}", f"US_{index[0]}_{index[1]}.zip")
    print(f"US_{index[0]}_{index[1]}.zip has been created successfully")
