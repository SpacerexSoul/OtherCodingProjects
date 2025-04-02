import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

# Ensure directories exist
os.makedirs('data/fund_admin_updates', exist_ok=True)
os.makedirs('data/internal_tracker', exist_ok=True)

def generate_investor_list(count=20):
    """Generate a list of sample investors"""
    investors = []
    locations = ['Cayman Islands', 'Delaware', 'United Kingdom', 'Switzerland', 'Hong Kong', 'Jersey', 'Malta']
    
    for i in range(1, count + 1):
        unique_id = f"INV{i:03d}"
        fund_type = random.choice(['MCFLP', 'MCFLTD1'])
        investor_name = f"Investor {i} {random.choice(['LLC', 'LP', 'Ltd', 'Inc', 'Fund'])}"
        short_name = f"Inv {i}"
        location = random.choice(locations)
        
        investors.append({
            'unique_id': unique_id,
            'investor_name': investor_name,
            'investor_short_name': short_name,
            'fund_type': fund_type,
            'location': location,
            'hid': i * 10
        })
    
    return investors

def create_internal_tracker():
    """Create a sample internal tracker file"""
    investors = generate_investor_list(20)
    
    # Create a list to hold all rows
    data_rows = []
    
    # Current date
    now = datetime.now()
    
    # Generate transactions for each investor
    for investor in investors:
        # Generate 1-3 transactions per investor
        for _ in range(random.randint(1, 3)):
            # Random date in the past year
            days_ago = random.randint(30, 365)
            trans_date = now - timedelta(days=days_ago)
            
            # Random transaction type and amount
            trans_type = random.choice(['Subscription', 'Redemption', 'Additional Subscription'])
            amount = round(random.uniform(100000, 10000000), 2)
            usd_equivalent = amount  # For simplicity, assume all are USD
            
            row = {
                'Investor Name': investor['investor_name'],
                'Investor Short Name': investor['investor_short_name'],
                'Unique ID': investor['unique_id'],
                'HID': investor['hid'],
                'Currently invested': 'Y',
                'Share Class': random.choice(['A-P', 'BP']),
                'Feeder Fund': 'Delaware' if 'LP' in investor['fund_type'] else 'Cayman',
                'New/Existing': random.choice(['New', 'Existing']),
                'Sub/Trans/Red': trans_type,
                'Dealing Date': trans_date.strftime('%d/%m/%Y'),
                'Redemption Type/Size/Notes': '' if 'Redemption' not in trans_type else 'Full Redemption',
                'Implemented 5% Holdback': random.choice(['Yes', 'No', '-']),
                'Amount': amount,
                'USD Equivalent': usd_equivalent,
                'Currency': 'USD',
                'Exchange Rate': 1.0,
                'Accurate as of': now.strftime('%d/%m/%Y'),
                'Locked Until': '',
                '% ERISA': f"{random.randint(0, 100)}%",
                '$ ERISA': round(amount * random.random(), 2),
                'CFTC Rep': random.choice(['NA', 'Yes', '']),
                'Sub Doc Addendum': random.choice(['Yes', 'No', '']),
                'Sub Doc Side Letter': random.choice(['Yes', 'No', '']),
                'PPM Sup Sent': (now - timedelta(days=random.randint(1, 30))).strftime('%d/%m/%Y'),
                'Juristriction of Org/Citizen of': investor['location'],
                'Principle place of Bus/Residence': investor['location'],
                'Tax status': random.choice(['Non-US', 'US', 'USTE']),
                'Investor Domicile Country': investor['location'],
                'Marketing Approval for Subscription': random.choice(['Y-ANI', 'Y-AF', 'N/A', ''])
            }
            
            data_rows.append(row)
    
    # Create DataFrame
    internal_df = pd.DataFrame(data_rows)
    
    # Add separation headers - these will be represented as empty columns in Excel
    columns_order = [
        'Investor Name', 'Investor Short Name', 'Unique ID', 'HID', 'Currently invested',
        'Investor Details (Separation header)',  # Added as an empty column
        'Share Class', 'Feeder Fund', 'New/Existing', 'Sub/Trans/Red', 'Dealing Date',
        'Redemption Type/Size/Notes', 'Implemented 5% Holdback', 'Amount', 'USD Equivalent',
        'Currency', 'Exchange Rate', 'Accurate as of',
        'Flow Details (Separation Header)',  # Added as an empty column
        'Locked Until',
        'Terms (Separation Header)',  # Added as an empty column
        '% ERISA', '$ ERISA',
        'ERISA (Separation Header)',  # Added as an empty column
        'CFTC Rep', 'Sub Doc Addendum', 'Sub Doc Side Letter', 'PPM Sup Sent',
        'Documents (Separation Header)',  # Added as an empty column
        'Juristriction of Org/Citizen of', 'Principle place of Bus/Residence',
        'Tax status', 'Investor Domicile Country',
        'Domicile & Tax (Separation Header)',  # Added as an empty column
        'Marketing Approval for Subscription',
        'Approvals (Separation Header)'  # Added as an empty column
    ]
    
    # Ensure all columns exist
    for col in columns_order:
        if col not in internal_df.columns:
            internal_df[col] = ''
    
    # Reorder columns
    internal_df = internal_df[columns_order]
    
    # Save to Excel
    internal_df.to_excel('data/internal_tracker/sample_internal_tracker.xlsx', index=False)
    print(f"Created sample internal tracker with {len(data_rows)} entries")
    
    return internal_df

def create_fund_admin_data():
    """Create a sample fund admin data file"""
    investors = generate_investor_list(20)
    
    # Create a list to hold all rows
    data_rows = []
    
    # Current date
    now = datetime.now()
    
    # Generate transactions for each investor
    for investor in investors:
        # Generate 1-3 transactions per investor
        for _ in range(random.randint(1, 3)):
            # Random date in the past year
            days_ago = random.randint(30, 365)
            trans_date = now - timedelta(days=days_ago)
            
            # Random transaction type and amount
            trans_type = random.choice(['Subscription', 'Transfer in', 'Transfer Out', 'Exchange in', 'Exchange Out', 'Redemption'])
            amount = round(random.uniform(100000, 10000000), 2)
            
            # Random currency
            currency = random.choice(['USD', 'GBP'])
            
            # NAV and shares
            nav = round(random.uniform(900, 1100), 6)
            shares = round(amount / nav, 6)
            
            # FX rate based on currency
            fx_rate = 1.0 if currency == 'USD' else 1.39
            
            # Calculate USD equivalent
            usd_equivalent = amount * fx_rate
            
            row = {
                'Unique ID': investor['unique_id'],
                'Date': trans_date.strftime('%d/%m/%Y'),
                'Transaction Type': trans_type,
                'Non-Cash Trans': random.choice(['Yes', 'No']),
                'Feeder': investor['fund_type'],
                'Fund Name': 'Limited' if 'LTD' in investor['fund_type'] else 'LP',
                'Currency': currency,
                'Class': random.choice(['A-P USD', 'BP']),
                'Series': random.choice(['Initial', '10 2021', '']),
                'ID': random.randint(1, 20),
                'New or Existing Investor': random.choice(['New', 'Existing']),
                'Amount': amount,
                'Value': amount,
                'Number of Shares': shares,
                'NAV': nav,
                'USD Equivalent': usd_equivalent,
                'Comments': '',
                'FX rate': fx_rate
            }
            
            data_rows.append(row)
    
    # Create DataFrame
    fund_admin_df = pd.DataFrame(data_rows)
    
    # Save to Excel
    fund_admin_df.to_excel('data/fund_admin_updates/sample_fund_admin.xlsx', index=False)
    print(f"Created sample fund admin data with {len(data_rows)} entries")
    
    return fund_admin_df

def create_additional_sheets():
    """Create an investor info sheet with additional data for lookups"""
    investors = generate_investor_list(25)  # Generate some extra investors
    
    # Create main investor info dataframe
    investor_info = []
    for investor in investors:
        row = {
            'Unique ID': investor['unique_id'],
            'Investor name': investor['investor_name'],
            'Short name': investor['investor_short_name'],
            'Domicile': investor['location'],
            'Founder': random.choice(['Blackstone', 'Partners', 'N/A']),
            'ERISA': random.choice(['Yes', 'No']),
            'Created Date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%d/%m/%Y')
        }
        investor_info.append(row)
    
    # Create DataFrame
    investor_info_df = pd.DataFrame(investor_info)
    
    # Save to Excel with multiple sheets
    with pd.ExcelWriter('data/fund_admin_updates/investor_info.xlsx') as writer:
        investor_info_df.to_excel(writer, sheet_name='Investor Info', index=False)
        
        # Create a contact info sheet
        contact_info = []
        for investor in investors:
            for i in range(random.randint(1, 3)):  # 1-3 contacts per investor
                contact = {
                    'Unique ID': investor['unique_id'],
                    'Contact Name': f"Contact {i} for {investor['investor_short_name']}",
                    'Email': f"contact{i}@{investor['investor_short_name'].lower().replace(' ', '')}.com",
                    'Phone': f"+1 555 {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    'Primary': 'Yes' if i == 0 else 'No'
                }
                contact_info.append(contact)
        
        contact_info_df = pd.DataFrame(contact_info)
        contact_info_df.to_excel(writer, sheet_name='Contact Info', index=False)
    
    print(f"Created investor info sheet with {len(investor_info)} investors and {len(contact_info)} contacts")

if __name__ == "__main__":
    print("Generating sample data files...")
    
    # Create internal tracker
    internal_df = create_internal_tracker()
    
    # Create fund admin data
    fund_admin_df = create_fund_admin_data()
    
    # Create additional reference sheets
    create_additional_sheets()
    
    print("Sample data creation complete!") 