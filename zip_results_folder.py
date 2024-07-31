import os
import zipfile
import argparse

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zip a folder and its contents")
    parser.add_argument("folder_to_zip", type=str, help="The path of the folder to zip")
    parser.add_argument("zip_file_name", type=str, help="The desired path of the output zip file")

    args = parser.parse_args()

    folder_to_zip = args.folder_to_zip
    zip_file_name = args.zip_file_name
    
    # Check if the folder exists
    if os.path.isdir(folder_to_zip):
        zip_folder(folder_to_zip, zip_file_name)
        print(f"{folder_to_zip} has been zipped successfully into {zip_file_name}")
    else:
        print(f"The folder '{folder_to_zip}' does not exist")


# example usage:
# python zip_results_folder.py US_0_100 US_0_100.zip
