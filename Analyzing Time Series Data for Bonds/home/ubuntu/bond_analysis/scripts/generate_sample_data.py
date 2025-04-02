import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

# Create directory if it doesn't exist
os.makedirs('../data', exist_ok=True)

# Function to generate dates
def generate_dates(start_date, num_days):
    return [start_date + timedelta(days=i) for i in range(num_days)]

# Generate corporate bond dataset
def generate_corporate_bonds():
    # Parameters
    start_date = datetime(2020, 1, 1)
    num_days = 365 * 2  # 2 years of data
    num_bonds = 5
    
    # Bond identifiers and names
    bond_ids = [f'CORP{i:03d}' for i in range(1, num_bonds + 1)]
    bond_names = [
        'Tech Inc. 5Y Bond', 
        'Energy Corp 7Y Bond', 
        'Finance Group 3Y Bond', 
        'Manufacturing Ltd 10Y Bond',
        'Healthcare Systems 5Y Bond'
    ]
    
    # Credit ratings
    ratings = ['AAA', 'AA+', 'AA', 'A+', 'A', 'BBB+', 'BBB']
    bond_ratings = np.random.choice(ratings, num_bonds)
    
    # Generate dates
    dates = generate_dates(start_date, num_days)
    
    # Base yields for each bond (different starting points)
    base_yields = np.random.uniform(2.0, 5.0, num_bonds)
    
    # Create data
    data = []
    for day_idx, date in enumerate(dates):
        for bond_idx in range(num_bonds):
            # Some randomness in the yield
            random_factor = np.sin(day_idx / 180 * np.pi) * 0.5 + np.random.normal(0, 0.1)
            yield_value = base_yields[bond_idx] + random_factor
            
            # Occasionally introduce missing values
            if np.random.random() < 0.05:  # 5% chance of missing value
                yield_value = np.nan
                
            # Volume with some randomness
            volume = np.random.randint(1000, 10000) if np.random.random() > 0.1 else np.nan
            
            data.append({
                'Date': date,
                'BondID': bond_ids[bond_idx],
                'BondName': bond_names[bond_idx],
                'Rating': bond_ratings[bond_idx],
                'Yield': yield_value,
                'Volume': volume,
                'Sector': ['Technology', 'Energy', 'Finance', 'Manufacturing', 'Healthcare'][bond_idx]
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('../data/corporate_bonds.csv', index=False)
    print(f"Corporate bond dataset created with {len(df)} records")
    return df

# Generate government bond dataset
def generate_government_bonds():
    # Parameters
    start_date = datetime(2020, 1, 1)
    num_days = 365 * 2  # 2 years of data
    
    # Bond terms (in years)
    terms = [1, 2, 5, 10, 30]
    bond_ids = [f'GOV{term:02d}Y' for term in terms]
    bond_names = [f'{term}-Year Treasury' for term in terms]
    
    # Generate dates
    dates = generate_dates(start_date, num_days)
    
    # Base yields for each term (increasing with term)
    base_yields = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    # Create data
    data = []
    for day_idx, date in enumerate(dates):
        for term_idx, term in enumerate(terms):
            # Some randomness in the yield with trend
            trend = np.sin(day_idx / 180 * np.pi) * 0.3  # Seasonal component
            random_factor = trend + np.random.normal(0, 0.05)
            yield_value = base_yields[term_idx] + random_factor
            
            # Occasionally introduce missing values
            if np.random.random() < 0.03:  # 3% chance of missing value
                yield_value = np.nan
                
            # Trading volume
            volume = np.random.randint(5000, 50000) if np.random.random() > 0.05 else np.nan
            
            data.append({
                'Date': date,
                'BondID': bond_ids[term_idx],
                'BondName': bond_names[term_idx],
                'Term': term,
                'Yield': yield_value,
                'Volume': volume,
                'Country': 'USA'
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('../data/government_bonds.csv', index=False)
    print(f"Government bond dataset created with {len(df)} records")
    return df

if __name__ == "__main__":
    print("Generating sample bond datasets...")
    corp_df = generate_corporate_bonds()
    gov_df = generate_government_bonds()
    print("Sample datasets generated successfully!")
    
    # Display sample of each dataset
    print("\nCorporate Bonds Sample:")
    print(corp_df.head())
    
    print("\nGovernment Bonds Sample:")
    print(gov_df.head())
