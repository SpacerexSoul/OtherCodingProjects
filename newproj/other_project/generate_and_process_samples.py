import os
import subprocess
import sys

def main():
    print("\nGenerating Sample Data Files...")
    print("-" * 50)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate sample fund admin data
    print("\nGenerating fund admin sample data...")
    subprocess.run([sys.executable, "data/sample_fund_admin.xlsx"])
    
    # Generate sample internal tracker data
    print("\nGenerating internal tracker sample data...")
    subprocess.run([sys.executable, "data/sample_internal_tracker.xlsx"])
    
    # Process the files using the data separator
    print("\nProcessing generated files...")
    from data_processor import DataSeparator
    
    separator = DataSeparator()
    
    # Process fund admin sheet
    success, message = separator.process_fund_admin_sheet("data/sample_fund_admin.xlsx")
    print(f"\nFund Admin Processing: {'✅ Success' if success else '❌ Failed'}")
    print(f"Message: {message}")
    
    # Process internal tracker
    success, message = separator.process_internal_tracker("data/sample_internal_tracker.xlsx")
    print(f"\nInternal Tracker Processing: {'✅ Success' if success else '❌ Failed'}")
    print(f"Message: {message}")
    
    # Run validation and reconciliation
    print("\nRunning validation and reconciliation...")
    success, message, report = separator.validate_and_reconcile()
    print(f"\nValidation and Reconciliation: {'✅ Success' if success else '❌ Failed'}")
    print(f"Message: {message}")
    
    if success and report:
        print("\nSummary:")
        print("-" * 50)
        print(f"Historical Net Flow: ${report['historical_summary']['net_flow']:,.2f}")
        print(f"Expected Inflows (Weighted): ${report['forecast_summary']['weighted_expected_inflows']:,.2f}")
    
    print("\nAll done! You can now run the dashboard with:")
    print("streamlit run dashboard.py")

if __name__ == "__main__":
    main() 