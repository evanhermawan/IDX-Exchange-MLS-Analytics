# -*- coding: utf-8 -*-

# Week 1 Listings Data Audit:
# - Sum of individual files: 866,140
# - Rows after combining: 866,140
# - Rows before residential filter: 866,140
# - Rows after residential filter: 550,542

import pandas as pd
import glob
import os

# path to raw data
DATA_DIR = r"C:\GitHub\IDX-Exchange-MLS-Analytics\mls_raw_data" 

print("Processing listings datasets...")

# find all monthly listing files
file_list = sorted(glob.glob(os.path.join(DATA_DIR, "CRMLSListing*.csv")))

if not file_list:
    print("Error: No listing files found.")
    exit()

individual_row_counts = 0
dfs = []

# loop and read each file
for file_path in file_list:
    df = pd.read_csv(file_path, low_memory=False)
    file_rows = len(df)
    individual_row_counts += file_rows
    print(f"Loaded {os.path.basename(file_path)}: {file_rows:,} rows")
    dfs.append(df)

# combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)
concatenated_row_count = len(combined_df)

print(f"\nSum of individual files: {individual_row_counts:,}")
print(f"Rows after combining: {concatenated_row_count:,}")

# filter for residential properties only
filtered_df = combined_df[combined_df['PropertyType'] == 'Residential']
filtered_row_count = len(filtered_df)

print(f"Rows before residential filter: {concatenated_row_count:,}")
print(f"Rows after residential filter: {filtered_row_count:,}")

# save to root folder
output_path = r"C:\GitHub\IDX-Exchange-MLS-Analytics\listings.csv"
filtered_df.to_csv(output_path, index=False)
print(f"\nSaved master listings file to: {output_path}")