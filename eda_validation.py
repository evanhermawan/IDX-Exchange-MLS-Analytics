# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# setup paths
base_dir = r"C:\GitHub\IDX-Exchange-MLS-Analytics"
data_dir = os.path.join(base_dir, "mls_raw_data")

# 1. load raw data & check initial share
print("loading raw data files...")
sold_files = sorted(glob.glob(os.path.join(data_dir, "CRMLSSold*.csv")))
if not sold_files:
    print("error: no raw sold files found.")
    exit()

df_list = [pd.read_csv(f, low_memory=False) for f in sold_files]
sold = pd.concat(df_list, ignore_index=True)

print("\n--- property type share ---")
print(sold['PropertyType'].value_counts(normalize=True).round(4) * 100)

# filter for residential
sold = sold[sold['PropertyType'] == 'Residential'].copy()
print(f"filtered row count: {len(sold):,}")

# 2. missing value analysis
null_counts = sold.isnull().sum()
null_pct = (null_counts / len(sold)) * 100
null_report = pd.DataFrame({'count': null_counts, 'percent': null_pct})

# flag anything over 90% missing
high_missing = null_report[null_report['percent'] > 90]
print("\n--- columns with >90% missing data ---")
print(high_missing.round(2) if not high_missing.empty else "none")

# 3. numeric distributions & basic analytics
num_cols = [
    'ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea', 
    'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger', 
    'DaysOnMarket', 'YearBuilt'
]
for col in num_cols:
    if col in sold.columns:
        sold[col] = pd.to_numeric(sold[col], errors='coerce')

print("\n--- numeric field stats ---")
print(sold[num_cols].describe(percentiles=[.25, .50, .75, .90]).round(2))

# quick check on suggested handbook questions
print("\n--- handbook quick insights ---")
print(f"median price: ${sold['ClosePrice'].median():,.2f}")
print(f"average price: ${sold['ClosePrice'].mean():,.2f}")
print(f"days on market (median): {sold['DaysOnMarket'].median()} days")

above_list = (sold['ClosePrice'] > sold['ListPrice']).mean() * 100
print(f"homes sold above list price: {above_list:.2f}%")

# save required distribution plots
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.figure()
sold['ClosePrice'].hist(bins=50)
plt.title('residential close price distribution')
plt.savefig(os.path.join(base_dir, 'close_price_hist.png'))

plt.figure()
sold.boxplot(column=['DaysOnMarket'])
plt.title('days on market boxplot')
plt.savefig(os.path.join(base_dir, 'days_on_market_box.png'))
plt.close('all')

# save clean base filtered data
sold.to_csv(os.path.join(base_dir, "sold_filtered.csv"), index=False)


# 4. pull fred mortgage data & resample to monthly
print("\n--- starting fred macroeconomic integration ---")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['rate_30yr_fixed'] = pd.to_numeric(mortgage['rate_30yr_fixed'], errors='coerce')

# change weekly to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index()

# 5. create matching keys and left merge
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

listings_path = os.path.join(base_dir, "listings.csv")
if os.path.exists(listings_path):
    listings = pd.read_csv(listings_path, low_memory=False)
    listings['year_month'] = pd.to_datetime(listings['ListingContractDate']).dt.to_period('M')
    
    # merge economic data
    sold_enriched = sold.merge(mortgage_monthly, on='year_month', how='left')
    listings_enriched = listings.merge(mortgage_monthly, on='year_month', how='left')
    
    # validation check for nulls
    print("\n--- validation check (null counts should be 0) ---")
    print("sold data unmapped rows:", sold_enriched['rate_30yr_fixed'].isnull().sum())
    print("listings data unmapped rows:", listings_enriched['rate_30yr_fixed'].isnull().sum())
    
    # save enriched sets
    sold_enriched.to_csv(os.path.join(base_dir, "sold_enriched.csv"), index=False)
    listings_enriched.to_csv(os.path.join(base_dir, "listings_enriched.csv"), index=False)
    print("\nprocessing complete. all files updated.")
else:
    print(f"\nerror: listings.csv missing at {listings_path}. skipping listings merge.")