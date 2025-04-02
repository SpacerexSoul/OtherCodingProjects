import unittest
import pandas as pd
import os
import shutil
from datetime import datetime
from investor_flow_processor import InvestorFlowProcessor

class TestInvestorFlowProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Clean up any existing test data
        if os.path.exists('data/internal_tracker'):
            shutil.rmtree('data/internal_tracker')
        if os.path.exists('data/fund_admin_updates'):
            shutil.rmtree('data/fund_admin_updates')
            
        # Initialize processor (this will create a fresh internal tracker)
        self.processor = InvestorFlowProcessor()
        
        # Create a test fund admin file
        self.fund_admin_data = pd.DataFrame({
            'investor_id': ['INV001', 'INV002'],
            'investor_name': ['Test Investor 1', 'Test Investor 2'],
            'fund_type': ['Private Equity', 'Venture Capital'],
            'investment_amount': [1000000, 2000000],
            'transaction_date': ['2024-03-01', '2024-03-15'],
            'transaction_type': ['inflow', 'inflow']
        })
        
        # Save test fund admin file
        os.makedirs('data/fund_admin_updates', exist_ok=True)
        self.fund_admin_file = 'data/fund_admin_updates/test_fund_admin.xlsx'
        self.fund_admin_data.to_excel(self.fund_admin_file, index=False)

    def tearDown(self):
        """Clean up test files after each test."""
        if os.path.exists('data/internal_tracker'):
            shutil.rmtree('data/internal_tracker')
        if os.path.exists('data/fund_admin_updates'):
            shutil.rmtree('data/fund_admin_updates')

    def test_update_from_fund_admin(self):
        """Test updating internal tracker with fund admin data."""
        # Update tracker with fund admin data
        success, message = self.processor.update_from_fund_admin(self.fund_admin_file)
        
        # Verify update was successful
        self.assertTrue(success, f"Update failed: {message}")
        
        # Read updated tracker
        tracker = pd.read_excel(self.processor.internal_tracker_path)
        
        # Verify data was properly imported
        self.assertEqual(len(tracker), 2, "Expected 2 records in tracker")
        self.assertFalse(tracker['is_forecast'].any(), "All records should be actuals")
        
        # Verify amounts match
        total_amount = tracker['amount'].sum()
        expected_amount = self.fund_admin_data['investment_amount'].sum()
        self.assertEqual(total_amount, expected_amount, "Amounts don't match")

    def test_add_forecast(self):
        """Test adding a forecast to the tracker."""
        # First update with fund admin data
        self.processor.update_from_fund_admin(self.fund_admin_file)
        
        # Add a forecast
        forecast_data = {
            'investor_id': 'INV001',
            'investor_name': 'Test Investor 1',
            'fund_type': 'Private Equity',
            'amount': 3000000,
            'date': '2024-06-01',
            'transaction_type': 'inflow',
            'notes': 'Test forecast'
        }
        
        success, message = self.processor.add_forecast(forecast_data)
        self.assertTrue(success, f"Adding forecast failed: {message}")
        
        # Read updated tracker
        tracker = pd.read_excel(self.processor.internal_tracker_path)
        
        # Verify forecast was added
        forecasts = tracker[tracker['is_forecast']]
        self.assertEqual(len(forecasts), 1, "Expected 1 forecast")
        self.assertEqual(forecasts.iloc[0]['amount'], 3000000, "Forecast amount doesn't match")

    def test_preserve_forecasts(self):
        """Test that forecasts are preserved when updating with fund admin data."""
        # Add a forecast first
        forecast_data = {
            'investor_id': 'INV003',
            'investor_name': 'Test Investor 3',
            'fund_type': 'Real Estate',
            'amount': 5000000,
            'date': '2024-12-01',
            'transaction_type': 'inflow',
            'notes': 'Test forecast'
        }
        self.processor.add_forecast(forecast_data)
        
        # Update with fund admin data
        success, message = self.processor.update_from_fund_admin(self.fund_admin_file)
        self.assertTrue(success, f"Update failed: {message}")
        
        # Read updated tracker
        tracker = pd.read_excel(self.processor.internal_tracker_path)
        
        # Verify both actuals and forecast are present
        actuals = tracker[~tracker['is_forecast']]
        forecasts = tracker[tracker['is_forecast']]
        
        self.assertEqual(len(actuals), 2, "Expected 2 actuals")
        self.assertEqual(len(forecasts), 1, "Expected 1 forecast")
        self.assertEqual(forecasts.iloc[0]['amount'], 5000000, "Forecast amount doesn't match")

if __name__ == '__main__':
    unittest.main() 