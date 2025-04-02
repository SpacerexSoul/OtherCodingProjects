import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def load_datasets():
    """Load the corporate and government bond datasets"""
    print("Loading bond datasets...")
    
    # Load corporate bonds
    corp_bonds = pd.read_csv('../data/corporate_bonds.csv')
    
    # Load government bonds
    gov_bonds = pd.read_csv('../data/government_bonds.csv')
    
    print(f"Loaded corporate bonds: {corp_bonds.shape[0]} records")
    print(f"Loaded government bonds: {gov_bonds.shape[0]} records")
    
    return corp_bonds, gov_bonds

def prepare_datasets(corp_bonds, gov_bonds):
    """Prepare the datasets for analysis"""
    print("\nPreparing datasets for analysis...")
    
    # Convert Date columns to datetime
    date_columns = ['Date', 'Issue Date', 'Maturity Date']
    for col in date_columns:
        if col in corp_bonds.columns:
            corp_bonds[col] = pd.to_datetime(corp_bonds[col])
        if col in gov_bonds.columns:
            gov_bonds[col] = pd.to_datetime(gov_bonds[col])
    
    # Convert numeric columns that might be loaded as strings
    numeric_columns = ['Face OS', 'Mkt Cap', 'Mkt Cap %', 'Avr. Life', 'EIR Duration',
                      'Blended YTM', 'Stripped YTM', 'Blended Spread', 'Stripped Spread',
                      'Spread Duration', 'Daily Change (%)', 'MTD Change (%)', 'YTD Change (%)',
                      'Current Face Price Bid', 'Current Face Price Offer',
                      'Original Face Price Bid', 'Original Face Price Offer',
                      'Dirty Price', 'Accrued Interest']
    
    for col in numeric_columns:
        if col in corp_bonds.columns:
            corp_bonds[col] = pd.to_numeric(corp_bonds[col], errors='coerce')
        if col in gov_bonds.columns:
            gov_bonds[col] = pd.to_numeric(gov_bonds[col], errors='coerce')
    
    # Check for missing values in each dataset
    print("\nMissing values in corporate bonds:")
    print(corp_bonds.isna().sum())
    
    print("\nMissing values in government bonds:")
    print(gov_bonds.isna().sum())
    
    # Basic statistics for each dataset
    print("\nCorporate bonds statistics:")
    print(corp_bonds.describe())
    
    print("\nGovernment bonds statistics:")
    print(gov_bonds.describe())
    
    # Create a summary of bond types
    print("\nCorporate bond types:")
    print(corp_bonds.groupby(['BondID', 'BondName', 'Sector']).size().reset_index(name='Count'))
    
    print("\nGovernment bond types:")
    print(gov_bonds.groupby(['BondID', 'BondName', 'Term']).size().reset_index(name='Count'))
    
    return corp_bonds, gov_bonds

def save_prepared_data(corp_bonds, gov_bonds):
    """Save the prepared datasets"""
    # Create a directory for prepared data if it doesn't exist
    os.makedirs('../data/prepared', exist_ok=True)
    
    # Save prepared datasets
    corp_bonds.to_csv('../data/prepared/corp_bonds_prepared.csv', index=False)
    gov_bonds.to_csv('../data/prepared/gov_bonds_prepared.csv', index=False)
    
    print("\nPrepared datasets saved to data/prepared directory")

if __name__ == "__main__":
    # Load datasets
    corp_bonds, gov_bonds = load_datasets()
    
    # Prepare datasets
    corp_bonds, gov_bonds = prepare_datasets(corp_bonds, gov_bonds)
    
    # Save prepared data
    save_prepared_data(corp_bonds, gov_bonds)
    
    print("\nData preparation completed successfully!")
