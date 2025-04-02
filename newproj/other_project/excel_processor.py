import pandas as pd
import os
from datetime import datetime
import shutil
from typing import Optional, Tuple, List, Set, Dict

class ExcelProcessor:
    def __init__(self):
        self.old_sheet_dir = "data/old_sheet"
        self.unprocessed_dir = "data/unprocessed"
        self.processed_dir = "data/processed"
        self.history_dir = "data/history"
        
        # Create directories if they don't exist
        for directory in [self.old_sheet_dir, self.unprocessed_dir, 
                         self.processed_dir, self.history_dir]:
            os.makedirs(directory, exist_ok=True)

    def normalize_column_name(self, column: str) -> str:
        """Normalize column name by removing spaces and converting to lowercase."""
        return str(column).lower().replace(' ', '')

    def get_normalized_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get mapping of normalized column names to original column names."""
        return {self.normalize_column_name(col): col for col in df.columns}

    def validate_columns(self, old_df: pd.DataFrame, new_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate that new DataFrame has the required columns.
        Returns: (is_valid: bool, message: str)
        """
        # Define required columns (case-insensitive)
        required_columns = {
            'investorname',
            'investmentamount',
            'investmentdate',
            'fundtype'
        }
        
        # Normalize column names (remove spaces and convert to lowercase)
        old_cols = {col.lower().replace(' ', '') for col in old_df.columns}
        new_cols = {col.lower().replace(' ', '') for col in new_df.columns}
        
        # Check for required columns (case-insensitive)
        missing_required = required_columns - new_cols
        if missing_required:
            # Convert back to display format for error message
            missing_display = {' '.join(col.title() for col in name.split()) for name in missing_required}
            return False, f"Missing required columns: {missing_display}"
        
        # Get common columns for duplicate checking
        common_cols = new_cols & old_cols
        if not common_cols:
            return False, "No matching columns found between old and new sheets"
        
        return True, "Column validation successful"

    def archive_current_sheet(self):
        """Move current sheet to history folder."""
        current_files = [f for f in os.listdir(self.old_sheet_dir) if f.endswith('.xlsx')]
        for file in current_files:
            src = os.path.join(self.old_sheet_dir, file)
            dst = os.path.join(self.history_dir, f"archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file}")
            shutil.move(src, dst)

    def get_latest_old_sheet(self) -> Optional[str]:
        """Get the path to the latest old sheet."""
        files = [f for f in os.listdir(self.old_sheet_dir) if f.endswith('.xlsx')]
        if not files:
            # If no file in old_sheet, check history
            history_files = [f for f in os.listdir(self.history_dir) if f.endswith('.xlsx')]
            if not history_files:
                return None
            # Get the most recent file from history
            latest_history = sorted(history_files)[-1]
            # Copy it to old_sheet
            src = os.path.join(self.history_dir, latest_history)
            dst = os.path.join(self.old_sheet_dir, latest_history.replace('archived_', ''))
            shutil.copy2(src, dst)
            return dst
        return os.path.join(self.old_sheet_dir, sorted(files)[-1])

    def get_unprocessed_files(self) -> List[str]:
        """Get list of unprocessed Excel files."""
        return [f for f in os.listdir(self.unprocessed_dir) if f.endswith('.xlsx')]

    def normalize_dataframe_columns(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Normalize DataFrame columns to match old sheet format.
        Returns: (normalized_df, column_mapping)
        """
        df = df.copy()
        column_mapping = self.get_normalized_columns(df)
        df.columns = [self.normalize_column_name(col) for col in df.columns]
        return df, column_mapping

    def check_for_duplicates(self, old_df: pd.DataFrame, new_df: pd.DataFrame) -> bool:
        """
        Check if new data contains duplicates of existing data.
        Returns True if there are NO duplicates.
        """
        # Normalize both DataFrames' columns
        old_df, _ = self.normalize_dataframe_columns(old_df)
        new_df, _ = self.normalize_dataframe_columns(new_df)

        # Get common columns for comparison (excluding optional columns)
        key_columns = ['investor name', 'investment date', 'investment amount']
        common_cols = [col for col in key_columns if col in old_df.columns and col in new_df.columns]
        
        if not common_cols:
            return True  # No common key columns to check duplicates

        # Check for duplicates in key columns
        merged = pd.merge(old_df[common_cols], new_df[common_cols], how='inner')
        return len(merged) == 0

    def process_file(self, filename: str, test_mode: bool = False) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Process a single unprocessed file.
        Returns: (success: bool, message: str, processed_df: Optional[pd.DataFrame])
        """
        try:
            # Get the latest old sheet
            old_sheet_path = self.get_latest_old_sheet()
            if not old_sheet_path:
                return False, "No existing old sheet found", None

            # Read the files
            old_df = pd.read_excel(old_sheet_path)
            new_file_path = os.path.join(self.unprocessed_dir, filename)
            new_df = pd.read_excel(new_file_path)

            # Print column names for debugging
            print(f"Old sheet columns: {list(old_df.columns)}")
            print(f"New sheet columns: {list(new_df.columns)}")

            # Validate columns
            is_valid, message = self.validate_columns(old_df, new_df)
            if not is_valid:
                return False, message, None

            # Check for duplicates
            if not self.check_for_duplicates(old_df, new_df):
                return False, "New data contains duplicates", None

            # Normalize columns in both DataFrames
            old_df, old_mapping = self.normalize_dataframe_columns(old_df)
            new_df, _ = self.normalize_dataframe_columns(new_df)

            # Ensure new_df has all columns from old_df (fill with NaN where missing)
            for col in old_df.columns:
                if col not in new_df.columns:
                    new_df[col] = pd.NA

            # Reorder columns to match old_df
            new_df = new_df[old_df.columns]

            # Combine DataFrames
            combined_df = pd.concat([old_df, new_df], ignore_index=True)

            # Restore original column names
            combined_df.columns = [old_mapping[col] for col in combined_df.columns]

            if not test_mode:
                # Archive current sheet
                self.archive_current_sheet()

                # Save the combined data as the new current sheet
                new_path = os.path.join(self.old_sheet_dir, 'investor_relations_current.xlsx')
                combined_df.to_excel(new_path, index=False)

                # Move processed file to processed directory
                processed_path = os.path.join(self.processed_dir, filename)
                shutil.move(new_file_path, processed_path)

            return True, f"Successfully processed {filename}", combined_df

        except Exception as e:
            return False, f"Error processing {filename}: {str(e)}", None

    def process_all_files(self, test_mode: bool = False) -> List[Tuple[str, bool, str, Optional[pd.DataFrame]]]:
        """
        Process all unprocessed files.
        Returns list of (filename, success, message, processed_df) tuples.
        """
        results = []
        for filename in self.get_unprocessed_files():
            success, message, df = self.process_file(filename, test_mode)
            results.append((filename, success, message, df))
        return results

def main():
    processor = ExcelProcessor()
    results = processor.process_all_files()
    
    print("\nProcessing Results:")
    print("-" * 50)
    for filename, success, message, _ in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"{filename}: {status}")
        print(f"Message: {message}")
        print("-" * 50)

if __name__ == "__main__":
    main() 