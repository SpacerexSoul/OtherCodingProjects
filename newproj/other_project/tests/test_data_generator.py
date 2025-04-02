import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class TestDataGenerator:
    def __init__(self):
        self.test_files_dir = "tests/test_files"
        os.makedirs(self.test_files_dir, exist_ok=True)

    def generate_fund_admin_test_file(self, filename: str, num_investors: int = 10):
        """Generate a test fund admin Excel file."""
        np.random.seed(42)
        
        # Generate dates for the past 3 months
        end_date = datetime(2024, 3, 15)  # Fund admin data as of March 15th
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create sample data
        data = []
        fund_types = ['Private Equity', 'Venture Capital', 'Real Estate', 'Hedge Fund', 'Fixed Income']
        
        for investor_id in range(1, num_investors + 1):
            # Generate 2-3 transactions per investor
            num_transactions = np.random.randint(2, 4)
            for _ in range(num_transactions):
                transaction_date = np.random.choice(dates)
                data.append({
                    'investor_id': f'INV{investor_id:03d}',
                    'investor_name': f'Test Investor {investor_id}',
                    'fund_type': np.random.choice(fund_types),
                    'investment_amount': np.random.randint(1000000, 10000000),  # $1M to $10M
                    'transaction_date': transaction_date,
                    'transaction_type': np.random.choice(['inflow', 'outflow'], p=[0.7, 0.3])
                })
        
        df = pd.DataFrame(data)
        df = df.sort_values('transaction_date')
        output_path = os.path.join(self.test_files_dir, filename)
        df.to_excel(output_path, index=False)
        return output_path

    def generate_internal_tracker_test_file(self, filename: str, num_investors: int = 15):
        """Generate a test internal tracker Excel file."""
        np.random.seed(43)
        
        # Generate dates
        current_date = datetime(2024, 3, 26)  # Current date
        historical_start = current_date - timedelta(days=90)
        historical_dates = pd.date_range(start=historical_start, end=current_date, freq='D')
        forecast_dates = pd.date_range(start=current_date + timedelta(days=1), 
                                     end=current_date + timedelta(days=365), freq='D')
        
        data = []
        fund_types = ['Private Equity', 'Venture Capital', 'Real Estate', 'Hedge Fund', 'Fixed Income']
        
        # Historical data (matching some fund admin entries)
        for investor_id in range(1, num_investors + 1):
            # Historical entries (2-3 per investor)
            num_historical = np.random.randint(2, 4)
            for _ in range(num_historical):
                expected_date = np.random.choice(historical_dates)
                data.append({
                    'investor_id': f'INV{investor_id:03d}',
                    'investor_name': f'Test Investor {investor_id}',
                    'fund_type': np.random.choice(fund_types),
                    'expected_amount': np.random.randint(1000000, 10000000),  # $1M to $10M
                    'expected_date': expected_date,
                    'transaction_type': np.random.choice(['inflow', 'outflow'], p=[0.7, 0.3]),
                    'probability': 1.0,  # Historical data has 100% probability
                    'status': 'actual',
                    'notes': 'Historical transaction'
                })
            
            # Forecast entries (1-3 per investor)
            num_forecasts = np.random.randint(1, 4)
            for _ in range(num_forecasts):
                expected_date = np.random.choice(forecast_dates)
                probability = np.random.choice([0.25, 0.5, 0.75, 0.9])
                data.append({
                    'investor_id': f'INV{investor_id:03d}',
                    'investor_name': f'Test Investor {investor_id}',
                    'fund_type': np.random.choice(fund_types),
                    'expected_amount': np.random.randint(1000000, 10000000),
                    'expected_date': expected_date,
                    'transaction_type': np.random.choice(['inflow', 'outflow'], p=[0.8, 0.2]),
                    'probability': probability,
                    'status': 'forecast',
                    'notes': f'Forecast with {probability*100}% confidence'
                })
        
        df = pd.DataFrame(data)
        df = df.sort_values('expected_date')
        output_path = os.path.join(self.test_files_dir, filename)
        df.to_excel(output_path, index=False)
        return output_path

def main():
    generator = TestDataGenerator()
    
    # Generate test files
    print("\nGenerating test files...")
    print("-" * 50)
    
    # Fund admin test file
    fund_admin_path = generator.generate_fund_admin_test_file("test_fund_admin.xlsx")
    print(f"Created fund admin test file: {fund_admin_path}")
    
    # Internal tracker test file
    internal_tracker_path = generator.generate_internal_tracker_test_file("test_internal_tracker.xlsx")
    print(f"Created internal tracker test file: {internal_tracker_path}")
    
    print("\nTest files generated successfully!")

if __name__ == "__main__":
    main() 