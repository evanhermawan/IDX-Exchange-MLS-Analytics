# -*- coding: utf-8 -*-

# Week 1 Data Aggregation Row Counts

# Listings Data Audit:
# - Total raw rows from monthly files: 866,140
# - Rows after concatenation: 866,140
# - Rows before residential filter: 866,140
# - Rows after residential filter: 550,542

# Sold Data Audit:
# - Total raw rows from monthly files: 615,725
# - Rows after concatenation: 615,725
# - Rows before residential filter: 615,725
# - Rows after residential filter: 414,063

import pandas as pd
import glob
import os

# Path to raw data directory
DATA_DIR = r"C:\GitHub\IDX-Exchange-MLS-Analytics\mls_raw_data" 

def aggregate_dataset(file_pattern, output_name):
    print("=========================================")
    print(f"Processing {output_name} datasets")
    print("=========================================")
    
    # Get all monthly csv files
    file_list = sorted(glob.glob(os.path.join(DATA_DIR, f"{file_pattern}*.csv")))
    
    if not file_list:
        print(f"Error: No files found matching '{file_pattern}' in {DATA_DIR}")
        return
    
    individual_row_counts = 0
    dfs = []
    
    # Loop through and read each file
    for file_path in file_list:
        df = pd.read_csv(file_path, low_memory=False)
        file_rows = len(df)
        individual_row_counts += file_rows
        print(f" Loaded {os.path.basename(file_path)}: {file_rows:,} rows")
        dfs.append(df)
        
    # Merge everything into one dataframe
    combined_df = pd.concat(dfs, ignore_index=True)
    concatenated_row_count = len(combined_df)
    
    print(f"\nSum of individual files: {individual_row_counts:,}")
    print(f"Rows after combining: {concatenated_row_count:,}")
    
    # Filter for residential only
    filtered_df = combined_df[combined_df['PropertyType'] == 'Residential']
    filtered_row_count = len(filtered_df)
    
    print(f"Rows before residential filter: {concatenated_row_count:,}")
    print(f"Rows after residential filter: {filtered_row_count:,}")
    
    # Save output file to root
    output_path = f"C:\\GitHub\\IDX-Exchange-MLS-Analytics\\{output_name}.csv"
    filtered_df.to_csv(output_path, index=False)
    print(f"\nSaved master file to: {output_path}\n\n")

if __name__ == "__main__":
    # Process both datasets
    aggregate_dataset("CRMLSListing", "listings")
    aggregate_dataset("CRMLSSold", "sold")