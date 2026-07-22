# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# Load clean dataset
df = pd.read_csv(r"C:\GitHub\IDX-Exchange-MLS-Analytics\sold_cleaned.csv", low_memory=False)

# Convert dates to datetime
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# --- 1. ENGINEERED MARKET METRICS ---
# Price ratios
list_col = 'ListPrice' if 'ListPrice' in df.columns else 'OriginalListPrice'
df['PriceRatio'] = df['ClosePrice'] / df[list_col].replace(0, np.nan)
df['CloseToOrigListRatio'] = df['ClosePrice'] / df['OriginalListPrice'].replace(0, np.nan)

# Price per square foot
df['PPSF'] = df['ClosePrice'] / df['LivingArea'].replace(0, np.nan)

# Time-series components
df['CloseYear'] = df['CloseDate'].dt.year
df['CloseMonth'] = df['CloseDate'].dt.month
df['YrMo'] = df['CloseDate'].dt.strftime('%Y-%m')

# Contract and escrow durations (in days)
df['ListingToContractDays'] = (df['PurchaseContractDate'] - df['ListingContractDate']).dt.days
df['ContractToCloseDays'] = (df['CloseDate'] - df['PurchaseContractDate']).dt.days

# --- 2. SCHOOL DISTRICT SPATIAL JOIN ---
try:
    import geopandas as gpd
    geojson_url = "https://data.ca.gov/dataset/7dfaf005-58eb-45db-93b1-7aff091b2172/resource/7dfaf005-58eb-45db-93b1-7aff091b2172/download/california_school_districts.geojson"
    districts = gpd.read_file(geojson_url)
    
    valid_geo = df.dropna(subset=['Latitude', 'Longitude'])
    valid_geo = valid_geo[(valid_geo['Latitude'] != 0) & (valid_geo['Longitude'] != 0)].copy()
    
    gdf = gpd.GeoDataFrame(
        valid_geo,
        geometry=gpd.points_from_xy(valid_geo.Longitude, valid_geo.Latitude),
        crs="EPSG:4326"
    )
    
    if districts.crs != "EPSG:4326":
        districts = districts.to_crs("EPSG:4326")
        
    joined = gpd.sjoin(gdf, districts, how="left", predicate="within")
    name_col = [c for c in joined.columns if 'district' in c.lower() or 'name' in c.lower()][0]
    df['SchoolDistrict'] = joined[name_col]
    print("School district join complete.")
except Exception as e:
    print(f"Skipped spatial join: {e}")
    df['SchoolDistrict'] = np.nan

# --- 3. SEGMENT SUMMARIES ---
# Property Types
summary_property = df.groupby(['PropertyType', 'PropertySubType']).agg(
    TotalSales=('ClosePrice', 'count'),
    AvgClosePrice=('ClosePrice', 'mean'),
    MedianPPSF=('PPSF', 'median'),
    AvgPriceRatio=('PriceRatio', 'mean'),
    AvgContractToClose=('ContractToCloseDays', 'mean')
).reset_index()

# Location (County & MLS Area)
summary_location = df.groupby(['CountyOrParish', 'MLSAreaMajor']).agg(
    TotalSales=('ClosePrice', 'count'),
    AvgClosePrice=('ClosePrice', 'mean'),
    MedianPPSF=('PPSF', 'median'),
    AvgContractToClose=('ContractToCloseDays', 'mean')
).reset_index()

# Brokerage Offices (Competitive Intelligence)
summary_offices = df.groupby(['ListOfficeName', 'BuyerOfficeName']).agg(
    TotalSales=('ClosePrice', 'count'),
    AvgClosePrice=('ClosePrice', 'mean'),
    AvgPriceRatio=('PriceRatio', 'mean')
).reset_index().sort_values(by='TotalSales', ascending=False)

# --- 4. PRINT DELIVERABLE SAMPLES ---
print("\n=== SAMPLE ENGINEERED METRICS ===")
cols_to_show = ['ClosePrice', 'PriceRatio', 'CloseToOrigListRatio', 'PPSF', 'YrMo', 'ListingToContractDays', 'ContractToCloseDays']
print(df[cols_to_show].head(10).to_string(index=False))

print("\n=== SUMMARY BY PROPERTY TYPE ===")
print(summary_property.head(10).to_string(index=False))

print("\n=== SUMMARY BY LOCATION ===")
print(summary_location.head(10).to_string(index=False))

print("\n=== SUMMARY BY BROKERAGE OFFICE ===")
print(summary_offices.head(10).to_string(index=False))

# Export enriched CSV
output_path = r"C:\GitHub\IDX-Exchange-MLS-Analytics\sold_enriched.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved enriched dataset to {output_path}")
