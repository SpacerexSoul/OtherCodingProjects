import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def load_prepared_datasets():
    """Load the prepared corporate and government bond datasets"""
    print("Loading prepared bond datasets...")
    
    # Load prepared corporate bonds
    corp_bonds = pd.read_csv('../data/prepared/corp_bonds_prepared.csv')
    corp_bonds['Date'] = pd.to_datetime(corp_bonds['Date'])
    
    # Load prepared government bonds
    gov_bonds = pd.read_csv('../data/prepared/gov_bonds_prepared.csv')
    gov_bonds['Date'] = pd.to_datetime(gov_bonds['Date'])
    
    print(f"Loaded prepared corporate bonds: {corp_bonds.shape[0]} records")
    print(f"Loaded prepared government bonds: {gov_bonds.shape[0]} records")
    
    return corp_bonds, gov_bonds

def create_time_series_indices(corp_bonds, gov_bonds):
    """Create time series indices for both datasets"""
    print("\nCreating time series indices...")
    
    # Set Date as index for both datasets
    corp_bonds_ts = corp_bonds.copy()
    corp_bonds_ts.set_index('Date', inplace=True)
    
    gov_bonds_ts = gov_bonds.copy()
    gov_bonds_ts.set_index('Date', inplace=True)
    
    # Create a pivot table for corporate bonds (Date x BondID with Yield values)
    corp_yield_pivot = corp_bonds.pivot(index='Date', columns='BondID', values='Yield')
    print("\nCorporate bonds yield pivot table (first 5 rows):")
    print(corp_yield_pivot.head())
    
    # Create a pivot table for government bonds (Date x BondID with Yield values)
    gov_yield_pivot = gov_bonds.pivot(index='Date', columns='BondID', values='Yield')
    print("\nGovernment bonds yield pivot table (first 5 rows):")
    print(gov_yield_pivot.head())
    
    # Create monthly average yields for corporate bonds by sector
    monthly_corp_by_sector = corp_bonds.copy()
    monthly_corp_by_sector['Month'] = monthly_corp_by_sector['Date'].dt.to_period('M')
    monthly_corp_sector_avg = monthly_corp_by_sector.groupby(['Month', 'Sector'])['Yield'].mean().reset_index()
    monthly_corp_sector_pivot = monthly_corp_sector_avg.pivot(index='Month', columns='Sector', values='Yield')
    
    print("\nMonthly average corporate bond yields by sector (first 5 rows):")
    print(monthly_corp_sector_pivot.head())
    
    # Create monthly average yields for government bonds by term
    monthly_gov_by_term = gov_bonds.copy()
    monthly_gov_by_term['Month'] = monthly_gov_by_term['Date'].dt.to_period('M')
    monthly_gov_term_avg = monthly_gov_by_term.groupby(['Month', 'Term'])['Yield'].mean().reset_index()
    monthly_gov_term_pivot = monthly_gov_term_avg.pivot(index='Month', columns='Term', values='Yield')
    
    print("\nMonthly average government bond yields by term (first 5 rows):")
    print(monthly_gov_term_pivot.head())
    
    # Create weekly average yields
    corp_bonds['Week'] = corp_bonds['Date'].dt.to_period('W')
    weekly_corp_avg = corp_bonds.groupby(['Week', 'BondID'])['Yield'].mean().reset_index()
    
    gov_bonds['Week'] = gov_bonds['Date'].dt.to_period('W')
    weekly_gov_avg = gov_bonds.groupby(['Week', 'BondID'])['Yield'].mean().reset_index()
    
    print("\nWeekly average corporate bond yields (first 5 rows):")
    print(weekly_corp_avg.head())
    
    print("\nWeekly average government bond yields (first 5 rows):")
    print(weekly_gov_avg.head())
    
    # Create quarterly average yields
    corp_bonds['Quarter'] = corp_bonds['Date'].dt.to_period('Q')
    quarterly_corp_avg = corp_bonds.groupby(['Quarter', 'BondID'])['Yield'].mean().reset_index()
    
    gov_bonds['Quarter'] = gov_bonds['Date'].dt.to_period('Q')
    quarterly_gov_avg = gov_bonds.groupby(['Quarter', 'BondID'])['Yield'].mean().reset_index()
    
    print("\nQuarterly average corporate bond yields (first 5 rows):")
    print(quarterly_corp_avg.head())
    
    print("\nQuarterly average government bond yields (first 5 rows):")
    print(quarterly_gov_avg.head())
    
    return {
        'corp_bonds_ts': corp_bonds_ts,
        'gov_bonds_ts': gov_bonds_ts,
        'corp_yield_pivot': corp_yield_pivot,
        'gov_yield_pivot': gov_yield_pivot,
        'monthly_corp_sector_pivot': monthly_corp_sector_pivot,
        'monthly_gov_term_pivot': monthly_gov_term_pivot,
        'weekly_corp_avg': weekly_corp_avg,
        'weekly_gov_avg': weekly_gov_avg,
        'quarterly_corp_avg': quarterly_corp_avg,
        'quarterly_gov_avg': quarterly_gov_avg
    }

def save_time_series_data(time_series_data):
    """Save the time series data to files"""
    # Create a directory for time series data if it doesn't exist
    os.makedirs('../data/time_series', exist_ok=True)
    
    # Save time series data
    time_series_data['corp_bonds_ts'].to_csv('../data/time_series/corp_bonds_ts.csv')
    time_series_data['gov_bonds_ts'].to_csv('../data/time_series/gov_bonds_ts.csv')
    time_series_data['corp_yield_pivot'].to_csv('../data/time_series/corp_yield_pivot.csv')
    time_series_data['gov_yield_pivot'].to_csv('../data/time_series/gov_yield_pivot.csv')
    
    # Convert period index to string for saving
    monthly_corp = time_series_data['monthly_corp_sector_pivot'].copy()
    monthly_corp.index = monthly_corp.index.astype(str)
    monthly_corp.to_csv('../data/time_series/monthly_corp_sector_pivot.csv')
    
    monthly_gov = time_series_data['monthly_gov_term_pivot'].copy()
    monthly_gov.index = monthly_gov.index.astype(str)
    monthly_gov.to_csv('../data/time_series/monthly_gov_term_pivot.csv')
    
    # Save weekly and quarterly data
    weekly_corp = time_series_data['weekly_corp_avg'].copy()
    weekly_corp['Week'] = weekly_corp['Week'].astype(str)
    weekly_corp.to_csv('../data/time_series/weekly_corp_avg.csv', index=False)
    
    weekly_gov = time_series_data['weekly_gov_avg'].copy()
    weekly_gov['Week'] = weekly_gov['Week'].astype(str)
    weekly_gov.to_csv('../data/time_series/weekly_gov_avg.csv', index=False)
    
    quarterly_corp = time_series_data['quarterly_corp_avg'].copy()
    quarterly_corp['Quarter'] = quarterly_corp['Quarter'].astype(str)
    quarterly_corp.to_csv('../data/time_series/quarterly_corp_avg.csv', index=False)
    
    quarterly_gov = time_series_data['quarterly_gov_avg'].copy()
    quarterly_gov['Quarter'] = quarterly_gov['Quarter'].astype(str)
    quarterly_gov.to_csv('../data/time_series/quarterly_gov_avg.csv', index=False)
    
    print("\nTime series data saved to data/time_series directory")

if __name__ == "__main__":
    # Load prepared datasets
    corp_bonds, gov_bonds = load_prepared_datasets()
    
    # Create time series indices
    time_series_data = create_time_series_indices(corp_bonds, gov_bonds)
    
    # Save time series data
    save_time_series_data(time_series_data)
    
    print("\nTime series indices creation completed successfully!")
