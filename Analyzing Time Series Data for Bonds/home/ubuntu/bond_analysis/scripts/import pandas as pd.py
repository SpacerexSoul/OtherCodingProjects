import pandas as pd
import os

def load_datasets(data_dir='../data/'):
    """Load multiple corporate and government bond datasets
    
    Args:
        data_dir: Path to the directory containing data files (default: '../data/')
    """
    print(f"Loading bond datasets from {data_dir}...")
    
    # Check if directory exists
    if not os.path.exists(data_dir):
        print(f"Warning: Directory {data_dir} not found!")
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created empty directory: {data_dir}")
        return {}, {}
    
    all_files = os.listdir(data_dir)
    
    # Find all relevant CSV files
    corp_files = [f for f in all_files if f.startswith('Corp_') and f.endswith('.csv')]
    gov_files = [f for f in all_files if f.startswith('Gov_') and f.endswith('.csv')]
    
    # Load corporate bond files
    corp_dfs = {}
    for file in corp_files:
        name = file.replace('.csv', '')
        corp_dfs[name] = pd.read_csv(os.path.join(data_dir, file))
        print(f"Loaded {name}: {corp_dfs[name].shape[0]} records")
    
    # Load government bond files
    gov_dfs = {}
    for file in gov_files:
        name = file.replace('.csv', '')
        gov_dfs[name] = pd.read_csv(os.path.join(data_dir, file))
        print(f"Loaded {name}: {gov_dfs[name].shape[0]} records")
    
    return corp_dfs, gov_dfs

def prepare_datasets(corp_dfs, gov_dfs):
    """Prepare the datasets for analysis"""
    print("\nPreparing datasets for analysis...")
    
    # Process corporate bond dataframes
    for name, df in corp_dfs.items():
        print(f"\nProcessing {name}...")
        # Convert Date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        # Check for missing values
        print(f"Missing values in {name}:")
        print(df.isna().sum())
        
        # Basic statistics
        print(f"\n{name} statistics:")
        print(df.describe())
        
        # Summary of bond types if applicable columns exist
        if all(col in df.columns for col in ['BondID', 'BondName', 'Sector']):
            print(f"\n{name} bond types:")
            print(df.groupby(['BondID', 'BondName', 'Sector']).size().reset_index(name='Count'))
    
    # Process government bond dataframes
    for name, df in gov_dfs.items():
        print(f"\nProcessing {name}...")
        # Convert Date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        # Check for missing values
        print(f"Missing values in {name}:")
        print(df.isna().sum())
        
        # Basic statistics
        print(f"\n{name} statistics:")
        print(df.describe())
        
        # Summary of bond types if applicable columns exist
        if all(col in df.columns for col in ['BondID', 'BondName', 'Term']):
            print(f"\n{name} bond types:")
            print(df.groupby(['BondID', 'BondName', 'Term']).size().reset_index(name='Count'))
    
    return corp_dfs, gov_dfs

def save_prepared_data(corp_dfs, gov_dfs, output_dir='../data/prepared'):
    """Save the prepared datasets
    
    Args:
        corp_dfs: Dictionary of corporate bond dataframes
        gov_dfs: Dictionary of government bond dataframes
        output_dir: Directory to save prepared data (default: '../data/prepared')
    """
    # Create a directory for prepared data if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save corporate bond dataframes
    for name, df in corp_dfs.items():
        output_path = os.path.join(output_dir, f"{name}_prepared.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved {name} to {output_path}")
    
    # Save government bond dataframes
    for name, df in gov_dfs.items():
        output_path = os.path.join(output_dir, f"{name}_prepared.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved {name} to {output_path}")
    
    print(f"\nPrepared datasets saved to {output_dir}")

if __name__ == "__main__":
    # You can specify the data directory here
    data_dir = '../data/'  # Changed from './data/' to '../data/'
    
    # Load datasets
    corp_dfs, gov_dfs = load_datasets(data_dir)
    
    # Prepare datasets
    corp_dfs, gov_dfs = prepare_datasets(corp_dfs, gov_dfs)
    
    # Save prepared data using the same base directory
    output_dir = os.path.join(data_dir, 'prepared')  # Fixed to avoid redundant data directory
    save_prepared_data(corp_dfs, gov_dfs, output_dir)
    
    print("\nData preparation completed successfully!")