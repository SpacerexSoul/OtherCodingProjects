import streamlit as st
import pandas as pd
import os
import tempfile
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from investor_flow_manager import InvestorFlowManager
import shutil
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Investor Flow Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the manager
@st.cache_resource
def get_manager():
    return InvestorFlowManager()

manager = get_manager()

# App title and description
st.title("Investor Flow Manager")
st.markdown("""
This app helps you track and manage investor fund flows by combining fund admin data with internal forecasts.
""")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Process Fund Admin", "Add Forecast", "Reports", "Settings"])

# Function to load the current investor tracker data
@st.cache_data
def load_investor_data(path=None):
    """Load investor data from the specified path or the default path"""
    if path is None:
        path = manager.config['internal_tracker_path']
        
    if os.path.exists(path):
        data = pd.read_excel(path)
        if not data.empty:
            data['date'] = pd.to_datetime(data['date'])
        return data
    return pd.DataFrame()

# Helper function to map and standardize column names
def process_fund_admin_with_mapping(file_path, column_mapping=None):
    """
    Process fund admin file with custom column mapping
    
    Args:
        file_path: Path to the fund admin file
        column_mapping: Dictionary mapping custom columns to expected columns
        
    Returns:
        Processed dataframe with standardized column names
    """
    # Read the fund admin file
    df = pd.read_excel(file_path)
    
    # If no mapping provided, return as is
    if not column_mapping:
        return df
    
    # Create a new dataframe with the expected column names
    mapped_df = pd.DataFrame()
    
    # Apply the mapping
    for expected_col, custom_col in column_mapping.items():
        if custom_col and custom_col in df.columns:
            mapped_df[expected_col] = df[custom_col]
    
    return mapped_df

# Get current data
data = load_investor_data()

# Dashboard page
if page == "Dashboard":
    st.header("Investor Flow Dashboard")
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if not data.empty:
        # Calculate metrics
        total_investors = data['investor_id'].nunique()
        total_inflow = data[data['transaction_type'] == 'inflow']['amount'].sum()
        total_outflow = data[data['transaction_type'] == 'outflow']['amount'].sum()
        net_flow = total_inflow - total_outflow
        
        col1.metric("Total Investors", total_investors)
        col2.metric("Total Inflow", f"${total_inflow:,.2f}")
        col3.metric("Total Outflow", f"${total_outflow:,.2f}")
        col4.metric("Net Flow", f"${net_flow:,.2f}")
        
        # Split data into actuals and forecasts
        actuals = data[~data['is_forecast']].copy()
        forecasts = data[data['is_forecast']].copy()
        
        st.subheader("Current Data Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Actual Flows**")
            if not actuals.empty:
                st.dataframe(
                    actuals.sort_values('date', ascending=False)[
                        ['investor_name', 'date', 'transaction_type', 'amount', 'fund_type']
                    ].style.format({'amount': '${:,.2f}'})
                )
            else:
                st.info("No actual flows recorded yet.")
        
        with col2:
            st.write("**Forecasted Flows**")
            if not forecasts.empty:
                st.dataframe(
                    forecasts.sort_values('date')[
                        ['investor_name', 'date', 'transaction_type', 'amount', 'fund_type', 'notes']
                    ].style.format({'amount': '${:,.2f}'})
                )
            else:
                st.info("No forecasts recorded yet.")
        
        # Monthly flow chart (actual and forecast)
        st.subheader("Monthly Net Flows")
        
        if not actuals.empty or not forecasts.empty:
            # Prepare monthly data
            monthly_data = {'actuals': {}, 'forecasts': {}}
            
            # Handle actuals
            if not actuals.empty:
                actuals.loc[:, 'yearmonth'] = actuals['date'].dt.strftime('%Y-%m')
                inflows = actuals[actuals['transaction_type'] == 'inflow'].groupby('yearmonth')['amount'].sum()
                outflows = actuals[actuals['transaction_type'] == 'outflow'].groupby('yearmonth')['amount'].sum()
                
                for month in inflows.index:
                    monthly_data['actuals'][month] = monthly_data['actuals'].get(month, 0) + inflows[month]
                
                for month in outflows.index:
                    monthly_data['actuals'][month] = monthly_data['actuals'].get(month, 0) - outflows[month]
            
            # Handle forecasts
            if not forecasts.empty:
                forecasts.loc[:, 'yearmonth'] = forecasts['date'].dt.strftime('%Y-%m')
                inflows = forecasts[forecasts['transaction_type'] == 'inflow'].groupby('yearmonth')['amount'].sum()
                outflows = forecasts[forecasts['transaction_type'] == 'outflow'].groupby('yearmonth')['amount'].sum()
                
                for month in inflows.index:
                    monthly_data['forecasts'][month] = monthly_data['forecasts'].get(month, 0) + inflows[month]
                
                for month in outflows.index:
                    monthly_data['forecasts'][month] = monthly_data['forecasts'].get(month, 0) - outflows[month]
            
            # Combine and sort all months
            all_months = set(monthly_data['actuals'].keys()) | set(monthly_data['forecasts'].keys())
            all_months = sorted(all_months)
            
            # Create DataFrame for chart
            chart_data = pd.DataFrame(index=all_months)
            chart_data['Actual Net Flow'] = [monthly_data['actuals'].get(month, 0) for month in all_months]
            chart_data['Forecast Net Flow'] = [monthly_data['forecasts'].get(month, 0) for month in all_months]
            
            # Display the chart
            fig = px.bar(
                chart_data,
                x=chart_data.index,
                y=['Actual Net Flow', 'Forecast Net Flow'],
                labels={'index': 'Month', 'value': 'Net Flow Amount'},
                title='Monthly Net Fund Flows (Actual vs Forecast)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for chart.")
    else:
        st.info("No data available. Please process fund admin files or add forecasts.")

# Process Fund Admin page
elif page == "Process Fund Admin":
    st.header("Process Fund Admin Files")
    
    st.markdown("""
    Update your investor tracker with new fund admin data. You can:
    
    1. Select an existing investor tracker file or use the default
    2. Upload or select a fund admin file to process
    3. Map custom column headers if needed
    4. Update the investor tracker with the fund admin data
    """)
    
    # Display column mapping info
    with st.expander("About Column Mapping"):
        st.markdown("""
        ### Expected Column Headers
        
        The following columns are required in your fund admin files:
        
        | Expected Column | Description |
        | --- | --- |
        | `investor_id` | Unique identifier for the investor |
        | `investor_name` | Name of the investor |
        | `fund_type` | Type of fund |
        | `investment_amount` | Amount of the flow |
        | `transaction_date` | Date of the transaction |
        | `transaction_type` | Type of transaction (inflow/outflow) |
        
        The system will automatically try to match your columns to these expected headers. If automatic mapping fails, you'll be able to manually map them.
        
        To view or modify the accepted column names and transaction type values, go to the **Settings** page.
        """)
    
    # Create two tabs: one for file selection and one for file upload
    tab1, tab2 = st.tabs(["File Upload", "Select Existing Files"])
    
    # Tab 1: File upload (original functionality)
    with tab1:
        uploaded_file = st.file_uploader("Upload Fund Admin Excel File", type="xlsx")
        
        if uploaded_file:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Preview the file columns
            preview_df = pd.read_excel(tmp_path)
            if not preview_df.empty:
                st.write("Preview of uploaded file:")
                st.dataframe(preview_df.head(5))
                
                # Try automatic column mapping
                auto_mapped = True
                column_mapping = {}
                missing_columns = []
                
                # Check for each required field
                for field in ['investor_id', 'investor_name', 'fund_type', 
                             'investment_amount', 'transaction_date', 'transaction_type']:
                    # Find matching column in the DataFrame
                    actual_col = manager._find_matching_column(preview_df, field)
                    
                    if actual_col:
                        column_mapping[field] = actual_col
                    else:
                        auto_mapped = False
                        missing_columns.append(field)
                
                # Show mapping status
                if auto_mapped:
                    st.success("✅ All columns were automatically mapped successfully!")
                    
                    # Show the mapping that was found
                    st.subheader("Detected Column Mapping")
                    mapping_data = pd.DataFrame({
                        "Expected Column": list(column_mapping.keys()),
                        "Your Column": list(column_mapping.values())
                    })
                    st.dataframe(mapping_data)
                else:
                    st.warning(f"⚠️ Could not automatically map these columns: {', '.join(missing_columns)}")
                    
                    # Create an interactive mapping selection for each missing field
                    st.subheader("Column Mapping")
                    st.write("Please map the missing columns:")
                    
                    # Get column names from the file
                    available_columns = list(preview_df.columns)
                    
                    for field in missing_columns:
                        column_mapping[field] = st.selectbox(
                            f"Map '{field}' to:",
                            options=[""] + available_columns,
                            format_func=lambda x: x if x else "Select a column",
                            key=f"upload_{field}"
                        )
                
                # Process the file
                if st.button("Process Uploaded File"):
                    # Validate the mapping
                    missing_mappings = [field for field, col in column_mapping.items() if not col]
                    
                    if missing_mappings:
                        st.error(f"Please map all required columns before processing. Missing: {', '.join(missing_mappings)}")
                    else:
                        with st.spinner("Processing file..."):
                            # Process with mapping
                            mapped_df = process_fund_admin_with_mapping(tmp_path, column_mapping)
                            
                            # Save mapped df to a new temp file
                            mapped_path = tmp_path + "_mapped.xlsx"
                            mapped_df.to_excel(mapped_path, index=False)
                            
                            # Process the mapped file
                            result = manager.update_from_fund_admin(mapped_path)
                            
                            # Clean up temp files
                            os.unlink(mapped_path)
                            os.unlink(tmp_path)
                            
                            # Display results
                            if result['success']:
                                st.success(result['message'])
                                
                                st.subheader("Processing Summary")
                                st.write(f"New entries: {result['stats']['new_entries']}")
                                st.write(f"Total records: {result['stats']['total_records']}")
                                st.write(f"Total inflow: ${result['stats']['inflow_amount']:,.2f}")
                                st.write(f"Total outflow: ${result['stats']['outflow_amount']:,.2f}")
                                st.write(f"Net flow: ${result['stats']['net_flow']:,.2f}")
                                
                                # Reload the data
                                st.cache_data.clear()
                            else:
                                st.error(result['message'])
                                
                                if 'validation_issues' in result:
                                    st.subheader("Validation Issues")
                                    for issue in result['validation_issues']:
                                        st.warning(issue)
    
    # Tab 2: Select existing files
    with tab2:
        st.subheader("Select Files to Process")
        
        # 1. Select investor tracker file (optional)
        use_custom_tracker = st.checkbox("Use custom investor tracker file", value=False)
        tracker_file_path = None
        
        if use_custom_tracker:
            tracker_files = []
            
            # Look for Excel files in the data/internal_tracker directory
            tracker_dir = os.path.dirname(manager.config['internal_tracker_path'])
            if os.path.exists(tracker_dir):
                tracker_files = [
                    f for f in os.listdir(tracker_dir) 
                    if f.endswith('.xlsx') and os.path.isfile(os.path.join(tracker_dir, f))
                ]
            
            if tracker_files:
                selected_tracker = st.selectbox(
                    "Select investor tracker file", 
                    options=tracker_files,
                    format_func=lambda x: x
                )
                tracker_file_path = os.path.join(tracker_dir, selected_tracker)
                
                # Show preview of the selected tracker
                tracker_preview = load_investor_data(tracker_file_path)
                if not tracker_preview.empty:
                    st.write("Preview of selected tracker:")
                    st.dataframe(
                        tracker_preview.head(5).style.format({'amount': '${:,.2f}'})
                    )
            else:
                st.warning("No tracker files found in data/internal_tracker directory")
        else:
            st.info(f"Using default investor tracker: {os.path.basename(manager.config['internal_tracker_path'])}")
        
        # 2. Select fund admin file
        fund_admin_files = []
        
        # Look for Excel files in the data/fund_admin_updates directory
        fund_admin_dir = manager.config['fund_admin_folder']
        if os.path.exists(fund_admin_dir):
            fund_admin_files = [
                f for f in os.listdir(fund_admin_dir) 
                if f.endswith('.xlsx') and os.path.isfile(os.path.join(fund_admin_dir, f))
                and 'processed' not in f  # Skip files in processed directory
                and 'mapped_' not in f    # Skip already mapped files
            ]
        
        if fund_admin_files:
            selected_fund_admin = st.selectbox(
                "Select fund admin file to process", 
                options=fund_admin_files,
                format_func=lambda x: x
            )
            fund_admin_path = os.path.join(fund_admin_dir, selected_fund_admin)
            
            # Show preview of the selected fund admin file
            if os.path.exists(fund_admin_path):
                fund_admin_preview = pd.read_excel(fund_admin_path)
                if not fund_admin_preview.empty:
                    st.write("Preview of selected fund admin file:")
                    st.dataframe(
                        fund_admin_preview.head(5)
                    )
                    
                    # Try automatic column mapping
                    auto_mapped = True
                    column_mapping = {}
                    missing_columns = []
                    
                    # Check for each required field
                    for field in ['investor_id', 'investor_name', 'fund_type', 
                                 'investment_amount', 'transaction_date', 'transaction_type']:
                        # Find matching column in the DataFrame
                        actual_col = manager._find_matching_column(fund_admin_preview, field)
                        
                        if actual_col:
                            column_mapping[field] = actual_col
                        else:
                            auto_mapped = False
                            missing_columns.append(field)
                    
                    # Show mapping status
                    if auto_mapped:
                        st.success("✅ All columns were automatically mapped successfully!")
                        
                        # Show the mapping that was found
                        st.subheader("Detected Column Mapping")
                        mapping_data = pd.DataFrame({
                            "Expected Column": list(column_mapping.keys()),
                            "Your Column": list(column_mapping.values())
                        })
                        st.dataframe(mapping_data)
                    else:
                        st.warning(f"⚠️ Could not automatically map these columns: {', '.join(missing_columns)}")
                        
                        # Create an interactive mapping selection for each missing field
                        st.subheader("Column Mapping")
                        st.write("Please map the missing columns:")
                        
                        # Get column names from the file
                        available_columns = list(fund_admin_preview.columns)
                        
                        for field in missing_columns:
                            column_mapping[field] = st.selectbox(
                                f"Map '{field}' to:",
                                options=[""] + available_columns,
                                format_func=lambda x: x if x else "Select a column",
                                key=f"existing_{field}"
                            )
                    
                    # Process button
                    if st.button("Process Selected Files"):
                        # Validate the mapping if not auto-mapped
                        if not auto_mapped:
                            missing_mappings = [field for field, col in column_mapping.items() if not col]
                            
                            if missing_mappings:
                                st.error(f"Please map all required columns before processing. Missing: {', '.join(missing_mappings)}")
                                st.stop()
                        
                        with st.spinner("Processing files..."):
                            # If using custom tracker, we need to:
                            # 1. Temporarily backup the current default
                            # 2. Copy the selected tracker to the default location
                            # 3. Process the fund admin file
                            # 4. Restore the original default if needed
                            
                            result = None
                            backup_path = None
                            tmp_mapped_path = None
                            
                            try:
                                # Handle custom mapping if needed
                                if not auto_mapped:
                                    # Process with mapping
                                    mapped_df = process_fund_admin_with_mapping(fund_admin_path, column_mapping)
                                    
                                    # Save mapped df to a temp file
                                    tmp_mapped_path = os.path.join(
                                        os.path.dirname(fund_admin_path),
                                        f"mapped_{os.path.basename(fund_admin_path)}"
                                    )
                                    mapped_df.to_excel(tmp_mapped_path, index=False)
                                    
                                    # Use the mapped file for processing
                                    processing_path = tmp_mapped_path
                                else:
                                    # Use original file
                                    processing_path = fund_admin_path
                                
                                # Handle custom tracker if needed
                                if use_custom_tracker and tracker_file_path:
                                    # Backup current default if it exists
                                    default_path = manager.config['internal_tracker_path']
                                    if os.path.exists(default_path):
                                        backup_path = default_path + ".backup"
                                        shutil.copy2(default_path, backup_path)
                                    
                                    # Copy selected tracker to default location
                                    shutil.copy2(tracker_file_path, default_path)
                                
                                # Process the fund admin file
                                result = manager.update_from_fund_admin(processing_path)
                                
                            finally:
                                # Clean up temp mapped file if created
                                if tmp_mapped_path and os.path.exists(tmp_mapped_path):
                                    os.remove(tmp_mapped_path)
                                    
                                # Always restore backup if we made one
                                if backup_path and os.path.exists(backup_path):
                                    shutil.copy2(backup_path, default_path)
                                    os.remove(backup_path)
                            
                            # Display results
                            if result and result['success']:
                                # If using custom tracker, copy updated default back to custom location
                                if use_custom_tracker and tracker_file_path:
                                    shutil.copy2(manager.config['internal_tracker_path'], tracker_file_path)
                                
                                st.success(result['message'])
                                
                                st.subheader("Processing Summary")
                                st.write(f"New entries: {result['stats']['new_entries']}")
                                st.write(f"Total records: {result['stats']['total_records']}")
                                st.write(f"Total inflow: ${result['stats']['inflow_amount']:,.2f}")
                                st.write(f"Total outflow: ${result['stats']['outflow_amount']:,.2f}")
                                st.write(f"Net flow: ${result['stats']['net_flow']:,.2f}")
                                
                                # Move file to processed folder after successful processing
                                processed_path = os.path.join(manager.config['processed_admin_folder'], selected_fund_admin)
                                shutil.move(fund_admin_path, processed_path)
                                st.info(f"File moved to processed folder: {processed_path}")
                                
                                # Reload the data
                                st.cache_data.clear()
                            elif result:
                                st.error(result['message'])
                                
                                if 'validation_issues' in result:
                                    st.subheader("Validation Issues")
                                    for issue in result['validation_issues']:
                                        st.warning(issue)
                                
                                if 'missing_columns' in result:
                                    st.subheader("Missing Columns")
                                    st.error(f"Could not find these required columns: {', '.join(result['missing_columns'])}")
                            else:
                                st.error("An unknown error occurred during processing")
        else:
            st.warning("No fund admin files found in data/fund_admin_updates directory")

# Add Forecast page
elif page == "Add Forecast":
    st.header("Add Forecast")
    
    st.markdown("""
    Add forecasted investor flows to the tracker.
    """)
    
    # Get unique investors from existing data for dropdown
    investors = []
    if not data.empty:
        investors = data[['investor_id', 'investor_name']].drop_duplicates().values.tolist()
    
    # Form for adding a forecast
    with st.form("forecast_form"):
        # Option to select existing investor or add new one
        use_existing = st.checkbox("Use existing investor", value=len(investors) > 0)
        
        if use_existing and investors:
            selected_investor = st.selectbox(
                "Select Investor", 
                options=investors,
                format_func=lambda x: f"{x[0]} - {x[1]}"
            )
            investor_id = selected_investor[0]
            investor_name = selected_investor[1]
        else:
            investor_id = st.text_input("Investor ID")
            investor_name = st.text_input("Investor Name")
        
        # Other forecast details
        fund_type = st.text_input("Fund Type")
        amount = st.number_input("Amount", min_value=0.0, format="%f")
        date = st.date_input("Date")
        transaction_type = st.selectbox("Transaction Type", options=["inflow", "outflow"])
        notes = st.text_area("Notes")
        
        submit = st.form_submit_button("Add Forecast")
    
    if submit:
        # Validate inputs
        if not investor_id or not investor_name or not fund_type or amount <= 0:
            st.error("Please fill all required fields with valid values.")
        else:
            # Format forecast data
            forecast_data = {
                'investor_id': investor_id,
                'investor_name': investor_name,
                'fund_type': fund_type,
                'amount': amount,
                'date': date.strftime('%Y-%m-%d'),
                'transaction_type': transaction_type,
                'notes': notes
            }
            
            # Add forecast
            with st.spinner("Adding forecast..."):
                result = manager.add_forecast(forecast_data)
                
                # Display result
                if result['success']:
                    st.success(result['message'])
                    
                    # Reload the data
                    st.cache_data.clear()
                else:
                    st.error(result['message'])

# Reports page
elif page == "Reports":
    st.header("Reports and Analysis")
    
    if not data.empty:
        # Generate reports if data exists
        with st.spinner("Generating reports..."):
            manager.generate_reports()
        
        # Display summary report
        st.subheader("Summary Report")
        summary_path = os.path.join(manager.config['reports_folder'], 'summary_report.xlsx')
        
        if os.path.exists(summary_path):
            summary = pd.read_excel(summary_path, index_col=0)
            
            # Format summary for display
            formatted_summary = summary.style.format({
                'actual_inflows': '${:,.2f}',
                'actual_outflows': '${:,.2f}',
                'forecast_inflows': '${:,.2f}',
                'forecast_outflows': '${:,.2f}',
                'actual_net': '${:,.2f}',
                'forecast_net': '${:,.2f}',
                'total_net': '${:,.2f}'
            })
            
            st.dataframe(formatted_summary)
            
            # Download links for reports
            st.subheader("Download Reports")
            
            with open(summary_path, "rb") as file:
                st.download_button(
                    label="Download Summary Report (Excel)",
                    data=file,
                    file_name="investor_summary_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Display charts
            st.subheader("Charts")
            
            col1, col2 = st.columns(2)
            
            # Monthly flows chart
            monthly_chart_path = os.path.join(manager.config['reports_folder'], 'monthly_flows.png')
            if os.path.exists(monthly_chart_path):
                with col1:
                    st.image(monthly_chart_path, caption="Monthly Net Fund Flows", use_column_width=True)
            
            # Investor flows chart
            investor_chart_path = os.path.join(manager.config['reports_folder'], 'investor_flows.png')
            if os.path.exists(investor_chart_path):
                with col2:
                    st.image(investor_chart_path, caption="Net Fund Flow by Investor", use_column_width=True)
        else:
            st.warning("Summary report not found. Try regenerating reports.")
    else:
        st.info("No data available. Please process fund admin files or add forecasts first.")

# Settings page
elif page == "Settings":
    st.header("Settings")
    
    st.write("""
    Configure the column mapping and data processing settings for the investor flow manager.
    These settings allow the app to work with different fund admin file formats.
    """)
    
    # Column mapping settings
    st.subheader("Column Mapping Configuration")
    
    tabs = st.tabs(["Column Names", "Transaction Types", "Test Mapping"])
    
    # Tab 1: Column Names
    with tabs[0]:
        st.markdown("""
        ### Column Name Mappings
        
        Configure mappings from your custom column headers to the standard column names required by the system.
        The system will try to match your columns to these names (case-insensitive).
        """)
        
        # Get current column mappings
        current_mappings = manager.config['column_mappings']
        
        # Create UI for each expected column
        fields = [
            ('investor_id', 'Investor ID', 'Unique identifier for the investor'),
            ('investor_name', 'Investor Name', 'Name of the investor'),
            ('fund_type', 'Fund Type', 'Type of fund, strategy, or class'),
            ('investment_amount', 'Investment Amount', 'Amount of the flow'),
            ('transaction_date', 'Transaction Date', 'Date of the transaction'),
            ('transaction_type', 'Transaction Type', 'Type of transaction (inflow/outflow)')
        ]
        
        for field_id, field_name, field_desc in fields:
            st.write(f"#### {field_name}")
            st.write(field_desc)
            
            # Get existing mappings for this field
            mappings = current_mappings.get(field_id, [])
            mappings_text = ", ".join(mappings)
            
            new_mappings = st.text_area(
                f"Enter possible column names for {field_name} (comma-separated)",
                value=mappings_text,
                key=f"mappings_{field_id}",
                help="Enter all possible column names that might appear in your fund admin files"
            )
            
            if st.button(f"Update {field_name} Mappings", key=f"update_{field_id}"):
                # Parse new mappings
                new_mapping_list = [m.strip() for m in new_mappings.split(",") if m.strip()]
                current_mappings[field_id] = new_mapping_list
                
                # Update the config
                manager.config['column_mappings'] = current_mappings
                
                st.success(f"{field_name} mappings updated successfully!")
    
    # Tab 2: Transaction Types
    with tabs[1]:
        st.markdown("""
        ### Transaction Type Values
        
        Configure the values that identify inflows vs outflows in your fund admin files.
        """)
        
        # Get current transaction type mappings
        transaction_values = manager.config.get('transaction_type_values', {
            'inflow': [],
            'outflow': []
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Inflow Terms")
            inflow_values = transaction_values.get('inflow', [])
            inflow_text = "\n".join(inflow_values)
            
            new_inflows = st.text_area(
                "Enter terms that identify inflows (one per line)",
                value=inflow_text,
                height=300,
                help="The system will look for these terms in transaction type values to identify inflows"
            )
        
        with col2:
            st.subheader("Outflow Terms")
            outflow_values = transaction_values.get('outflow', [])
            outflow_text = "\n".join(outflow_values)
            
            new_outflows = st.text_area(
                "Enter terms that identify outflows (one per line)",
                value=outflow_text,
                height=300,
                help="The system will look for these terms in transaction type values to identify outflows"
            )
        
        if st.button("Update Transaction Type Mappings"):
            # Parse new values
            new_inflow_list = [line.strip() for line in new_inflows.splitlines() if line.strip()]
            new_outflow_list = [line.strip() for line in new_outflows.splitlines() if line.strip()]
            
            # Update the config
            transaction_values['inflow'] = new_inflow_list
            transaction_values['outflow'] = new_outflow_list
            manager.config['transaction_type_values'] = transaction_values
            
            st.success("Transaction type mappings updated successfully!")
    
    # Tab 3: Test Mapping
    with tabs[2]:
        st.markdown("""
        ### Test Column Mapping
        
        Test how your column mappings would work with a sample file.
        Upload an Excel file to see how the system would map its columns.
        """)
        
        test_file = st.file_uploader("Upload a file to test column mapping", type="xlsx")
        
        if test_file:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(test_file.getvalue())
                tmp_path = tmp.name
            
            # Read the file
            test_df = pd.read_excel(tmp_path)
            
            # Show file preview
            st.write("File Preview:")
            st.dataframe(test_df.head(5))
            
            # Try mapping columns
            st.subheader("Column Mapping Results")
            
            mapping_results = []
            
            for field_id, field_name, _ in fields:
                # Try to find matching column
                matched_col = manager._find_matching_column(test_df, field_id)
                status = "✅ Matched" if matched_col else "❌ Not Found"
                
                mapping_results.append({
                    "Expected Column": field_name,
                    "Actual Column": matched_col if matched_col else "Not found",
                    "Status": status
                })
            
            # Display results
            results_df = pd.DataFrame(mapping_results)
            st.dataframe(results_df)
            
            # Check overall status
            success = all(row['Status'] == "✅ Matched" for row in mapping_results)
            
            if success:
                st.success("All required columns were successfully mapped!")
            else:
                st.warning("Some columns could not be mapped. Review your column mappings in the 'Column Names' tab.")
            
            # Display value standardization for transaction types
            if "Transaction Type" in test_df.columns or any(col in test_df.columns for col in current_mappings.get('transaction_type', [])):
                st.subheader("Transaction Type Standardization")
                st.write("Here's how transaction types would be standardized:")
                
                # Find the transaction type column
                trans_col = manager._find_matching_column(test_df, 'transaction_type')
                
                if trans_col:
                    # Get unique values
                    unique_types = test_df[trans_col].dropna().unique()
                    
                    stand_results = []
                    for val in unique_types:
                        standardized = manager._standardize_transaction_type(val)
                        stand_results.append({
                            "Original Value": val,
                            "Standardized To": standardized,
                            "Valid": "✅ Valid" if standardized in ['inflow', 'outflow'] else "❌ Invalid"
                        })
                    
                    # Display results
                    stand_df = pd.DataFrame(stand_results)
                    st.dataframe(stand_df)
                    
                    # Check for invalid types
                    invalid_count = sum(1 for row in stand_results if row['Valid'] == "❌ Invalid")
                    if invalid_count > 0:
                        st.warning(f"Found {invalid_count} invalid transaction types. Review your transaction type mappings.")
                    else:
                        st.success("All transaction types were successfully standardized!")
                else:
                    st.info("Transaction type column not found.")
            
            # Clean up
            os.unlink(tmp_path)

# Add footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app helps track investor fund flows "
    "by combining fund admin data with internal forecasts."
) 