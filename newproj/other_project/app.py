import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from excel_processor import ExcelProcessor
import os
import shutil
from datetime import datetime

st.set_page_config(page_title="Investor Relations Excel Processor", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stProgress .st-bo {
        background-color: #00a878;
    }
    </style>
""", unsafe_allow_html=True)

def save_uploaded_file(uploaded_file, directory):
    """Save uploaded file to specified directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def load_excel_data(file_path):
    """Load Excel file and return DataFrame."""
    if file_path and os.path.exists(file_path):
        return pd.read_excel(file_path)
    return None

def create_investment_summary(df):
    """Create investment summary metrics and charts."""
    if 'Investment amount' in df.columns:
        total_investment = df['Investment amount'].sum()
        avg_investment = df['Investment amount'].mean()
        num_investors = len(df)
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Investment", f"${total_investment:,.2f}")
        with col2:
            st.metric("Average Investment", f"${avg_investment:,.2f}")
        with col3:
            st.metric("Number of Investors", num_investors)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Fund Type Distribution
            if 'Fund type' in df.columns:
                fig_fund = px.pie(df, values='Investment amount', names='Fund type',
                                title='Investment Distribution by Fund Type')
                st.plotly_chart(fig_fund, use_container_width=True)
        
        with col2:
            # Investment Timeline
            if 'investment date' in df.columns:
                df_sorted = df.sort_values('investment date')
                fig_timeline = px.line(df_sorted, x='investment date', y='Investment amount',
                                     title='Investment Timeline')
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Additional visualizations for the larger dataset
        if 'Investment Region' in df.columns and 'Risk Level' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Region-wise Investment
                region_data = df.groupby('Investment Region')['Investment amount'].sum().reset_index()
                fig_region = px.bar(region_data, x='Investment Region', y='Investment amount',
                                  title='Investments by Region')
                st.plotly_chart(fig_region, use_container_width=True)
            
            with col2:
                # Risk Level Distribution
                risk_data = df.groupby('Risk Level')['Investment amount'].sum().reset_index()
                fig_risk = px.bar(risk_data, x='Risk Level', y='Investment amount',
                                 title='Investments by Risk Level')
                st.plotly_chart(fig_risk, use_container_width=True)

def main():
    st.title("Investor Relations Excel Processor")
    
    processor = ExcelProcessor()
    
    # Sidebar for file uploads
    with st.sidebar:
        st.header("Upload Files")
        
        # Old sheet upload
        st.subheader("Current Data Sheet")
        old_file = st.file_uploader("Upload existing investor relations sheet", type=['xlsx'])
        
        if old_file:
            save_uploaded_file(old_file, processor.old_sheet_dir)
            st.success(f"✅ Saved base file: {old_file.name}")
        
        # New sheet upload
        st.subheader("New Data Sheet")
        new_file = st.file_uploader("Upload new investor data", type=['xlsx'])
        
        if new_file:
            save_uploaded_file(new_file, processor.unprocessed_dir)
            st.success(f"✅ Saved new file: {new_file.name}")
        
        # Add a divider
        st.divider()
        
        # Show file requirements
        with st.expander("📋 File Requirements"):
            st.markdown("""
                ### Required Columns:
                - Investor Name
                - Investment Amount
                - Investment Date
                - Fund Type
                
                ### Optional Columns:
                - Contact Email
                - Investment Region
                - Risk Level
                - Expected Return
                - Investment Term
                - Company
                - Phone
                
                *Note: Column names are case and space insensitive*
            """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["Current Data", "New Data", "Processing History"])
    
    # Current Data Tab
    with tab1:
        st.header("Current Investment Portfolio")
        latest_old = processor.get_latest_old_sheet()
        if latest_old:
            old_df = load_excel_data(latest_old)
            if old_df is not None:
                create_investment_summary(old_df)
                
                # Data table with filters
                st.subheader("Detailed Data View")
                if 'Fund type' in old_df.columns:
                    fund_type_filter = st.multiselect('Filter by Fund Type:', 
                                                     options=old_df['Fund type'].unique())
                    if fund_type_filter:
                        old_df = old_df[old_df['Fund type'].isin(fund_type_filter)]
                
                st.dataframe(old_df, use_container_width=True)
        else:
            st.info("No current data available. Please upload a base Excel file.")
    
    # New Data Tab
    with tab2:
        st.header("New Investment Data")
        unprocessed_files = processor.get_unprocessed_files()
        
        if unprocessed_files:
            st.subheader("Files to Process")
            for file in unprocessed_files:
                st.write(f"📄 {file}")
                
                # Preview new data
                new_df = load_excel_data(os.path.join(processor.unprocessed_dir, file))
                if new_df is not None:
                    with st.expander(f"Preview: {file}"):
                        create_investment_summary(new_df)
            
            if st.button("Process New Data", type="primary"):
                results = processor.process_all_files()
                
                for filename, success, message, _ in results:
                    if success:
                        st.success(f"✅ {filename}: {message}")
                    else:
                        st.error(f"❌ {filename}: {message}")
                
                st.rerun()
        else:
            st.info("No new data to process. Please upload new Excel files.")
    
    # History Tab
    with tab3:
        st.header("Processing History")
        processed_files = os.listdir(processor.processed_dir) if os.path.exists(processor.processed_dir) else []
        
        if processed_files:
            history_df = pd.DataFrame({
                'Filename': processed_files,
                'Processed Date': [datetime.fromtimestamp(os.path.getmtime(
                    os.path.join(processor.processed_dir, f))).strftime('%Y-%m-%d %H:%M:%S')
                    for f in processed_files]
            })
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No processing history available.")

if __name__ == "__main__":
    main() 