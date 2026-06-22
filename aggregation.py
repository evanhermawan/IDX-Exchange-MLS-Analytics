# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 10:50:31 2026

@author: evanb
"""
# =====================================================================
# WEEK 1 DELIVERABLE: MONTHLY DATASET AGGREGATION ROW COUNT AUDIT
# 
# 📊 LISTINGS DATASET AUDIT:
#   - Sum of individual monthly files: 866,140 rows
#   - Master dataframe AFTER concatenation: 866,140 rows
#   - Rows BEFORE Residential filter: 866,140 rows
#   - Rows AFTER Residential filter: 550,542 rows
# 
# 📊 SOLD DATASETS AUDIT:
#   - Sum of individual monthly files: 615,725 rows
#   - Master dataframe AFTER concatenation: 615,725 rows
#   - Rows BEFORE Residential filter: 615,725 rows
#   - Rows AFTER Residential filter: 414,063 rows
# =====================================================================

import pandas as pd
import glob
import os

# Define the local path where your files are saved
DATA_DIR = r"C:\GitHub\IDX-Exchange-MLS-Analytics\mls_raw_data" 

def aggregate_dataset(file_pattern, output_name):
    print(f"=========================================")
    print(f"PROCESSING: {output_name.upper()} DATASETS")
    print(f"=========================================")
    
    # 1. Find all matching monthly files
    file_list = sorted(glob.glob(os.path.join(DATA_DIR, f"{file_pattern}*.csv")))
    
    if not file_list:
        print(f"❌ Error: No files found matching pattern '{file_pattern}' in {DATA_DIR}")
        return
    
    individual_row_counts = 0
    dfs = []
    
    # Read each file individually to log individual row counts
    for file_path in file_list:
        df = pd.read_csv(file_path, low_memory=False)
        file_rows = len(df)
        individual_row_counts += file_rows
        print(f" Loaded {os.path.basename(file_path)}: {file_rows:,} rows")
        dfs.append(df)
        
    # 2. Concatenate all datasets into one
    combined_df = pd.concat(dfs, ignore_index=True)
    concatenated_row_count = len(combined_df)
    
    # [HANDBOOK REQUIREMENT] Log counts before and after concatenation
    print(f"\n📈 [COUNT AUDIT] Sum of individual monthly files: {individual_row_counts:,}")
    print(f"📈 [COUNT AUDIT] Master dataframe AFTER concatenation: {concatenated_row_count:,}")
    
    # 3. Apply Property Type filter
    # [HANDBOOK REQUIREMENT] Filter to PropertyType == 'Residential' only
    filtered_df = combined_df[combined_df['PropertyType'] == 'Residential']
    filtered_row_count = len(filtered_df)
    
    # [HANDBOOK REQUIREMENT] Log counts before and after the Residential filter
    print(f"📊 [COUNT AUDIT] Rows BEFORE Residential filter: {concatenated_row_count:,}")
    print(f"📊 [COUNT AUDIT] Rows AFTER Residential filter: {filtered_row_count:,}")
    
    # 4. Save to the root directory
    output_path = f"C:\\GitHub\\IDX-Exchange-MLS-Analytics\\{output_name}.csv"
    filtered_df.to_csv(output_path, index=False)
    print(f"\n✅ Success! Saved clean master file to: {output_path}\n\n")

if __name__ == "__main__":
    # Run the processing pipeline for both sets of data
    aggregate_dataset("CRMLSListing", "listings")
    aggregate_dataset("CRMLSSold", "sold")