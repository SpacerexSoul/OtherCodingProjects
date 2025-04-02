import pandas as pd
import os
from datetime import datetime
from typing import Tuple

class InvestorFlowProcessor:
    def __init__(self):
        """Initialize the processor with necessary file paths."""
        self.internal_tracker_path = "data/internal_tracker/investor_flows.xlsx"
        
        # Ensure directory exists
        os.makedirs("data/internal_tracker", exist_ok=True)
        
        # Create internal tracker if it doesn't exist
        if not os.path.exists(self.internal_tracker_path):
            self._create_empty_tracker()

    def _create_empty_tracker(self):
        """Create an empty internal tracker with the required structure."""
        empty_df = pd.DataFrame(columns=[
            'investor_id',
            'investor_name',
            'fund_type',
            'amount',
            'date',
            'transaction_type',  # 'inflow' or 'outflow'
            'is_forecast',       # True for forecasts, False for actuals
            'notes'
        ])
        empty_df.to_excel(self.internal_tracker_path, index=False)

    def update_from_fund_admin(self, fund_admin_file: str) -> Tuple[bool, str]:
        """
        Update internal tracker with new fund admin data.
        Preserves existing forecasts while updating historical data.
        """
        try:
            # Read files
            fund_admin = pd.read_excel(fund_admin_file)
            internal_tracker = pd.read_excel(self.internal_tracker_path)
            
            # Normalize column names from fund admin
            fund_admin.columns = [col.lower().strip().replace(' ', '_') for col in fund_admin.columns]
            
            # Validate fund admin data structure
            required_columns = {
                'investor_id',
                'investor_name',
                'fund_type',
                'investment_amount',
                'transaction_date',
                'transaction_type'
            }
            
            if not all(col in fund_admin.columns for col in required_columns):
                return False, f"Fund admin file missing required columns. Needed: {required_columns}"
            
            # Split internal tracker into forecasts and actuals
            forecasts = internal_tracker[internal_tracker['is_forecast']].copy() if not internal_tracker.empty else pd.DataFrame()
            
            # Convert fund admin data to internal tracker format
            new_actuals = pd.DataFrame({
                'investor_id': fund_admin['investor_id'],
                'investor_name': fund_admin['investor_name'],
                'fund_type': fund_admin['fund_type'],
                'amount': fund_admin['investment_amount'],
                'date': pd.to_datetime(fund_admin['transaction_date']),
                'transaction_type': fund_admin['transaction_type'],
                'is_forecast': False,
                'notes': 'Updated from fund admin'
            })
            
            # Combine new actuals with existing forecasts
            if not forecasts.empty:
                updated_tracker = pd.concat([new_actuals, forecasts], ignore_index=True)
            else:
                updated_tracker = new_actuals
            
            # Sort by date
            updated_tracker = updated_tracker.sort_values('date')
            
            # Save updated tracker
            updated_tracker.to_excel(self.internal_tracker_path, index=False)
            
            # Generate summary of changes
            summary = {
                'new_actuals': len(new_actuals),
                'preserved_forecasts': len(forecasts),
                'total_records': len(updated_tracker)
            }
            
            return True, f"Successfully updated internal tracker. Summary: {summary}"
            
        except Exception as e:
            return False, f"Error updating internal tracker: {str(e)}"

    def add_forecast(self, forecast_data: dict) -> Tuple[bool, str]:
        """
        Add a new forecast entry to the internal tracker.
        
        forecast_data should contain:
        - investor_id
        - investor_name
        - fund_type
        - amount
        - date
        - transaction_type
        - notes (optional)
        """
        try:
            # Read current tracker
            internal_tracker = pd.read_excel(self.internal_tracker_path)
            
            # Validate required fields
            required_fields = {'investor_id', 'investor_name', 'fund_type', 'amount', 'date', 'transaction_type'}
            if not all(field in forecast_data for field in required_fields):
                return False, f"Missing required fields. Needed: {required_fields}"
            
            # Create new forecast entry
            new_forecast = pd.DataFrame([{
                'investor_id': forecast_data['investor_id'],
                'investor_name': forecast_data['investor_name'],
                'fund_type': forecast_data['fund_type'],
                'amount': forecast_data['amount'],
                'date': pd.to_datetime(forecast_data['date']),
                'transaction_type': forecast_data['transaction_type'],
                'is_forecast': True,
                'notes': forecast_data.get('notes', 'Manually added forecast')
            }])
            
            # Add to tracker
            if internal_tracker.empty:
                updated_tracker = new_forecast
            else:
                updated_tracker = pd.concat([internal_tracker, new_forecast], ignore_index=True)
            
            updated_tracker = updated_tracker.sort_values('date')
            
            # Save updated tracker
            updated_tracker.to_excel(self.internal_tracker_path, index=False)
            
            return True, "Successfully added forecast"
            
        except Exception as e:
            return False, f"Error adding forecast: {str(e)}"

def main():
    processor = InvestorFlowProcessor()
    
    # Example usage
    print("\nInvestor Flow Processor")
    print("-" * 50)
    
    # Process fund admin update if file provided
    fund_admin_file = input("\nEnter path to fund admin file (or press Enter to skip): ").strip()
    if fund_admin_file:
        success, message = processor.update_from_fund_admin(fund_admin_file)
        print(f"\nProcessing Result: {'✅ Success' if success else '❌ Failed'}")
        print(f"Message: {message}")
    
    # Add forecast if needed
    add_forecast = input("\nWould you like to add a forecast? (y/n): ").strip().lower()
    if add_forecast == 'y':
        forecast_data = {
            'investor_id': input("Investor ID: "),
            'investor_name': input("Investor Name: "),
            'fund_type': input("Fund Type: "),
            'amount': float(input("Amount: ")),
            'date': input("Date (YYYY-MM-DD): "),
            'transaction_type': input("Transaction Type (inflow/outflow): "),
            'notes': input("Notes (optional): ")
        }
        success, message = processor.add_forecast(forecast_data)
        print(f"\nForecast Addition: {'✅ Success' if success else '❌ Failed'}")
        print(f"Message: {message}")

if __name__ == "__main__":
    main() 