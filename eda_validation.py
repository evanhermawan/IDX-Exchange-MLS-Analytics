# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os

# paths
data_dir = r"C:\GitHub\IDX-Exchange-MLS-Analytics\mls_raw_data"
out_path = r"C:\GitHub\IDX-Exchange-MLS-Analytics\sold_filtered.csv"

# read raw files
files = sorted(glob.glob(os.path.join(data_dir, "CRMLSSold*.csv")))
if not files:
    print("no files found")
    exit()

print("reading files...")
all_dfs = []
for f in files:
    all_dfs.append(pd.read_csv(f, low_memory=False))
df = pd.concat(all_dfs, ignore_index=True)

# check types before the filter
print("\nunique property types:")
print(df['PropertyType'].unique())

print("\nproperty type share:")
print(df['PropertyType'].value_counts(normalize=True).round(4) * 100)

# filter for residential
print("\nfiltering data...")
df_res = df[df['PropertyType'] == 'Residential'].copy()
print(f"filtered rows: {len(df_res):,}")

# full null count summary table
null_counts = df_res.isnull().sum()
null_pct = (null_counts / len(df_res)) * 100

null_table = pd.DataFrame({
    'null_count': null_counts,
    'null_percent': null_pct
})

pd.set_option('display.max_rows', None)
print("\nall null counts:")
print(null_table.round(2))

# flag cols over 90% missing
high_missing = null_table[null_table['null_percent'] > 90]
print("\ncolumns with >90% missing values:")
if high_missing.empty:
    print("none")
else:
    print(high_missing.round(2))

# numeric distribution summaries
num_cols = [
    'ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea', 
    'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger', 
    'DaysOnMarket', 'YearBuilt'
]

for c in num_cols:
    if c in df_res.columns:
        df_res[c] = pd.to_numeric(df_res[c], errors='coerce')

print("\nnumeric distribution summary:")
stats = df_res[num_cols].describe(percentiles=[.25, .50, .75, .90])
print(stats.round(2))

# save out new file
df_res.to_csv(out_path, index=False)
print(f"\nsaved filtered file to: {out_path}")