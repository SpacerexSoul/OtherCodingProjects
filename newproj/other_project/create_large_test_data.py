import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Helper functions
def generate_company_name():
    prefixes = ['Global', 'Tech', 'Green', 'Future', 'Smart', 'Blue', 'Red', 'Alpha', 'Beta', 'Meta']
    suffixes = ['Ventures', 'Capital', 'Investments', 'Partners', 'Fund', 'Group', 'Holdings', 'Associates']
    return f"{random.choice(prefixes)} {random.choice(suffixes)}"

def generate_email(name):
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'investment.com', 'fund.com']
    email_name = name.lower().replace(' ', '.')
    return f"{email_name}@{random.choice(domains)}"

def generate_phone():
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

def generate_investment_amount():
    # Generate amounts between $100K and $10M with some variation
    base = random.randint(100, 10000)
    return base * 1000

def generate_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

# Create large dataset
num_records = 100
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 3, 15)

# Generate investor names
first_names = ['James', 'Emma', 'Michael', 'Sophia', 'William', 'Olivia', 'Alexander', 'Isabella', 
               'Daniel', 'Ava', 'David', 'Mia', 'Joseph', 'Charlotte', 'Andrew', 'Amelia',
               'John', 'Elizabeth', 'Christopher', 'Sofia']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
              'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

# Create data
data = {
    'Investor Name': [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(num_records)],
    'Investment Amount': [generate_investment_amount() for _ in range(num_records)],
    'Investment Date': [generate_date(start_date, end_date).strftime('%Y-%m-%d') for _ in range(num_records)],
    'Fund Type': [random.choice(['Equity', 'Debt', 'Mixed', 'Real Estate', 'Venture Capital', 'Private Equity', 'Hedge Fund']) for _ in range(num_records)],
    'Contact Email': [],  # Will be generated based on names
    'Investment Region': [random.choice(['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Australia']) for _ in range(num_records)],
    'Risk Level': [random.choice(['Low', 'Medium', 'High']) for _ in range(num_records)],
    'Expected Return': [random.uniform(5, 25) for _ in range(num_records)],  # 5% to 25%
    'Investment Term (Years)': [random.choice([1, 2, 3, 5, 7, 10]) for _ in range(num_records)],
    'Company': [generate_company_name() for _ in range(num_records)],
    'Phone': [generate_phone() for _ in range(num_records)]
}

# Generate emails based on names
data['Contact Email'] = [generate_email(name) for name in data['Investor Name']]

# Create DataFrame
df = pd.DataFrame(data)

# Add some interesting calculated columns
df['Investment Category'] = df.apply(
    lambda x: 'Small' if x['Investment Amount'] < 1000000 
    else ('Medium' if x['Investment Amount'] < 5000000 else 'Large'),
    axis=1
)

# Sort by investment date
df = df.sort_values('Investment Date')

# Save to Excel
output_dir = os.path.join('data', 'unprocessed')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'large_investor_dataset_march2024.xlsx')
df.to_excel(output_file, index=False)

print(f"Created large dataset with {num_records} records at: {output_file}")

# Print some statistics
print("\nDataset Statistics:")
print("-" * 50)
print(f"Total Investment Amount: ${df['Investment Amount'].sum():,.2f}")
print("\nInvestments by Fund Type:")
print(df['Fund Type'].value_counts())
print("\nInvestments by Region:")
print(df['Investment Region'].value_counts())
print("\nAverage Investment by Risk Level:")
print(df.groupby('Risk Level')['Investment Amount'].mean().apply(lambda x: f"${x:,.2f}")) 