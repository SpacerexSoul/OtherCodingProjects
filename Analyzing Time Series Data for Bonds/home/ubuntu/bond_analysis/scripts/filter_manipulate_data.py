import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def load_time_series_data():
    """Load the time series data"""
    print("Loading time series data...")
    
    # Load time series data
    corp_bonds_ts = pd.read_csv('../data/time_series/corp_bonds_ts.csv', parse_dates=['Date'], index_col='Date')
    gov_bonds_ts = pd.read_csv('../data/time_series/gov_bonds_ts.csv', parse_dates=['Date'], index_col='Date')
    corp_yield_pivot = pd.read_csv('../data/time_series/corp_yield_pivot.csv', parse_dates=['Date'], index_col='Date')
    gov_yield_pivot = pd.read_csv('../data/time_series/gov_yield_pivot.csv', parse_dates=['Date'], index_col='Date')
    
    print(f"Loaded time series data successfully")
    
    return {
        'corp_bonds_ts': corp_bonds_ts,
        'gov_bonds_ts': gov_bonds_ts,
        'corp_yield_pivot': corp_yield_pivot,
        'gov_yield_pivot': gov_yield_pivot
    }

def filter_by_date_range(time_series_data):
    """Filter data by specific date ranges"""
    print("\nFiltering data by date ranges...")
    
    # Filter corporate bonds for 2020 Q1
    q1_2020_start = '2020-01-01'
    q1_2020_end = '2020-03-31'
    corp_q1_2020 = time_series_data['corp_bonds_ts'].loc[q1_2020_start:q1_2020_end]
    
    # Filter government bonds for 2020 Q1
    gov_q1_2020 = time_series_data['gov_bonds_ts'].loc[q1_2020_start:q1_2020_end]
    
    # Filter corporate bonds for 2021 Q3
    q3_2021_start = '2021-07-01'
    q3_2021_end = '2021-09-30'
    corp_q3_2021 = time_series_data['corp_bonds_ts'].loc[q3_2021_start:q3_2021_end]
    
    # Filter government bonds for 2021 Q3
    gov_q3_2021 = time_series_data['gov_bonds_ts'].loc[q3_2021_start:q3_2021_end]
    
    print(f"Corporate bonds Q1 2020: {corp_q1_2020.shape[0]} records")
    print(f"Government bonds Q1 2020: {gov_q1_2020.shape[0]} records")
    print(f"Corporate bonds Q3 2021: {corp_q3_2021.shape[0]} records")
    print(f"Government bonds Q3 2021: {gov_q3_2021.shape[0]} records")
    
    return {
        'corp_q1_2020': corp_q1_2020,
        'gov_q1_2020': gov_q1_2020,
        'corp_q3_2021': corp_q3_2021,
        'gov_q3_2021': gov_q3_2021
    }

def filter_by_conditions(time_series_data):
    """Filter data based on specific conditions"""
    print("\nFiltering data based on conditions...")
    
    # Filter corporate bonds with yield > 4.0
    high_yield_corp = time_series_data['corp_bonds_ts'][time_series_data['corp_bonds_ts']['Yield'] > 4.0]
    
    # Filter government bonds with yield > 2.0
    high_yield_gov = time_series_data['gov_bonds_ts'][time_series_data['gov_bonds_ts']['Yield'] > 2.0]
    
    # Filter corporate bonds with volume > 7000
    high_volume_corp = time_series_data['corp_bonds_ts'][time_series_data['corp_bonds_ts']['Volume'] > 7000]
    
    # Filter government bonds with volume > 35000
    high_volume_gov = time_series_data['gov_bonds_ts'][time_series_data['gov_bonds_ts']['Volume'] > 35000]
    
    # Filter corporate bonds in Technology sector
    tech_bonds = time_series_data['corp_bonds_ts'][time_series_data['corp_bonds_ts']['Sector'] == 'Technology']
    
    # Filter government bonds with term > 10 years
    long_term_gov = time_series_data['gov_bonds_ts'][time_series_data['gov_bonds_ts']['Term'] > 10]
    
    print(f"Corporate bonds with yield > 4.0: {high_yield_corp.shape[0]} records")
    print(f"Government bonds with yield > 2.0: {high_yield_gov.shape[0]} records")
    print(f"Corporate bonds with volume > 7000: {high_volume_corp.shape[0]} records")
    print(f"Government bonds with volume > 35000: {high_volume_gov.shape[0]} records")
    print(f"Technology sector bonds: {tech_bonds.shape[0]} records")
    print(f"Government bonds with term > 10 years: {long_term_gov.shape[0]} records")
    
    return {
        'high_yield_corp': high_yield_corp,
        'high_yield_gov': high_yield_gov,
        'high_volume_corp': high_volume_corp,
        'high_volume_gov': high_volume_gov,
        'tech_bonds': tech_bonds,
        'long_term_gov': long_term_gov
    }

def remove_specific_records(time_series_data):
    """Remove specific records based on conditions"""
    print("\nRemoving specific records...")
    
    # Create copies to avoid modifying original data
    corp_bonds_filtered = time_series_data['corp_bonds_ts'].copy()
    gov_bonds_filtered = time_series_data['gov_bonds_ts'].copy()
    
    # Remove corporate bonds with missing yield values
    corp_bonds_no_missing_yield = corp_bonds_filtered.dropna(subset=['Yield'])
    
    # Remove government bonds with missing volume values
    gov_bonds_no_missing_volume = gov_bonds_filtered.dropna(subset=['Volume'])
    
    # Remove corporate bonds from Energy sector
    corp_bonds_no_energy = corp_bonds_filtered[corp_bonds_filtered['Sector'] != 'Energy']
    
    # Remove government bonds with term = 1 (1-year treasuries)
    gov_bonds_no_1y = gov_bonds_filtered[gov_bonds_filtered['Term'] != 1]
    
    print(f"Corporate bonds after removing missing yields: {corp_bonds_no_missing_yield.shape[0]} records (removed {corp_bonds_filtered.shape[0] - corp_bonds_no_missing_yield.shape[0]} records)")
    print(f"Government bonds after removing missing volumes: {gov_bonds_no_missing_volume.shape[0]} records (removed {gov_bonds_filtered.shape[0] - gov_bonds_no_missing_volume.shape[0]} records)")
    print(f"Corporate bonds after removing Energy sector: {corp_bonds_no_energy.shape[0]} records (removed {corp_bonds_filtered.shape[0] - corp_bonds_no_energy.shape[0]} records)")
    print(f"Government bonds after removing 1-year treasuries: {gov_bonds_no_1y.shape[0]} records (removed {gov_bonds_filtered.shape[0] - gov_bonds_no_1y.shape[0]} records)")
    
    return {
        'corp_bonds_no_missing_yield': corp_bonds_no_missing_yield,
        'gov_bonds_no_missing_volume': gov_bonds_no_missing_volume,
        'corp_bonds_no_energy': corp_bonds_no_energy,
        'gov_bonds_no_1y': gov_bonds_no_1y
    }

def handle_missing_values(time_series_data):
    """Handle missing values in time series data"""
    print("\nHandling missing values...")
    
    # Create copies to avoid modifying original data
    corp_yield_pivot_filled = time_series_data['corp_yield_pivot'].copy()
    gov_yield_pivot_filled = time_series_data['gov_yield_pivot'].copy()
    
    # Fill missing values using forward fill method
    corp_yield_pivot_ffill = corp_yield_pivot_filled.ffill()
    
    # Fill missing values using backward fill method
    gov_yield_pivot_bfill = gov_yield_pivot_filled.bfill()
    
    # Fill missing values using linear interpolation
    corp_yield_pivot_interp = corp_yield_pivot_filled.interpolate(method='linear')
    gov_yield_pivot_interp = gov_yield_pivot_filled.interpolate(method='linear')
    
    # Fill missing values with mean of the column
    corp_yield_pivot_mean = corp_yield_pivot_filled.fillna(corp_yield_pivot_filled.mean())
    gov_yield_pivot_mean = gov_yield_pivot_filled.fillna(gov_yield_pivot_filled.mean())
    
    # Count missing values before and after filling
    corp_missing_before = corp_yield_pivot_filled.isna().sum().sum()
    corp_missing_after_interp = corp_yield_pivot_interp.isna().sum().sum()
    
    gov_missing_before = gov_yield_pivot_filled.isna().sum().sum()
    gov_missing_after_interp = gov_yield_pivot_interp.isna().sum().sum()
    
    print(f"Corporate bonds missing values before: {corp_missing_before}")
    print(f"Corporate bonds missing values after interpolation: {corp_missing_after_interp}")
    print(f"Government bonds missing values before: {gov_missing_before}")
    print(f"Government bonds missing values after interpolation: {gov_missing_after_interp}")
    
    return {
        'corp_yield_pivot_ffill': corp_yield_pivot_ffill,
        'gov_yield_pivot_bfill': gov_yield_pivot_bfill,
        'corp_yield_pivot_interp': corp_yield_pivot_interp,
        'gov_yield_pivot_interp': gov_yield_pivot_interp,
        'corp_yield_pivot_mean': corp_yield_pivot_mean,
        'gov_yield_pivot_mean': gov_yield_pivot_mean
    }

def save_filtered_data(filtered_data):
    """Save the filtered data to files"""
    # Create a directory for filtered data if it doesn't exist
    os.makedirs('../data/filtered', exist_ok=True)
    
    # Save date range filtered data
    filtered_data['corp_q1_2020'].to_csv('../data/filtered/corp_q1_2020.csv')
    filtered_data['gov_q1_2020'].to_csv('../data/filtered/gov_q1_2020.csv')
    filtered_data['corp_q3_2021'].to_csv('../data/filtered/corp_q3_2021.csv')
    filtered_data['gov_q3_2021'].to_csv('../data/filtered/gov_q3_2021.csv')
    
    # Save condition filtered data
    filtered_data['high_yield_corp'].to_csv('../data/filtered/high_yield_corp.csv')
    filtered_data['high_yield_gov'].to_csv('../data/filtered/high_yield_gov.csv')
    filtered_data['tech_bonds'].to_csv('../data/filtered/tech_bonds.csv')
    filtered_data['long_term_gov'].to_csv('../data/filtered/long_term_gov.csv')
    
    # Save data with removed records
    filtered_data['corp_bonds_no_missing_yield'].to_csv('../data/filtered/corp_bonds_no_missing_yield.csv')
    filtered_data['gov_bonds_no_missing_volume'].to_csv('../data/filtered/gov_bonds_no_missing_volume.csv')
    
    # Save data with filled missing values
    filtered_data['corp_yield_pivot_interp'].to_csv('../data/filtered/corp_yield_pivot_interp.csv')
    filtered_data['gov_yield_pivot_interp'].to_csv('../data/filtered/gov_yield_pivot_interp.csv')
    
    print("\nFiltered data saved to data/filtered directory")

if __name__ == "__main__":
    # Load time series data
    time_series_data = load_time_series_data()
    
    # Filter by date range
    date_filtered_data = filter_by_date_range(time_series_data)
    
    # Filter by conditions
    condition_filtered_data = filter_by_conditions(time_series_data)
    
    # Remove specific records
    records_removed_data = remove_specific_records(time_series_data)
    
    # Handle missing values
    missing_values_handled_data = handle_missing_values(time_series_data)
    
    # Combine all filtered data
    all_filtered_data = {}
    all_filtered_data.update(date_filtered_data)
    all_filtered_data.update(condition_filtered_data)
    all_filtered_data.update(records_removed_data)
    all_filtered_data.update(missing_values_handled_data)
    
    # Save filtered data
    save_filtered_data(all_filtered_data)
    
    print("\nData filtering and manipulation completed successfully!")
