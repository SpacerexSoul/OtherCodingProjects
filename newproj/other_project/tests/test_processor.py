import unittest
import pandas as pd
import os
from datetime import datetime
from test_data_generator import TestDataGenerator
from data_processor import DataSeparator

class TestDataProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test files before running tests."""
        cls.generator = TestDataGenerator()
        cls.fund_admin_file = cls.generator.generate_fund_admin_test_file("test_fund_admin.xlsx")
        cls.internal_tracker_file = cls.generator.generate_internal_tracker_test_file("test_internal_tracker.xlsx")
        cls.processor = DataSeparator()

    def setUp(self):
        """Set up test environment before each test."""
        # Clean up processed directories
        for directory in ['data/processed/fund_admin', 'data/processed/internal_tracker']:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    os.remove(os.path.join(directory, file))

    def test_fund_admin_processing(self):
        """Test processing of fund admin data."""
        # Process fund admin file
        success, message = self.processor.process_fund_admin_sheet(self.fund_admin_file)
        
        # Assert processing was successful
        self.assertTrue(success, f"Fund admin processing failed: {message}")
        
        # Check if file was created in the right location
        processed_files = os.listdir('data/processed/fund_admin')
        self.assertTrue(len(processed_files) > 0, "No processed fund admin file found")
        
        # Load processed file and verify structure
        processed_file = pd.read_excel(os.path.join('data/processed/fund_admin', processed_files[0]))
        required_columns = {
            'investor_id',
            'investor_name',
            'fund_type',
            'investment_amount',
            'transaction_date',
            'transaction_type'
        }
        self.assertTrue(all(col in processed_file.columns for col in required_columns),
                       "Processed fund admin file missing required columns")

    def test_internal_tracker_processing(self):
        """Test processing of internal tracker data."""
        # Process internal tracker file
        success, message = self.processor.process_internal_tracker(self.internal_tracker_file)
        
        # Assert processing was successful
        self.assertTrue(success, f"Internal tracker processing failed: {message}")
        
        # Check if files were created in the right locations
        processed_files = os.listdir('data/processed/internal_tracker')
        self.assertTrue(len(processed_files) > 0, "No processed internal tracker files found")
        
        # Load processed file and verify structure
        processed_file = pd.read_excel(os.path.join('data/processed/internal_tracker', processed_files[0]))
        required_columns = {
            'investor_id',
            'investor_name',
            'fund_type',
            'expected_amount',
            'expected_date',
            'transaction_type',
            'probability',
            'status'
        }
        self.assertTrue(all(col in processed_file.columns for col in required_columns),
                       "Processed internal tracker file missing required columns")

    def test_data_validation(self):
        """Test data validation and reconciliation."""
        # Process both files
        self.processor.process_fund_admin_sheet(self.fund_admin_file)
        self.processor.process_internal_tracker(self.internal_tracker_file)
        
        # Run validation
        success, message, report = self.processor.validate_and_reconcile()
        
        # Assert validation was successful
        self.assertTrue(success, f"Data validation failed: {message}")
        
        # Check report structure
        self.assertIn('historical_summary', report, "Report missing historical summary")
        self.assertIn('forecast_summary', report, "Report missing forecast summary")
        
        # Verify report contents
        historical = report['historical_summary']
        self.assertGreater(historical['total_inflows'], 0, "No inflows found in historical data")
        self.assertIsInstance(historical['by_fund_type'], dict, "Fund type breakdown missing")
        
        forecast = report['forecast_summary']
        self.assertGreater(forecast['weighted_expected_inflows'], 0, "No forecast inflows found")
        self.assertIn('by_probability_range', forecast, "Probability range breakdown missing")

    def test_data_consistency(self):
        """Test consistency between fund admin and internal tracker data."""
        # Process both files
        self.processor.process_fund_admin_sheet(self.fund_admin_file)
        self.processor.process_internal_tracker(self.internal_tracker_file)
        
        # Get processed files
        fund_admin_files = os.listdir('data/processed/fund_admin')
        internal_files = os.listdir('data/processed/internal_tracker')
        
        fund_admin_data = pd.read_excel(os.path.join('data/processed/fund_admin', fund_admin_files[0]))
        internal_data = pd.read_excel(os.path.join('data/processed/internal_tracker', internal_files[0]))
        
        # Check investor consistency
        fund_admin_investors = set(fund_admin_data['investor_id'])
        internal_investors = set(internal_data['investor_id'])
        
        # All fund admin investors should be in internal tracker
        self.assertTrue(fund_admin_investors.issubset(internal_investors),
                       "Fund admin investors not found in internal tracker")
        
        # Check date ranges
        fund_admin_dates = pd.to_datetime(fund_admin_data['transaction_date'])
        internal_dates = pd.to_datetime(internal_data['expected_date'])
        
        self.assertLess(fund_admin_dates.max(), internal_dates.max(),
                       "Internal tracker should have future dates (forecasts)")

if __name__ == '__main__':
    unittest.main() 