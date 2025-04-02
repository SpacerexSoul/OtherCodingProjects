import pandas as pd
import os
from datetime import datetime, timedelta

def create_sample_fund_admin():
    """Create a sample fund admin file with test data."""
    # Ensure directory exists
    os.makedirs("data/fund_admin_updates", exist_ok=True)
    
    # Create sample data
    data = [
        {
            'investor_id': 'INV001',
            'investor_name': 'Global Ventures Ltd',
            'fund_type': 'Private Equity',
            'investment_amount': 5000000,
            'transaction_date': '2024-03-01',
            'transaction_type': 'inflow'
        },
        {
            'investor_id': 'INV002',
            'investor_name': 'Tech Growth Partners',
            'fund_type': 'Venture Capital',
            'investment_amount': 3000000,
            'transaction_date': '2024-03-15',
            'transaction_type': 'inflow'
        },
        {
            'investor_id': 'INV003',
            'investor_name': 'Real Estate Fund I',
            'fund_type': 'Real Estate',
            'investment_amount': 7500000,
            'transaction_date': '2024-03-20',
            'transaction_type': 'inflow'
        },
        {
            'investor_id': 'INV001',
            'investor_name': 'Global Ventures Ltd',
            'fund_type': 'Private Equity',
            'investment_amount': 1000000,
            'transaction_date': '2024-03-25',
            'transaction_type': 'outflow'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_file = "data/fund_admin_updates/march_2024_fund_admin.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nCreated sample fund admin file: {output_file}")
    print("\nSample data summary:")
    print("-" * 50)
    print(f"Total records: {len(df)}")
    print(f"Total inflows: ${df[df['transaction_type'] == 'inflow']['investment_amount'].sum():,.2f}")
    print(f"Total outflows: ${df[df['transaction_type'] == 'outflow']['investment_amount'].sum():,.2f}")
    print(f"Net flow: ${(df[df['transaction_type'] == 'inflow']['investment_amount'].sum() - df[df['transaction_type'] == 'outflow']['investment_amount'].sum()):,.2f}")
    print("-" * 50)
    
    return output_file

if __name__ == "__main__":
    create_sample_fund_admin() 