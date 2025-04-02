import pyodbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict

def connect_to_db():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=HedgeFundDB;UID=SA;PWD=YourStrong@Passw0rd'
    return pyodbc.connect(conn_str)

def get_existing_countries():
    conn = connect_to_db()
    df = pd.read_sql("SELECT DISTINCT CountryCode, CountryName FROM MarketIndicators", conn)
    conn.close()
    return df.to_dict('records')

def generate_bonds(countries: List[Dict], num_bonds: int = 50):
    bonds = []
    credit_ratings = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-']
    bond_types = ['Government', 'Corporate']  # Updated to match constraint
    payment_frequencies = [1, 2, 4]  # Annual, Semi-annual, Quarterly
    
    for i in range(num_bonds):
        country = random.choice(countries)
        issue_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 365*2))
        maturity_years = random.choice([3, 5, 7, 10, 15, 20, 30])
        maturity_date = issue_date + timedelta(days=365*maturity_years)
        
        # Generate ISIN: 2 chars country code + 8 digits + 2 check digits
        isin = f"{country['CountryCode']}{str(i).zfill(8)}00"
        
        # Determine bond type and issuer name
        bond_type = random.choice(bond_types)
        issuer_name = f"{country['CountryName']} Government" if bond_type == 'Government' else f"{country['CountryName']} Corp {i}"
        
        bond = {
            'ISIN': isin,
            'IssuerName': issuer_name,
            'Country': country['CountryName'],
            'Currency': 'USD' if random.random() < 0.8 else country['CountryCode'],
            'IssueDate': issue_date.strftime('%Y-%m-%d'),
            'MaturityDate': maturity_date.strftime('%Y-%m-%d'),
            'CouponRate': round(random.uniform(3, 12), 2),
            'PaymentFrequency': random.choice(payment_frequencies),
            'FaceValue': 1000,
            'IssuePrice': round(random.uniform(95, 105), 2),
            'CreditRating': random.choice(credit_ratings),
            'BondType': bond_type
        }
        bonds.append(bond)
    
    return bonds

def generate_market_data(bond_ids: List[int], start_date: datetime, end_date: datetime):
    market_data = []
    current_date = start_date
    
    while current_date <= end_date:
        for bond_id in bond_ids:
            # Generate daily price with some randomness but trending
            base_price = 100 + np.sin(current_date.toordinal() / 180.0) * 5
            price = round(base_price + random.uniform(-2, 2), 2)
            spread = round(random.uniform(100, 500), 2)  # Spread in basis points
            volume = random.randint(100000, 1000000)
            bid_ask_spread = round(random.uniform(0.1, 0.5), 2)
            
            market_data.append({
                'BondID': bond_id,
                'Date': current_date.strftime('%Y-%m-%d'),
                'Price': price,
                'Yield': round((price / 100) * random.uniform(3, 8), 2),
                'SpreadToUS': spread,
                'Volume': volume,
                'BidPrice': price - bid_ask_spread/2,
                'AskPrice': price + bid_ask_spread/2
            })
        current_date += timedelta(days=1)
    
    return market_data

def generate_trades(bond_ids: List[int], start_date: datetime, end_date: datetime, num_trades: int = 1000):
    trades = []
    counterparties = [
        'Goldman Sachs', 'JP Morgan', 'Morgan Stanley', 'Citibank', 'Deutsche Bank',
        'HSBC', 'BNP Paribas', 'Barclays', 'UBS', 'Credit Suisse'
    ]
    
    for _ in range(num_trades):
        trade_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        bond_id = random.choice(bond_ids)
        trade_type = random.choice(['BUY', 'SELL'])
        price = round(random.uniform(95, 105), 2)
        quantity = random.randint(100000, 1000000)
        
        trades.append({
            'BondID': bond_id,
            'TradeDate': trade_date.strftime('%Y-%m-%d'),
            'TradeType': trade_type,
            'Quantity': quantity,
            'Price': price,
            'TotalAmount': round(price * quantity / 100, 2),
            'CounterpartyName': random.choice(counterparties)
        })
    
    return trades

def insert_data():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        cursor.execute("DELETE FROM Trades")
        cursor.execute("DELETE FROM MarketData")
        cursor.execute("DELETE FROM Bonds")
        conn.commit()
        
        # Get existing countries from MarketIndicators
        countries = get_existing_countries()
        
        # Generate and insert bonds
        print("Generating bonds...")
        bonds = generate_bonds(countries)
        for bond in bonds:
            cursor.execute("""
                INSERT INTO Bonds (ISIN, IssuerName, Country, Currency, IssueDate, MaturityDate, 
                                 CouponRate, PaymentFrequency, FaceValue, IssuePrice, CreditRating, BondType)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (bond['ISIN'], bond['IssuerName'], bond['Country'], bond['Currency'],
                  bond['IssueDate'], bond['MaturityDate'], bond['CouponRate'],
                  bond['PaymentFrequency'], bond['FaceValue'], bond['IssuePrice'],
                  bond['CreditRating'], bond['BondType']))
        
        # Get bond IDs
        cursor.execute("SELECT BondID FROM Bonds")
        bond_ids = [row[0] for row in cursor.fetchall()]
        
        # Generate and insert market data
        print("Generating market data...")
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 3, 15)
        market_data = generate_market_data(bond_ids, start_date, end_date)
        
        batch_size = 1000
        for i in range(0, len(market_data), batch_size):
            batch = market_data[i:i+batch_size]
            for data in batch:
                cursor.execute("""
                    INSERT INTO MarketData (BondID, Date, Price, Yield, SpreadToUS, Volume, BidPrice, AskPrice)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['BondID'], data['Date'], data['Price'], data['Yield'],
                      data['SpreadToUS'], data['Volume'], data['BidPrice'], data['AskPrice']))
            conn.commit()
            print(f"Inserted {i+len(batch)} market data points...")
        
        # Generate and insert trades
        print("Generating trades...")
        trades = generate_trades(bond_ids, start_date, end_date)
        
        for trade in trades:
            cursor.execute("""
                INSERT INTO Trades (BondID, TradeDate, TradeType, Quantity, Price, TotalAmount, CounterpartyName)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (trade['BondID'], trade['TradeDate'], trade['TradeType'],
                  trade['Quantity'], trade['Price'], trade['TotalAmount'],
                  trade['CounterpartyName']))
        
        # Commit all changes
        conn.commit()
        print("Data generation completed successfully!")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM Bonds")
        num_bonds = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MarketData")
        num_market_data = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Trades")
        num_trades = cursor.fetchone()[0]
        
        print(f"\nStatistics:")
        print(f"- Number of bonds: {num_bonds}")
        print(f"- Number of market data points: {num_market_data}")
        print(f"- Number of trades: {num_trades}")
        
        # Print sample data
        print("\nSample Bonds:")
        cursor.execute("SELECT TOP 3 BondID, ISIN, IssuerName, Country, CreditRating FROM Bonds")
        for row in cursor.fetchall():
            print(row)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    insert_data() 