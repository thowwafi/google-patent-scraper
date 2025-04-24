import os
import pandas as pd
import math

# Path to your original CSV file
path = os.path.abspath("source/data_sic_36_NA_copy.csv")
data = pd.read_csv(path, sep=",")
total_rows = len(data)
rows_per_file = 5000
num_files = math.ceil(total_rows / rows_per_file)
print(f"Total rows: {total_rows}")
print(f"Splitting into {num_files} files with {rows_per_file} rows each")
output_dir = os.path.join(os.path.dirname(path), "split_files")
os.makedirs(output_dir, exist_ok=True)
for i in range(num_files):
    start_idx = i * rows_per_file
    end_idx = min((i + 1) * rows_per_file, total_rows)
    chunk = data.iloc[start_idx:end_idx]
    output_filename = f"data_sic_36_NA_part_{i+1}.csv"
    output_path = os.path.join(output_dir, output_filename)
    chunk.to_csv(output_path, index=False)
    print(f"Saved {len(chunk)} rows to {output_filename}")
