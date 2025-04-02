import wbgapi as wb
import pandas as pd
import pyodbc
from datetime import datetime

# Set up World Bank API
wb.economy.coder = 'id'  # Use ISO3 country codes

# List of emerging market countries
em_countries = [
    'BRA', 'MEX', 'IND', 'IDN', 'TUR', 'ZAF', 'CHN', 'ARG', 'COL',
    'THA', 'MYS', 'PHL', 'EGY', 'PAK', 'VNM', 'CHL', 'PER'
]

# Relevant World Bank indicators for bonds
indicators = {
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth',
    'FP.CPI.TOTL.ZG': 'Inflation Rate',
    'GC.DOD.TOTL.CD': 'Total Government Debt',
    'NY.GDP.PCAP.CD': 'GDP per capita',
    'BN.CAB.XOKA.CD': 'Current Account Balance'
}

try:
    print("Fetching data from World Bank API...")
    # Fetch data
    df = wb.data.DataFrame(
        list(indicators.keys()),
        em_countries,
        time=range(2020, 2024),  # Updated to use more recent available data
        labels=True,
        skipBlanks=True
    )
    
    print("Data fetched successfully. Preparing to load into SQL Server...")
    
    # Connect to SQL Server
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=HedgeFundDB;UID=SA;PWD=YourStrong@Passw0rd'
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Create MarketIndicators table if it doesn't exist
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketIndicators')
    CREATE TABLE MarketIndicators (
        IndicatorID INT IDENTITY(1,1) PRIMARY KEY,
        CountryCode VARCHAR(3),
        CountryName VARCHAR(100),
        IndicatorCode VARCHAR(50),
        IndicatorName VARCHAR(100),
        Year INT,
        Value DECIMAL(18,4)
    )
    """)
    
    # Insert data into SQL Server
    records_inserted = 0
    
    # Process the DataFrame
    for index, row in df.iterrows():
        country_code = index[0]  # First part of the index tuple is the country code
        indicator_code = index[1]  # Second part is the indicator code
        
        # Get the country name and indicator name from the row
        country_name = row['Country']
        indicator_name = row['Series']
        
        # Process each year column
        for year in range(2020, 2024):
            year_col = f'YR{year}'
            if year_col in row.index and pd.notna(row[year_col]):
                value = float(row[year_col])
                
                cursor.execute("""
                INSERT INTO MarketIndicators 
                (CountryCode, CountryName, IndicatorCode, IndicatorName, Year, Value)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (country_code, country_name, indicator_code, indicator_name, year, value))
                records_inserted += 1
    
    conn.commit()
    print(f"Data successfully loaded into SQL Server. {records_inserted} records inserted.")
    
    # Print sample of inserted data
    print("\nSample of inserted data:")
    cursor.execute("""
    SELECT TOP 5 CountryCode, CountryName, IndicatorName, Year, Value 
    FROM MarketIndicators 
    ORDER BY IndicatorID
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
except Exception as e:
    print(f"Error: {str(e)}")
    if 'df' in locals():
        print("\nDataFrame structure:")
        print(df.head())
        print("\nColumns:", df.columns.tolist())
        print("\nIndex levels:", df.index.names)
    
finally:
    if 'conn' in locals():
        conn.close()
        print("\nDatabase connection closed.") 