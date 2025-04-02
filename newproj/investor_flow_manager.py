import pandas as pd
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class InvestorFlowManager:
    def __init__(self, config=None):
        """
        Initialize the flow manager with configuration.
        
        Args:
            config (dict, optional): Configuration dictionary with paths and settings.
        """
        # Default configuration
        self.config = {
            'internal_tracker_path': 'data/internal_tracker/investor_flows.xlsx',
            'fund_admin_folder': 'data/fund_admin_updates',
            'reports_folder': 'data/reports',
            'processed_admin_folder': 'data/fund_admin_updates/processed',
            
            # Direct column mappings between internal tracker and fund admin sheet
            'column_mappings': {
                # Maps from internal tracker column to fund admin column
                'Investor Name': 'Investor name',  # May be in investor info sheet
                'Investor Short Name': 'Short name',  # May be in investor info sheet
                'Unique ID': 'Unique ID',
                'HID': 'ID',
                'Feeder Fund': 'Feeder',
                'Share Class': 'Class',
                'New/Existing': 'New or Existing Investor',
                'Sub/Trans/Red': 'Transaction Type',
                'Dealing Date': 'Date',
                'Amount': 'Amount',
                'USD Equivalent': 'USD Equivalent',
                'Currency': 'Currency',
                'Exchange Rate': 'FX rate'
            },
            
            # Required columns for core functionality
            'required_columns': {
                'internal': [
                    'Unique ID',         # Primary identifier
                    'Investor Name',     # Investor name
                    'Amount',            # Transaction amount
                    'Dealing Date',      # Transaction date
                    'Sub/Trans/Red',     # Transaction type
                    'Feeder Fund'        # Fund type
                ],
                'fund_admin': [
                    'Unique ID',         # Primary identifier
                    'Date',              # Transaction date
                    'Transaction Type',  # Transaction type
                    'Amount',            # Transaction amount
                    'Feeder'             # Fund type
                ]
            },
            
            # Inflow/outflow identification
            'transaction_types': {
                'inflow': [
                    'subscription', 'additional subscription', 'transfer in', 'exchange in', 
                    'related movement in', 'deposit', 'contribution', 'capital call'
                ],
                'outflow': [
                    'redemption', 'transfer out', 'exchange out', 'withdrawal', 
                    'distribution', 'related movement out'
                ]
            }
        }
        
        # Override defaults with provided config
        if config:
            self.config.update(config)
            
        # Ensure directories exist
        for folder in [
            os.path.dirname(self.config['internal_tracker_path']),
            self.config['fund_admin_folder'],
            self.config['reports_folder'],
            self.config['processed_admin_folder']
        ]:
            os.makedirs(folder, exist_ok=True)
            
        # Create internal tracker if it doesn't exist
        if not os.path.exists(self.config['internal_tracker_path']):
            self._create_empty_tracker()
    
    def _create_empty_tracker(self):
        """Create an empty internal tracker with required columns."""
        # Create a minimal structure with core columns
        empty_df = pd.DataFrame(columns=[
            'Unique ID',
            'Investor Name',
            'Investor Short Name',
            'Feeder Fund',
            'Share Class',
            'Sub/Trans/Red',
            'Dealing Date',
            'Amount',
            'USD Equivalent',
            'Currency',
            'Exchange Rate',
            'is_forecast'  # Internal flag for forecast vs actual
        ])
        
        empty_df.to_excel(self.config['internal_tracker_path'], index=False)
        print(f"Created new internal tracker at {self.config['internal_tracker_path']}")
    
    def get_internal_columns(self):
        """Get the list of columns in the internal tracker."""
        if os.path.exists(self.config['internal_tracker_path']):
            df = pd.read_excel(self.config['internal_tracker_path'])
            return list(df.columns)
        return []
    
    def get_fund_admin_columns(self, file_path=None):
        """
        Get the list of columns from a fund admin file.
        
        Args:
            file_path: Path to a specific fund admin file. If None, will look for the first file available.
            
        Returns:
            List of column names, or empty list if no file found
        """
        if file_path and os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return list(df.columns)
        
        # Try to find a fund admin file
        files = glob.glob(os.path.join(self.config['fund_admin_folder'], '*.xlsx'))
        if files:
            for file in files:
                if 'processed' not in file and 'mapped' not in file:
                    df = pd.read_excel(file)
                    return list(df.columns)
        
        return []
    
    def get_column_mappings(self):
        """Get the current column mappings."""
        return self.config['column_mappings']
    
    def update_column_mappings(self, mappings):
        """
        Update column mappings.
        
        Args:
            mappings: Dict mapping internal tracker columns to fund admin columns
        """
        self.config['column_mappings'] = mappings
        return {'success': True, 'message': 'Column mappings updated successfully'}
        
    def process_new_fund_admin_files(self):
        """
        Automatically process any new fund admin files found in the fund admin folder.
        Returns a summary of actions taken.
        """
        results = []
        
        # Find unprocessed Excel files in fund admin folder (exclude processed subfolder)
        unprocessed_files = []
        for file in glob.glob(os.path.join(self.config['fund_admin_folder'], '*.xlsx')):
            if 'processed' not in file and 'mapped_' not in file:  # Skip processed and mapped files
                unprocessed_files.append(file)
        
        print(f"Found {len(unprocessed_files)} unprocessed fund admin files")
        
        # Process each file
        for file_path in unprocessed_files:
            file_name = os.path.basename(file_path)
            result = self.update_from_fund_admin(file_path)
            
            if result['success']:
                # Move to processed folder after successful processing
                processed_path = os.path.join(self.config['processed_admin_folder'], file_name)
                os.rename(file_path, processed_path)
                result['file_moved_to'] = processed_path
            
            results.append(result)
            
        return results
    
    def _is_inflow(self, transaction_type):
        """
        Check if a transaction type represents an inflow.
        
        Args:
            transaction_type: String representing the transaction type
        
        Returns:
            Boolean indicating if it's an inflow
        """
        if not transaction_type:
            return False
            
        transaction_type = str(transaction_type).lower()
        
        for inflow_type in self.config['transaction_types']['inflow']:
            if inflow_type in transaction_type:
                return True
                
        return False
    
    def _is_outflow(self, transaction_type):
        """
        Check if a transaction type represents an outflow.
        
        Args:
            transaction_type: String representing the transaction type
        
        Returns:
            Boolean indicating if it's an outflow
        """
        if not transaction_type:
            return False
            
        transaction_type = str(transaction_type).lower()
        
        for outflow_type in self.config['transaction_types']['outflow']:
            if outflow_type in transaction_type:
                return True
                
        return False
    
    def update_from_fund_admin(self, fund_admin_file):
        """
        Update internal tracker with new fund admin data.
        Preserves existing forecasts while updating historical data.
        
        Returns dict with results and statistics.
        """
        result = {
            'file': fund_admin_file,
            'success': False,
            'message': '',
            'stats': {}
        }
        
        try:
            # Read files
            fund_admin = pd.read_excel(fund_admin_file)
            internal_tracker = pd.read_excel(self.config['internal_tracker_path'])
            
            # Initialize statistics
            stats = {
                'new_entries': 0,
                'total_records': 0,
                'inflow_amount': 0,
                'outflow_amount': 0,
                'net_flow': 0
            }
            
            # Validate fund admin contains required columns
            required_fund_admin = self.config['required_columns']['fund_admin']
            missing_columns = [col for col in required_fund_admin if col not in fund_admin.columns]
            
            if missing_columns:
                result['message'] = f"Fund admin file missing required columns: {missing_columns}"
                result['missing_columns'] = missing_columns
                return result
            
            # Get column mappings (fund admin -> internal)
            mappings = {v: k for k, v in self.config['column_mappings'].items()}
            
            # Process fund admin entries
            new_entries = []
            
            for _, row in fund_admin.iterrows():
                # Check if this record already exists in the internal tracker
                unique_id = row['Unique ID']
                transaction_date = pd.to_datetime(row['Date'], dayfirst=True)  # Assuming DD/MM/YYYY format
                transaction_type = row['Transaction Type']
                amount = row['Amount']
                
                # Skip if not a standard transaction type
                if not (self._is_inflow(transaction_type) or self._is_outflow(transaction_type)):
                    continue
                
                # Convert transaction type to standardized inflow/outflow
                if self._is_inflow(transaction_type):
                    flow_direction = 'inflow'
                elif self._is_outflow(transaction_type):
                    flow_direction = 'outflow'
                else:
                    flow_direction = 'unknown'
                
                # Check if this transaction already exists in internal tracker
                # (same ID, date, type, and amount)
                exists = False
                
                if not internal_tracker.empty:
                    # Ensure date columns are datetime
                    internal_tracker['Dealing Date'] = pd.to_datetime(internal_tracker['Dealing Date'], 
                                                                   errors='coerce')
                    
                    # Filter for potential matches
                    matches = internal_tracker[
                        (internal_tracker['Unique ID'] == unique_id) & 
                        (internal_tracker['Dealing Date'].dt.date == transaction_date.date()) &
                        (internal_tracker['Amount'] == amount)
                    ]
                    
                    if not matches.empty:
                        exists = True
                
                # Skip if already in the internal tracker
                if exists:
                    continue
                
                # Create new entry with mapped columns
                new_entry = {}
                
                # Add standard tracking columns
                new_entry['Unique ID'] = unique_id
                new_entry['Dealing Date'] = transaction_date
                new_entry['Amount'] = amount
                new_entry['Sub/Trans/Red'] = transaction_type
                new_entry['is_forecast'] = False  # Mark as actual data
                
                # Map values from fund admin to internal tracker for remaining columns
                for fund_col, internal_col in mappings.items():
                    if fund_col in fund_admin.columns and fund_col not in ['Unique ID', 'Date', 'Amount', 'Transaction Type']:
                        new_entry[internal_col] = row[fund_col]
                
                # Add to new entries list
                new_entries.append(new_entry)
                
                # Update statistics
                if flow_direction == 'inflow':
                    stats['inflow_amount'] += amount
                elif flow_direction == 'outflow':
                    stats['outflow_amount'] += amount
            
            # If we have new entries, update the internal tracker
            if new_entries:
                # Create DataFrame from new entries
                new_entries_df = pd.DataFrame(new_entries)
                
                # Split internal tracker into forecasts and actuals
                forecasts = internal_tracker[internal_tracker.get('is_forecast', False)].copy() if not internal_tracker.empty else pd.DataFrame()
                actuals = internal_tracker[~internal_tracker.get('is_forecast', False)].copy() if not internal_tracker.empty else pd.DataFrame()
                
                # Combine actuals with new entries
                if actuals.empty:
                    combined_actuals = new_entries_df
                else:
                    # Ensure columns are the same by adding missing columns
                    for col in actuals.columns:
                        if col not in new_entries_df.columns:
                            new_entries_df[col] = None
                    
                    for col in new_entries_df.columns:
                        if col not in actuals.columns:
                            actuals[col] = None
                    
                    # Concatenate
                    combined_actuals = pd.concat([actuals, new_entries_df], ignore_index=True)
                
                # Combine actuals with forecasts
                if forecasts.empty:
                    updated_tracker = combined_actuals
                else:
                    # Ensure columns are the same
                    for col in combined_actuals.columns:
                        if col not in forecasts.columns:
                            forecasts[col] = None
                            
                    for col in forecasts.columns:
                        if col not in combined_actuals.columns:
                            combined_actuals[col] = None
                    
                    # Concatenate
                    updated_tracker = pd.concat([combined_actuals, forecasts], ignore_index=True)
                
                # Sort by date
                if 'Dealing Date' in updated_tracker.columns:
                    updated_tracker['Dealing Date'] = pd.to_datetime(updated_tracker['Dealing Date'], errors='coerce')
                    updated_tracker = updated_tracker.sort_values('Dealing Date')
                
                # Save updated tracker
                updated_tracker.to_excel(self.config['internal_tracker_path'], index=False)
                
                # Update statistics
                stats['new_entries'] = len(new_entries)
                stats['total_records'] = len(updated_tracker)
                stats['net_flow'] = stats['inflow_amount'] - stats['outflow_amount']
                
                result['success'] = True
                result['message'] = f"Successfully updated tracker with {len(new_entries)} new entries"
                result['stats'] = stats
                
                # Generate reports
                self.generate_reports()
                
                return result
            else:
                result['success'] = True
                result['message'] = "No new entries found in fund admin file"
                result['stats'] = stats
                return result
            
        except Exception as e:
            result['message'] = f"Error updating tracker: {str(e)}"
            return result
    
    def add_forecast(self, forecast_data):
        """
        Add a new forecast entry to the internal tracker.
        
        forecast_data should contain required internal tracker fields.
        
        Returns dict with results.
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Read current tracker
            internal_tracker = pd.read_excel(self.config['internal_tracker_path'])
            
            # Validate required fields
            required_fields = set(self.config['required_columns']['internal'])
            missing_fields = required_fields - set(forecast_data.keys())
            
            if missing_fields:
                result['message'] = f"Missing required fields: {missing_fields}"
                return result
            
            # Check if transaction type is valid
            transaction_type = forecast_data.get('Sub/Trans/Red', '').lower()
            if not (self._is_inflow(transaction_type) or self._is_outflow(transaction_type)):
                result['message'] = f"Invalid transaction type: {transaction_type}. Must be inflow or outflow."
                return result
            
            # Mark as forecast
            forecast_data['is_forecast'] = True
            
            # Create new DataFrame for the forecast
            new_forecast = pd.DataFrame([forecast_data])
            
            # Add to internal tracker
            if internal_tracker.empty:
                updated_tracker = new_forecast
            else:
                # Ensure columns match
                for col in internal_tracker.columns:
                    if col not in new_forecast.columns:
                        new_forecast[col] = None
                
                for col in new_forecast.columns:
                    if col not in internal_tracker.columns:
                        internal_tracker[col] = None
                
                updated_tracker = pd.concat([internal_tracker, new_forecast], ignore_index=True)
            
            # Ensure date is correct format
            if 'Dealing Date' in updated_tracker.columns:
                updated_tracker['Dealing Date'] = pd.to_datetime(updated_tracker['Dealing Date'], errors='coerce')
                updated_tracker = updated_tracker.sort_values('Dealing Date')
            
            # Save updated tracker
            updated_tracker.to_excel(self.config['internal_tracker_path'], index=False)
            
            result['success'] = True
            result['message'] = "Successfully added forecast"
            
            # Regenerate reports
            self.generate_reports()
            
            return result
            
        except Exception as e:
            result['message'] = f"Error adding forecast: {str(e)}"
            return result
    
    def generate_reports(self):
        """Generate summary reports from the current data."""
        try:
            # Read current tracker
            internal_tracker = pd.read_excel(self.config['internal_tracker_path'])
            
            if internal_tracker.empty:
                print("No data available for reporting")
                return
            
            # Ensure date is datetime
            if 'Dealing Date' in internal_tracker.columns:
                internal_tracker['Dealing Date'] = pd.to_datetime(internal_tracker['Dealing Date'], errors='coerce')
            
            # Create summary report
            summary_report = self._create_summary_report(internal_tracker)
            summary_path = os.path.join(self.config['reports_folder'], 'summary_report.xlsx')
            summary_report.to_excel(summary_path, index=True)
            
            # Create charts
            self._create_charts(internal_tracker)
            
            print(f"Reports generated successfully in {self.config['reports_folder']}")
            
        except Exception as e:
            print(f"Error generating reports: {str(e)}")
    
    def _create_summary_report(self, data):
        """Create a summary report from the tracker data."""
        # Handle empty data
        if data.empty:
            return pd.DataFrame()
            
        # Ensure required columns exist
        required_cols = ['Unique ID', 'Investor Name', 'Amount', 'Sub/Trans/Red', 'is_forecast']
        missing_cols = set(required_cols) - set(data.columns)
        if missing_cols:
            print(f"Warning: Missing required columns for reporting: {missing_cols}")
            # Create empty columns for missing ones
            for col in missing_cols:
                data[col] = None
        
        # Split into actuals and forecasts
        actuals = data[~data['is_forecast']].copy()
        forecasts = data[data['is_forecast']].copy()
        
        # Add year and month columns if date is available
        if 'Dealing Date' in data.columns:
            for df in [actuals, forecasts]:
                if not df.empty:
                    df['year'] = df['Dealing Date'].dt.year
                    df['month'] = df['Dealing Date'].dt.month
                    df['month_name'] = df['Dealing Date'].dt.strftime('%b')
        
        # Summary by investor
        investor_summary = pd.DataFrame()
        
        # Actual flows by investor
        if not actuals.empty:
            inflow_mask = actuals['Sub/Trans/Red'].apply(lambda x: self._is_inflow(x))
            outflow_mask = actuals['Sub/Trans/Red'].apply(lambda x: self._is_outflow(x))
            
            actual_inflows = actuals[inflow_mask].groupby('Investor Name')['Amount'].sum()
            actual_outflows = actuals[outflow_mask].groupby('Investor Name')['Amount'].sum()
            
            if not actual_inflows.empty:
                investor_summary['actual_inflows'] = actual_inflows
            else:
                investor_summary['actual_inflows'] = 0
                
            if not actual_outflows.empty:
                investor_summary['actual_outflows'] = actual_outflows
            else:
                investor_summary['actual_outflows'] = 0
        else:
            investor_summary['actual_inflows'] = 0
            investor_summary['actual_outflows'] = 0
        
        # Forecast flows by investor
        if not forecasts.empty:
            inflow_mask = forecasts['Sub/Trans/Red'].apply(lambda x: self._is_inflow(x))
            outflow_mask = forecasts['Sub/Trans/Red'].apply(lambda x: self._is_outflow(x))
            
            forecast_inflows = forecasts[inflow_mask].groupby('Investor Name')['Amount'].sum()
            forecast_outflows = forecasts[outflow_mask].groupby('Investor Name')['Amount'].sum()
            
            # Add to summary
            if not forecast_inflows.empty:
                for investor in forecast_inflows.index:
                    if investor not in investor_summary.index:
                        investor_summary.loc[investor] = 0
                    investor_summary.loc[investor, 'forecast_inflows'] = forecast_inflows[investor]
            
            if not forecast_outflows.empty:
                for investor in forecast_outflows.index:
                    if investor not in investor_summary.index:
                        investor_summary.loc[investor] = 0
                    investor_summary.loc[investor, 'forecast_outflows'] = forecast_outflows[investor]
        
        # Ensure all columns exist
        for col in ['actual_inflows', 'actual_outflows', 'forecast_inflows', 'forecast_outflows']:
            if col not in investor_summary.columns:
                investor_summary[col] = 0
        
        # Fill NAs with 0
        investor_summary.fillna(0, inplace=True)
        
        # Calculate net flows
        investor_summary['actual_net'] = investor_summary['actual_inflows'] - investor_summary['actual_outflows']
        investor_summary['forecast_net'] = investor_summary['forecast_inflows'] - investor_summary['forecast_outflows']
        investor_summary['total_net'] = investor_summary['actual_net'] + investor_summary['forecast_net']
        
        # Sort by total net flow
        investor_summary = investor_summary.sort_values('total_net', ascending=False)
        
        # Add totals row
        investor_summary.loc['TOTAL'] = investor_summary.sum()
        
        return investor_summary
    
    def _create_charts(self, data):
        """Create visualization charts from the tracker data."""
        # Handle empty data
        if data.empty:
            return
            
        # Ensure required columns exist
        required_cols = ['Unique ID', 'Investor Name', 'Amount', 'Sub/Trans/Red', 'is_forecast', 'Dealing Date']
        missing_cols = set(required_cols) - set(data.columns)
        if missing_cols:
            print(f"Warning: Missing required columns for charts: {missing_cols}")
            return
        
        # Split into actuals and forecasts
        actuals = data[~data['is_forecast']].copy()
        forecasts = data[data['is_forecast']].copy()
        
        # 1. Monthly flow chart (actual and forecast)
        plt.figure(figsize=(12, 6))
        
        # Prepare monthly data
        monthly_data = {'actuals': {}, 'forecasts': {}}
        
        # Handle actuals
        if not actuals.empty:
            actuals['yearmonth'] = actuals['Dealing Date'].dt.strftime('%Y-%m')
            
            inflow_mask = actuals['Sub/Trans/Red'].apply(lambda x: self._is_inflow(x))
            outflow_mask = actuals['Sub/Trans/Red'].apply(lambda x: self._is_outflow(x))
            
            inflows = actuals[inflow_mask].groupby('yearmonth')['Amount'].sum()
            outflows = actuals[outflow_mask].groupby('yearmonth')['Amount'].sum()
            
            for month in inflows.index:
                monthly_data['actuals'][month] = monthly_data['actuals'].get(month, 0) + inflows[month]
            
            for month in outflows.index:
                monthly_data['actuals'][month] = monthly_data['actuals'].get(month, 0) - outflows[month]
        
        # Handle forecasts
        if not forecasts.empty:
            forecasts['yearmonth'] = forecasts['Dealing Date'].dt.strftime('%Y-%m')
            
            inflow_mask = forecasts['Sub/Trans/Red'].apply(lambda x: self._is_inflow(x))
            outflow_mask = forecasts['Sub/Trans/Red'].apply(lambda x: self._is_outflow(x))
            
            inflows = forecasts[inflow_mask].groupby('yearmonth')['Amount'].sum()
            outflows = forecasts[outflow_mask].groupby('yearmonth')['Amount'].sum()
            
            for month in inflows.index:
                monthly_data['forecasts'][month] = monthly_data['forecasts'].get(month, 0) + inflows[month]
            
            for month in outflows.index:
                monthly_data['forecasts'][month] = monthly_data['forecasts'].get(month, 0) - outflows[month]
        
        # Combine and sort all months
        all_months = set(monthly_data['actuals'].keys()) | set(monthly_data['forecasts'].keys())
        all_months = sorted(all_months)
        
        # Prepare chart data
        actual_values = [monthly_data['actuals'].get(month, 0) for month in all_months]
        forecast_values = [monthly_data['forecasts'].get(month, 0) for month in all_months]
        
        # Plot the data
        plt.bar(all_months, actual_values, color='blue', alpha=0.7, label='Actual Net Flow')
        plt.bar(all_months, forecast_values, color='orange', alpha=0.7, label='Forecast Net Flow')
        
        plt.title('Monthly Net Fund Flows (Actual vs Forecast)')
        plt.xlabel('Month')
        plt.ylabel('Net Flow Amount')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(os.path.join(self.config['reports_folder'], 'monthly_flows.png'))
        
        # 2. Investor breakdown chart
        plt.figure(figsize=(12, 8))
        
        # Get investor summary
        investor_summary = self._create_summary_report(data)
        
        if 'TOTAL' in investor_summary.index:
            investor_summary = investor_summary.drop('TOTAL')  # Remove total row for the chart
        
        # Sort by total net flow
        investor_summary = investor_summary.sort_values('total_net')
        
        # Plot the data
        investors = investor_summary.index
        y_pos = np.arange(len(investors))
        
        plt.barh(y_pos, investor_summary['actual_net'], label='Actual Net Flow', color='blue', alpha=0.7)
        plt.barh(y_pos, investor_summary['forecast_net'], left=investor_summary['actual_net'], 
                label='Forecast Net Flow', color='orange', alpha=0.7)
        
        plt.yticks(y_pos, investors)
        plt.xlabel('Net Flow Amount')
        plt.title('Net Fund Flow by Investor (Actual + Forecast)')
        plt.legend()
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(os.path.join(self.config['reports_folder'], 'investor_flows.png'))
        
        plt.close('all')  # Close all figures

def main():
    """Main function to run the investor flow manager interactively."""
    manager = InvestorFlowManager()
    
    print("\nInvestor Flow Manager")
    print("=" * 50)
    
    # Process any new fund admin files automatically
    print("\nChecking for new fund admin files...")
    results = manager.process_new_fund_admin_files()
    
    if results:
        print("\nProcessed files:")
        for result in results:
            status = "✅ Success" if result['success'] else "❌ Failed"
            print(f"- {os.path.basename(result['file'])}: {status}")
            if result['success']:
                print(f"  Added {result['stats']['new_entries']} new transactions")
                print(f"  Net flow: ${result['stats']['net_flow']:,.2f}")
    else:
        print("No new files to process")

    # Option to add forecasts
    add_forecast = input("\nWould you like to add a forecast? (y/n): ").strip().lower() == 'y'
    
    while add_forecast:
        forecast_data = {}
        try:
            forecast_data = {
                'Unique ID': input("\nUnique ID: "),
                'Investor Name': input("Investor Name: "),
                'Feeder Fund': input("Feeder Fund: "),
                'Amount': float(input("Amount: ")),
                'Dealing Date': input("Date (DD/MM/YYYY): "),
                'Sub/Trans/Red': input("Transaction Type: "),
                'Share Class': input("Share Class (optional): ")
            }
            
            result = manager.add_forecast(forecast_data)
            print(f"\nForecast Addition: {'✅ Success' if result['success'] else '❌ Failed'}")
            print(f"Message: {result['message']}")
            
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
        
        add_forecast = input("\nAdd another forecast? (y/n): ").strip().lower() == 'y'
    
    # Generate reports
    print("\nGenerating reports...")
    manager.generate_reports()
    
    print("\nDone! You can find reports in the data/reports folder.")

if __name__ == "__main__":
    main() 