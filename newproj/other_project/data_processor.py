import pandas as pd
import os
from datetime import datetime, timedelta
import shutil
from typing import Tuple, Dict
from enhanced_processor import EnhancedExcelProcessor

class DataSeparator:
    def __init__(self):
        self.base_dir = "data"
        self.fund_admin_dir = os.path.join(self.base_dir, "fund_admin")
        self.internal_tracker_dir = os.path.join(self.base_dir, "internal_tracker")
        
        # Ensure directories exist
        for directory in [
            os.path.join(self.fund_admin_dir, "historical"),
            os.path.join(self.internal_tracker_dir, "historical"),
            os.path.join(self.internal_tracker_dir, "forecasts")
        ]:
            os.makedirs(directory, exist_ok=True)

    def process_fund_admin_sheet(self, file_path: str) -> Tuple[bool, str]:
        """
        Process the fund admin sheet which comes every 15th.
        This contains the official record of actual flows.
        """
        try:
            # Read the fund admin sheet
            df = pd.read_excel(file_path)
            
            # Normalize column names
            df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
            
            # Validate required columns
            required_cols = {
                'investor_id',
                'investor_name',
                'fund_type',
                'investment_amount',
                'transaction_date',
                'transaction_type'
            }
            
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                return False, f"Missing required columns in fund admin sheet: {missing_cols}"
            
            # Ensure dates are in datetime format
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            
            # Save to historical folder with timestamp
            timestamp = datetime.now().strftime('%Y%m%d')
            output_path = os.path.join(
                self.fund_admin_dir,
                "historical",
                f"fund_admin_{timestamp}.xlsx"
            )
            
            df.to_excel(output_path, index=False)
            return True, f"Fund admin data processed and saved to {output_path}"
            
        except Exception as e:
            return False, f"Error processing fund admin sheet: {str(e)}"

    def process_internal_tracker(self, file_path: str) -> Tuple[bool, str]:
        """
        Process the internal tracker which contains both actuals and forecasts.
        Separates the data into historical and forecast categories.
        """
        try:
            # Read the internal tracker
            df = pd.read_excel(file_path)
            
            # Normalize column names
            df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
            
            # Validate required columns
            required_cols = {
                'investor_id',
                'investor_name',
                'fund_type',
                'expected_amount',
                'expected_date',
                'transaction_type',
                'probability',
                'status'
            }
            
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                return False, f"Missing required columns in internal tracker: {missing_cols}"
            
            # Ensure dates are in datetime format
            df['expected_date'] = pd.to_datetime(df['expected_date'])
            
            # Split into historical and forecast data
            historical_data = df[df['status'] == 'actual'].copy()
            forecast_data = df[df['status'] == 'forecast'].copy()
            
            # Save historical data
            timestamp = datetime.now().strftime('%Y%m%d')
            historical_path = os.path.join(
                self.internal_tracker_dir,
                "historical",
                f"internal_historical_{timestamp}.xlsx"
            )
            historical_data.to_excel(historical_path, index=False)
            
            # Save forecast data
            forecast_path = os.path.join(
                self.internal_tracker_dir,
                "forecasts",
                f"internal_forecast_{timestamp}.xlsx"
            )
            forecast_data.to_excel(forecast_path, index=False)
            
            return True, f"Internal tracker processed: {len(historical_data)} historical records, {len(forecast_data)} forecast records"
            
        except Exception as e:
            return False, f"Error processing internal tracker: {str(e)}"

    def validate_and_reconcile(self) -> Tuple[bool, str, Dict]:
        """
        Validate and reconcile the latest fund admin data with internal tracker data.
        """
        processor = EnhancedExcelProcessor()
        return processor.process_new_data()

def main():
    separator = DataSeparator()
    
    print("\nData Separation and Processing Tool")
    print("-" * 50)
    
    # Process fund admin sheet
    fund_admin_path = input("\nEnter path to fund admin sheet (or press Enter to skip): ").strip()
    if fund_admin_path:
        success, message = separator.process_fund_admin_sheet(fund_admin_path)
        print(f"\nFund Admin Processing: {'✅ Success' if success else '❌ Failed'}")
        print(f"Message: {message}")
    
    # Process internal tracker
    internal_tracker_path = input("\nEnter path to internal tracker sheet (or press Enter to skip): ").strip()
    if internal_tracker_path:
        success, message = separator.process_internal_tracker(internal_tracker_path)
        print(f"\nInternal Tracker Processing: {'✅ Success' if success else '❌ Failed'}")
        print(f"Message: {message}")
    
    # Run validation and reconciliation if both files were processed
    if fund_admin_path or internal_tracker_path:
        print("\nRunning validation and reconciliation...")
        success, message, report = separator.validate_and_reconcile()
        print(f"\nValidation and Reconciliation: {'✅ Success' if success else '❌ Failed'}")
        print(f"Message: {message}")
        
        if success and report:
            print("\nSummary:")
            print("-" * 50)
            print(f"Historical Net Flow: ${report['historical_summary']['net_flow']:,.2f}")
            print(f"Expected Inflows (Weighted): ${report['forecast_summary']['weighted_expected_inflows']:,.2f}")

if __name__ == "__main__":
    main() 