# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

# project path setup
base_dir = r"C:\GitHub\IDX-Exchange-MLS-Analytics"
input_path = os.path.join(base_dir, "sold_enriched.csv")

if not os.path.exists(input_path):
    print(f"error: {input_path} not found. please run the weeks 2-3 script first.")
    exit()

# load the enriched dataset
df = pd.read_csv(input_path, low_memory=False)
initial_rows = len(df)
initial_cols = df.shape[1]

print("--- data type validation before cleaning ---")
print(df[['CloseDate', 'Latitude', 'Longitude', 'ClosePrice']].dtypes)

# datetime conversion for all requested timeline fields
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# date consistency checks and boolean flagging
df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']

if 'PurchaseContractDate' in df.columns:
    df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
    df['negative_timeline_flag'] = (df['ListingContractDate'] > df['PurchaseContractDate']) | \
                                   (df['PurchaseContractDate'] > df['CloseDate'])
else:
    df['purchase_after_close_flag'] = False
    df['negative_timeline_flag'] = df['listing_after_close_flag']

print("\n--- date consistency flag counts ---")
print(f"listing date occurs after close date:  {df['listing_after_close_flag'].sum():,}")
print(f"purchase date occurs after close date: {df['purchase_after_close_flag'].sum():,}")
print(f"overall timeline sequence violations:  {df['negative_timeline_flag'].sum():,}")

# geographic data quality screening
df['geo_missing_flag'] = df['Latitude'].isnull() | df['Longitude'].isnull()
df['geo_zero_flag'] = (df['Latitude'] == 0.0) | (df['Longitude'] == 0.0)
df['geo_positive_lon_flag'] = df['Longitude'] > 0

# check coordinates falling completely outside california bounding box limits
df['geo_implausible_flag'] = ~df['Latitude'].between(32.5, 42.5) | ~df['Longitude'].between(-124.5, -114.0)
df.loc[df['geo_missing_flag'] | df['geo_zero_flag'], 'geo_implausible_flag'] = False

print("\n--- geographic data quality summary ---")
print(f"missing coordinate entries:      {df['geo_missing_flag'].sum():,}")
print(f"zero (sentinel null) placement:  {df['geo_zero_flag'].sum():,}")
print(f"positive longitude text errors:  {df['geo_positive_lon_flag'].sum():,}")
print(f"out-of-state/off-map coordinates: {df['geo_implausible_flag'].sum():,}")

# enforce proper numeric typing across target metrics
num_cols = ['ClosePrice', 'LivingArea', 'DaysOnMarket', 'BedroomsTotal', 'BathroomsTotalInteger']
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# remove unnecessary or redundant columns (columns with >90% missing values)
null_pct = (df.isnull().sum() / len(df)) * 100
high_missing_cols = null_pct[null_pct > 90].index.tolist()
df = df.drop(columns=high_missing_cols)

# construct operational filtering mask to drop invalid numeric records
valid_numeric_mask = (
    (df['ClosePrice'] > 0) & 
    (df['LivingArea'] > 0) & 
    (df['DaysOnMarket'] >= 0) & 
    (df['BedroomsTotal'] >= 0) & 
    (df['BathroomsTotalInteger'] >= 0)
)

df_cleaned = df[valid_numeric_mask].copy()
final_rows = len(df_cleaned)
final_cols = df_cleaned.shape[1]

print("\n--- data shape transformation summary ---")
print(f"initial dataset shape:  {initial_rows:,} rows, {initial_cols} columns")
print(f"cleaned dataset shape:  {final_rows:,} rows, {final_cols} columns")
print(f"redundant columns dropped: {len(high_missing_cols)}")
print(f"invalid rows filtered out: {initial_rows - final_rows:,}")

# final confirmation export
output_path = os.path.join(base_dir, "sold_cleaned.csv")
df_cleaned.to_csv(output_path, index=False)
print(f"\nsuccess: analysis-ready dataset saved to {output_path}")