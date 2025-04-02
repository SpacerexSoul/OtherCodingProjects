import pandas as pd
import os
from datetime import datetime, timedelta
import shutil
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import numpy as np

@dataclass
class ValidationResult:
    is_valid: bool
    discrepancies: List[str]
    details: Dict[str, any]

class EnhancedExcelProcessor:
    def __init__(self):
        # Directory structure
        self.base_dir = "data"
        self.fund_admin_dir = os.path.join(self.base_dir, "fund_admin")
        self.internal_tracker_dir = os.path.join(self.base_dir, "internal_tracker")
        self.reports_dir = os.path.join(self.base_dir, "reports")
        
        # Subdirectories
        self.fund_admin_historical = os.path.join(self.fund_admin_dir, "historical")
        self.fund_admin_forecasts = os.path.join(self.fund_admin_dir, "forecasts")
        self.internal_historical = os.path.join(self.internal_tracker_dir, "historical")
        self.internal_forecasts = os.path.join(self.internal_tracker_dir, "forecasts")
        
        # Create all directories
        for directory in [self.fund_admin_historical, self.fund_admin_forecasts,
                         self.internal_historical, self.internal_forecasts,
                         self.reports_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Required columns for each type
        self.fund_admin_required_cols = {
            'investor_id',
            'investor_name',
            'fund_type',
            'investment_amount',
            'transaction_date',
            'transaction_type'  # 'inflow' or 'outflow'
        }
        
        self.internal_required_cols = {
            'investor_id',
            'investor_name',
            'fund_type',
            'expected_amount',
            'expected_date',
            'transaction_type',
            'probability',  # probability of the forecast being realized
            'status'  # 'actual' or 'forecast'
        }

    def normalize_column_name(self, column: str) -> str:
        """Normalize column names to a standard format."""
        return str(column).lower().strip().replace(' ', '_')

    def validate_fund_admin_data(self, df: pd.DataFrame) -> ValidationResult:
        """Validate fund admin data structure and content."""
        normalized_cols = {self.normalize_column_name(col) for col in df.columns}
        missing_cols = self.fund_admin_required_cols - normalized_cols
        
        discrepancies = []
        if missing_cols:
            discrepancies.append(f"Missing required columns: {missing_cols}")
        
        # Validate data types and content
        if not missing_cols:
            # Check date format
            if not pd.to_datetime(df['transaction_date'], errors='coerce').notna().all():
                discrepancies.append("Invalid date format in transaction_date column")
            
            # Check transaction types
            valid_types = {'inflow', 'outflow'}
            invalid_types = set(df['transaction_type'].unique()) - valid_types
            if invalid_types:
                discrepancies.append(f"Invalid transaction types found: {invalid_types}")
            
            # Check for negative amounts
            if (df['investment_amount'] < 0).any():
                discrepancies.append("Negative investment amounts found")
        
        return ValidationResult(
            is_valid=len(discrepancies) == 0,
            discrepancies=discrepancies,
            details={
                'total_records': len(df),
                'date_range': (df['transaction_date'].min(), df['transaction_date'].max())
                if not missing_cols else None
            }
        )

    def validate_internal_data(self, df: pd.DataFrame) -> ValidationResult:
        """Validate internal tracker data structure and content."""
        normalized_cols = {self.normalize_column_name(col) for col in df.columns}
        missing_cols = self.internal_required_cols - normalized_cols
        
        discrepancies = []
        if missing_cols:
            discrepancies.append(f"Missing required columns: {missing_cols}")
        
        # Validate data types and content
        if not missing_cols:
            # Check date format
            if not pd.to_datetime(df['expected_date'], errors='coerce').notna().all():
                discrepancies.append("Invalid date format in expected_date column")
            
            # Check probability range
            if not df['probability'].between(0, 1).all():
                discrepancies.append("Probability values must be between 0 and 1")
            
            # Check status values
            valid_status = {'actual', 'forecast'}
            invalid_status = set(df['status'].unique()) - valid_status
            if invalid_status:
                discrepancies.append(f"Invalid status values found: {invalid_status}")
        
        return ValidationResult(
            is_valid=len(discrepancies) == 0,
            discrepancies=discrepancies,
            details={
                'total_records': len(df),
                'forecast_records': len(df[df['status'] == 'forecast']) if not missing_cols else 0,
                'actual_records': len(df[df['status'] == 'actual']) if not missing_cols else 0
            }
        )

    def compare_data_sources(self, fund_admin_df: pd.DataFrame, internal_df: pd.DataFrame) -> ValidationResult:
        """Compare fund admin and internal tracker data for discrepancies."""
        discrepancies = []
        
        # Filter actual transactions from internal tracker
        internal_actuals = internal_df[internal_df['status'] == 'actual'].copy()
        
        # Normalize dates for comparison
        fund_admin_df['transaction_date'] = pd.to_datetime(fund_admin_df['transaction_date'])
        internal_actuals['expected_date'] = pd.to_datetime(internal_actuals['expected_date'])
        
        # Compare total amounts by investor
        fund_admin_totals = fund_admin_df.groupby('investor_id')['investment_amount'].sum()
        internal_totals = internal_actuals.groupby('investor_id')['expected_amount'].sum()
        
        # Find mismatches
        amount_diff = pd.concat([fund_admin_totals, internal_totals], axis=1, keys=['fund_admin', 'internal'])
        mismatches = amount_diff[abs(amount_diff['fund_admin'] - amount_diff['internal']) > 0.01]
        
        if not mismatches.empty:
            discrepancies.append(f"Amount mismatches found for investors: {mismatches.index.tolist()}")
        
        # Check for missing transactions
        fund_admin_keys = set(zip(fund_admin_df['investor_id'], fund_admin_df['transaction_date']))
        internal_keys = set(zip(internal_actuals['investor_id'], internal_actuals['expected_date']))
        
        missing_in_internal = fund_admin_keys - internal_keys
        if missing_in_internal:
            discrepancies.append(f"Transactions in fund admin missing from internal tracker: {len(missing_in_internal)}")
        
        missing_in_fund_admin = internal_keys - fund_admin_keys
        if missing_in_fund_admin:
            discrepancies.append(f"Transactions in internal tracker missing from fund admin: {len(missing_in_fund_admin)}")
        
        return ValidationResult(
            is_valid=len(discrepancies) == 0,
            discrepancies=discrepancies,
            details={
                'total_fund_admin_amount': fund_admin_df['investment_amount'].sum(),
                'total_internal_amount': internal_actuals['expected_amount'].sum(),
                'mismatch_count': len(mismatches)
            }
        )

    def generate_summary_report(self, fund_admin_df: pd.DataFrame, internal_df: pd.DataFrame) -> Dict:
        """Generate a comprehensive summary report."""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'historical_summary': {},
            'forecast_summary': {},
            'validation_results': {}
        }
        
        # Historical Summary
        historical_data = fund_admin_df.copy()
        report['historical_summary'] = {
            'total_inflows': historical_data[historical_data['transaction_type'] == 'inflow']['investment_amount'].sum(),
            'total_outflows': historical_data[historical_data['transaction_type'] == 'outflow']['investment_amount'].sum(),
            'net_flow': historical_data[historical_data['transaction_type'] == 'inflow']['investment_amount'].sum() -
                       historical_data[historical_data['transaction_type'] == 'outflow']['investment_amount'].sum(),
            'by_fund_type': historical_data.groupby('fund_type')['investment_amount'].sum().to_dict(),
            'monthly_trends': historical_data.groupby(pd.Grouper(key='transaction_date', freq='M'))['investment_amount'].sum().to_dict()
        }
        
        # Forecast Summary
        forecast_data = internal_df[internal_df['status'] == 'forecast'].copy()
        report['forecast_summary'] = {
            'total_expected_inflows': forecast_data[forecast_data['transaction_type'] == 'inflow']['expected_amount'].sum(),
            'total_expected_outflows': forecast_data[forecast_data['transaction_type'] == 'outflow']['expected_amount'].sum(),
            'weighted_expected_inflows': (forecast_data[forecast_data['transaction_type'] == 'inflow']['expected_amount'] *
                                       forecast_data[forecast_data['transaction_type'] == 'inflow']['probability']).sum(),
            'by_probability_range': {
                'high (>75%)': len(forecast_data[forecast_data['probability'] > 0.75]),
                'medium (25-75%)': len(forecast_data[(forecast_data['probability'] >= 0.25) & (forecast_data['probability'] <= 0.75)]),
                'low (<25%)': len(forecast_data[forecast_data['probability'] < 0.25])
            }
        }
        
        # Save report
        report_path = os.path.join(self.reports_dir, f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Historical data
            pd.DataFrame([report['historical_summary']]).to_excel(writer, sheet_name='Historical_Summary', index=False)
            
            # Forecast data
            pd.DataFrame([report['forecast_summary']]).to_excel(writer, sheet_name='Forecast_Summary', index=False)
            
            # Raw data sheets
            fund_admin_df.to_excel(writer, sheet_name='Fund_Admin_Data', index=False)
            internal_df.to_excel(writer, sheet_name='Internal_Tracker_Data', index=False)
        
        return report

    def process_new_data(self) -> Tuple[bool, str, Dict]:
        """Process new fund admin and internal tracker data."""
        try:
            # Load latest fund admin data
            fund_admin_files = sorted([f for f in os.listdir(self.fund_admin_historical) if f.endswith('.xlsx')])
            if not fund_admin_files:
                return False, "No fund admin data found", {}
            
            latest_fund_admin = pd.read_excel(os.path.join(self.fund_admin_historical, fund_admin_files[-1]))
            
            # Load latest internal tracker data
            internal_files = sorted([f for f in os.listdir(self.internal_historical) if f.endswith('.xlsx')])
            if not internal_files:
                return False, "No internal tracker data found", {}
            
            latest_internal = pd.read_excel(os.path.join(self.internal_historical, internal_files[-1]))
            
            # Load forecast data
            forecast_files = sorted([f for f in os.listdir(self.internal_forecasts) if f.endswith('.xlsx')])
            if forecast_files:
                forecast_data = pd.read_excel(os.path.join(self.internal_forecasts, forecast_files[-1]))
                latest_internal = pd.concat([latest_internal, forecast_data], ignore_index=True)
            
            # Validate data
            fund_admin_validation = self.validate_fund_admin_data(latest_fund_admin)
            internal_validation = self.validate_internal_data(latest_internal)
            comparison_validation = self.compare_data_sources(latest_fund_admin, latest_internal)
            
            # Generate report if all validations pass
            if fund_admin_validation.is_valid and internal_validation.is_valid:
                report = self.generate_summary_report(latest_fund_admin, latest_internal)
                return True, "Data processed successfully", report
            else:
                validation_issues = (
                    fund_admin_validation.discrepancies +
                    internal_validation.discrepancies +
                    comparison_validation.discrepancies
                )
                return False, f"Validation failed: {'; '.join(validation_issues)}", {}
                
        except Exception as e:
            return False, f"Error processing data: {str(e)}", {}

def main():
    processor = EnhancedExcelProcessor()
    success, message, report = processor.process_new_data()
    
    print("\nProcessing Results:")
    print("-" * 50)
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message: {message}")
    if success:
        print("\nReport Summary:")
        print("-" * 50)
        print(f"Historical Net Flow: ${report['historical_summary']['net_flow']:,.2f}")
        print(f"Expected Inflows (Weighted): ${report['forecast_summary']['weighted_expected_inflows']:,.2f}")
        print("\nReport saved in data/reports directory")

if __name__ == "__main__":
    main() 