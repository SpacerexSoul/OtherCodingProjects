import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def load_datasets_for_merging():
    """Load the datasets for merging"""
    print("Loading datasets for merging...")
    
    # Load the original prepared datasets
    corp_bonds = pd.read_csv('../data/prepared/corp_bonds_prepared.csv')
    corp_bonds['Date'] = pd.to_datetime(corp_bonds['Date'])
    
    gov_bonds = pd.read_csv('../data/prepared/gov_bonds_prepared.csv')
    gov_bonds['Date'] = pd.to_datetime(gov_bonds['Date'])
    
    # Load some of the statistics
    corp_monthly_mean = pd.read_csv('../data/statistics/corp_monthly_mean.csv')
    corp_monthly_mean['Date'] = pd.to_datetime(corp_monthly_mean['Date'])
    
    gov_monthly_mean = pd.read_csv('../data/statistics/gov_monthly_mean.csv')
    gov_monthly_mean['Date'] = pd.to_datetime(gov_monthly_mean['Date'])
    
    # Load the yield pivot tables
    corp_yield_pivot = pd.read_csv('../data/filtered/corp_yield_pivot_interp.csv')
    corp_yield_pivot['Date'] = pd.to_datetime(corp_yield_pivot['Date'])
    
    gov_yield_pivot = pd.read_csv('../data/filtered/gov_yield_pivot_interp.csv')
    gov_yield_pivot['Date'] = pd.to_datetime(gov_yield_pivot['Date'])
    
    print(f"Loaded datasets for merging successfully")
    
    return {
        'corp_bonds': corp_bonds,
        'gov_bonds': gov_bonds,
        'corp_monthly_mean': corp_monthly_mean,
        'gov_monthly_mean': gov_monthly_mean,
        'corp_yield_pivot': corp_yield_pivot,
        'gov_yield_pivot': gov_yield_pivot
    }

def merge_corporate_government_daily():
    """Merge corporate and government bond data on a daily basis"""
    print("\nMerging corporate and government bond data on a daily basis...")
    
    # Load the datasets
    datasets = load_datasets_for_merging()
    corp_bonds = datasets['corp_bonds']
    gov_bonds = datasets['gov_bonds']
    
    # Create a date range that covers both datasets
    all_dates = pd.date_range(
        start=min(corp_bonds['Date'].min(), gov_bonds['Date'].min()),
        end=max(corp_bonds['Date'].max(), gov_bonds['Date'].max()),
        freq='D'
    )
    
    # Create a dataframe with all dates
    date_df = pd.DataFrame({'Date': all_dates})
    
    # Calculate daily average yields for corporate bonds
    corp_daily_avg = corp_bonds.groupby('Date')['Yield'].mean().reset_index()
    corp_daily_avg.rename(columns={'Yield': 'CorpYield'}, inplace=True)
    
    # Calculate daily average yields for government bonds
    gov_daily_avg = gov_bonds.groupby('Date')['Yield'].mean().reset_index()
    gov_daily_avg.rename(columns={'Yield': 'GovYield'}, inplace=True)
    
    # Calculate daily average volumes for corporate bonds
    corp_daily_vol = corp_bonds.groupby('Date')['Volume'].mean().reset_index()
    corp_daily_vol.rename(columns={'Volume': 'CorpVolume'}, inplace=True)
    
    # Calculate daily average volumes for government bonds
    gov_daily_vol = gov_bonds.groupby('Date')['Volume'].mean().reset_index()
    gov_daily_vol.rename(columns={'Volume': 'GovVolume'}, inplace=True)
    
    # Merge all daily data
    merged_daily = date_df.merge(corp_daily_avg, on='Date', how='left')
    merged_daily = merged_daily.merge(gov_daily_avg, on='Date', how='left')
    merged_daily = merged_daily.merge(corp_daily_vol, on='Date', how='left')
    merged_daily = merged_daily.merge(gov_daily_vol, on='Date', how='left')
    
    # Calculate the spread between corporate and government yields
    merged_daily['YieldSpread'] = merged_daily['CorpYield'] - merged_daily['GovYield']
    
    # Calculate the ratio of corporate to government volumes
    merged_daily['VolumeRatio'] = merged_daily['CorpVolume'] / merged_daily['GovVolume']
    
    print(f"Merged daily data shape: {merged_daily.shape}")
    print(f"Merged daily data columns: {merged_daily.columns.tolist()}")
    
    return merged_daily

def merge_yield_pivots():
    """Merge corporate and government bond yield pivot tables"""
    print("\nMerging corporate and government bond yield pivot tables...")
    
    # Load the datasets
    datasets = load_datasets_for_merging()
    corp_yield_pivot = datasets['corp_yield_pivot']
    gov_yield_pivot = datasets['gov_yield_pivot']
    
    # Rename columns to avoid conflicts
    corp_cols = corp_yield_pivot.columns.tolist()
    gov_cols = gov_yield_pivot.columns.tolist()
    
    # Remove 'Date' from the lists if present
    if 'Date' in corp_cols:
        corp_cols.remove('Date')
    if 'Date' in gov_cols:
        gov_cols.remove('Date')
    
    # Create new column names with prefixes
    corp_yield_pivot_renamed = corp_yield_pivot.copy()
    gov_yield_pivot_renamed = gov_yield_pivot.copy()
    
    for col in corp_cols:
        if col != 'Date':
            corp_yield_pivot_renamed.rename(columns={col: f'Corp_{col}'}, inplace=True)
    
    for col in gov_cols:
        if col != 'Date':
            gov_yield_pivot_renamed.rename(columns={col: f'Gov_{col}'}, inplace=True)
    
    # Merge the renamed pivot tables
    merged_pivots = pd.merge(
        corp_yield_pivot_renamed,
        gov_yield_pivot_renamed,
        on='Date',
        how='outer'
    )
    
    print(f"Merged pivot data shape: {merged_pivots.shape}")
    print(f"Merged pivot data columns: {merged_pivots.columns.tolist()[:10]} ... (and more)")
    
    return merged_pivots

def merge_monthly_data():
    """Merge monthly statistics for corporate and government bonds"""
    print("\nMerging monthly statistics for corporate and government bonds...")
    
    # Load the datasets
    datasets = load_datasets_for_merging()
    corp_monthly_mean = datasets['corp_monthly_mean']
    gov_monthly_mean = datasets['gov_monthly_mean']
    
    # Rename columns to avoid conflicts
    corp_monthly_mean.rename(columns={'Yield': 'CorpYield'}, inplace=True)
    gov_monthly_mean.rename(columns={'Yield': 'GovYield'}, inplace=True)
    
    # Merge the monthly data
    merged_monthly = pd.merge(
        corp_monthly_mean,
        gov_monthly_mean,
        on='Date',
        how='outer'
    )
    
    # Calculate the monthly spread
    merged_monthly['MonthlySpread'] = merged_monthly['CorpYield'] - merged_monthly['GovYield']
    
    print(f"Merged monthly data shape: {merged_monthly.shape}")
    print(f"Merged monthly data columns: {merged_monthly.columns.tolist()}")
    
    return merged_monthly

def merge_by_sector_and_term():
    """Create a merged dataset with sector and term information"""
    print("\nCreating a merged dataset with sector and term information...")
    
    # Load the datasets
    datasets = load_datasets_for_merging()
    corp_bonds = datasets['corp_bonds']
    gov_bonds = datasets['gov_bonds']
    
    # Create a sector summary for corporate bonds
    corp_sector_summary = corp_bonds.groupby(['Date', 'Sector']).agg({
        'Yield': 'mean',
        'Volume': 'sum'
    }).reset_index()
    corp_sector_summary.rename(columns={
        'Yield': 'SectorYield',
        'Volume': 'SectorVolume'
    }, inplace=True)
    
    # Create a term summary for government bonds
    gov_term_summary = gov_bonds.groupby(['Date', 'Term']).agg({
        'Yield': 'mean',
        'Volume': 'sum'
    }).reset_index()
    gov_term_summary.rename(columns={
        'Yield': 'TermYield',
        'Volume': 'TermVolume'
    }, inplace=True)
    
    # Create a cross-reference between sectors and terms
    # For each date, create all possible combinations of sectors and terms
    dates = pd.date_range(
        start=min(corp_bonds['Date'].min(), gov_bonds['Date'].min()),
        end=max(corp_bonds['Date'].max(), gov_bonds['Date'].max()),
        freq='D'
    )
    
    sectors = corp_bonds['Sector'].unique()
    terms = gov_bonds['Term'].unique()
    
    # Create all combinations
    date_list = []
    sector_list = []
    term_list = []
    
    for date in dates:
        for sector in sectors:
            for term in terms:
                date_list.append(date)
                sector_list.append(sector)
                term_list.append(term)
    
    # Create the cross-reference dataframe
    cross_ref = pd.DataFrame({
        'Date': date_list,
        'Sector': sector_list,
        'Term': term_list
    })
    
    # Merge with sector summary
    merged_sector_term = cross_ref.merge(
        corp_sector_summary,
        on=['Date', 'Sector'],
        how='left'
    )
    
    # Merge with term summary
    merged_sector_term = merged_sector_term.merge(
        gov_term_summary,
        on=['Date', 'Term'],
        how='left'
    )
    
    # Calculate the yield difference between sector and term
    merged_sector_term['YieldDiff'] = merged_sector_term['SectorYield'] - merged_sector_term['TermYield']
    
    # Calculate the volume ratio between sector and term
    merged_sector_term['VolumeRatio'] = merged_sector_term['SectorVolume'] / merged_sector_term['TermVolume']
    
    print(f"Merged sector-term data shape: {merged_sector_term.shape}")
    print(f"Merged sector-term data columns: {merged_sector_term.columns.tolist()}")
    
    return merged_sector_term

def save_merged_data(merged_data):
    """Save the merged datasets to files"""
    # Create a directory for merged data if it doesn't exist
    os.makedirs('../data/merged', exist_ok=True)
    
    # Save merged daily data
    merged_data['merged_daily'].to_csv('../data/merged/merged_daily.csv', index=False)
    
    # Save merged pivot data
    merged_data['merged_pivots'].to_csv('../data/merged/merged_pivots.csv', index=False)
    
    # Save merged monthly data
    merged_data['merged_monthly'].to_csv('../data/merged/merged_monthly.csv', index=False)
    
    # Save merged sector-term data
    merged_data['merged_sector_term'].to_csv('../data/merged/merged_sector_term.csv', index=False)
    
    print("\nMerged datasets saved to data/merged directory")

if __name__ == "__main__":
    # Merge corporate and government bond data on a daily basis
    merged_daily = merge_corporate_government_daily()
    
    # Merge corporate and government bond yield pivot tables
    merged_pivots = merge_yield_pivots()
    
    # Merge monthly statistics for corporate and government bonds
    merged_monthly = merge_monthly_data()
    
    # Create a merged dataset with sector and term information
    merged_sector_term = merge_by_sector_and_term()
    
    # Combine all merged datasets
    all_merged_data = {
        'merged_daily': merged_daily,
        'merged_pivots': merged_pivots,
        'merged_monthly': merged_monthly,
        'merged_sector_term': merged_sector_term
    }
    
    # Save merged data
    save_merged_data(all_merged_data)
    
    print("\nDataset merging completed successfully!")
