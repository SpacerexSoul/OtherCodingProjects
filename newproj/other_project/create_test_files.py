import pandas as pd
import os

# Create sample data for old sheet
old_data = pd.DataFrame({
    'Investor Name': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis'],
    'Investment Amount': [500000, 750000, 1000000, 250000],
    'Investment Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05'],
    'Fund Type': ['Equity', 'Debt', 'Mixed', 'Equity'],
    'Status': ['Active', 'Active', 'Closed', 'Active'],
    'Contact Email': ['john@example.com', 'emma@example.com', 'michael@example.com', 'sarah@example.com'],
    'Last Updated': ['2023-12-31', '2023-12-31', '2023-12-31', '2023-12-31']
})

# Create sample data for new sheet (with some different column names and missing columns)
new_data = pd.DataFrame({
    'investor name': ['Alice Wilson', 'Robert Taylor'],  # Note: different case
    'Investment amount': [800000, 600000],  # Note: space in name
    'investment date': ['2024-01-20', '2024-02-15'],
    'Fund type': ['Equity', 'Debt'],
    'Contact email': ['alice@example.com', 'robert@example.com']
    # Note: 'Status' and 'Last Updated' columns are missing
})

# Save old sheet
old_sheet_path = os.path.join('data', 'old_sheet', 'investor_relations_current.xlsx')
old_data.to_excel(old_sheet_path, index=False)

# Save new sheet
new_sheet_path = os.path.join('data', 'unprocessed', 'new_investors_march2024.xlsx')
new_data.to_excel(new_sheet_path, index=False)

print(f"Created old sheet at: {old_sheet_path}")
print(f"Created new sheet at: {new_sheet_path}") 