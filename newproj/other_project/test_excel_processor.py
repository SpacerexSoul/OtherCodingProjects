import unittest
import pandas as pd
import os
import shutil
from excel_processor import ExcelProcessor

class TestExcelProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.processor = ExcelProcessor()
        
        # Create test data directories
        self.test_dirs = [
            self.processor.old_sheet_dir,
            self.processor.unprocessed_dir,
            self.processor.processed_dir
        ]
        for directory in self.test_dirs:
            os.makedirs(directory, exist_ok=True)

        # Create sample old sheet
        self.old_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Investment Amount': [10000, 20000],
            'Date': ['2024-01-01', '2024-01-02'],
            'Status': ['Active', 'Active']
        })
        self.old_sheet_path = os.path.join(self.processor.old_sheet_dir, 'old_sheet.xlsx')
        self.old_data.to_excel(self.old_sheet_path, index=False)

    def tearDown(self):
        """Clean up test environment after each test."""
        for directory in self.test_dirs:
            shutil.rmtree(directory, ignore_errors=True)

    def test_column_validation_success(self):
        """Test successful column validation with matching columns."""
        new_data = pd.DataFrame({
            'name': ['Alice Brown'],  # Testing case insensitive
            'investment amount': [30000],  # Testing space insensitive
            'date': ['2024-01-03']
        })
        is_valid, message = self.processor.validate_columns(self.old_data, new_data)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Column validation successful")

    def test_column_validation_subset(self):
        """Test successful column validation with subset of columns."""
        new_data = pd.DataFrame({
            'Name': ['Alice Brown'],
            'Investment Amount': [30000]
        })
        is_valid, message = self.processor.validate_columns(self.old_data, new_data)
        self.assertTrue(is_valid)

    def test_column_validation_failure(self):
        """Test column validation failure with invalid columns."""
        new_data = pd.DataFrame({
            'Name': ['Alice Brown'],
            'Invalid Column': [30000]
        })
        is_valid, message = self.processor.validate_columns(self.old_data, new_data)
        self.assertFalse(is_valid)
        self.assertTrue("invalid column" in message.lower())

    def test_duplicate_detection(self):
        """Test duplicate detection in data."""
        # Create new data with a duplicate entry
        new_data = pd.DataFrame({
            'Name': ['John Doe'],
            'Investment Amount': [10000],
            'Date': ['2024-01-01']
        })
        has_no_duplicates = self.processor.check_for_duplicates(self.old_data, new_data)
        self.assertFalse(has_no_duplicates)

    def test_successful_processing(self):
        """Test successful processing of new data."""
        # Create new data file
        new_data = pd.DataFrame({
            'Name': ['Alice Brown'],
            'Investment Amount': [30000],
            'Date': ['2024-01-03']
        })
        new_file_path = os.path.join(self.processor.unprocessed_dir, 'new_data.xlsx')
        new_data.to_excel(new_file_path, index=False)

        # Process in test mode
        results = self.processor.process_all_files(test_mode=True)
        self.assertEqual(len(results), 1)
        
        filename, success, message, processed_df = results[0]
        self.assertTrue(success)
        self.assertEqual(len(processed_df), 3)  # Original 2 rows + 1 new row

    def test_missing_columns_handling(self):
        """Test handling of missing columns in new data."""
        # Create new data with missing columns
        new_data = pd.DataFrame({
            'Name': ['Alice Brown'],
            'Investment Amount': [30000]
        })
        new_file_path = os.path.join(self.processor.unprocessed_dir, 'new_data.xlsx')
        new_data.to_excel(new_file_path, index=False)

        # Process in test mode
        results = self.processor.process_all_files(test_mode=True)
        filename, success, message, processed_df = results[0]
        
        self.assertTrue(success)
        self.assertTrue('Date' in processed_df.columns)
        self.assertTrue('Status' in processed_df.columns)
        self.assertTrue(pd.isna(processed_df.iloc[-1]['Date']))

if __name__ == '__main__':
    unittest.main() 