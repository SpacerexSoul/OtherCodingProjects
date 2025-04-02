import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from enhanced_processor import EnhancedExcelProcessor

st.set_page_config(page_title="Fund Flow Dashboard", layout="wide")

def load_latest_report():
    """Load the most recent summary report."""
    reports_dir = "data/reports"
    if not os.path.exists(reports_dir):
        return None
    
    report_files = sorted([f for f in os.listdir(reports_dir) if f.startswith('summary_report_')])
    if not report_files:
        return None
    
    latest_report = os.path.join(reports_dir, report_files[-1])
    return {
        'historical': pd.read_excel(latest_report, sheet_name='Historical_Summary'),
        'forecast': pd.read_excel(latest_report, sheet_name='Forecast_Summary'),
        'fund_admin': pd.read_excel(latest_report, sheet_name='Fund_Admin_Data'),
        'internal': pd.read_excel(latest_report, sheet_name='Internal_Tracker_Data')
    }

def create_monthly_flow_chart(data):
    """Create a monthly flow visualization."""
    df = data['fund_admin'].copy()
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    monthly = df.groupby([pd.Grouper(key='transaction_date', freq='M'), 'transaction_type'])['investment_amount'].sum().reset_index()
    
    fig = go.Figure()
    
    # Add inflows
    inflows = monthly[monthly['transaction_type'] == 'inflow']
    fig.add_trace(go.Bar(
        x=inflows['transaction_date'],
        y=inflows['investment_amount'],
        name='Inflows',
        marker_color='green'
    ))
    
    # Add outflows
    outflows = monthly[monthly['transaction_type'] == 'outflow']
    fig.add_trace(go.Bar(
        x=outflows['transaction_date'],
        y=-outflows['investment_amount'],  # Negative for visualization
        name='Outflows',
        marker_color='red'
    ))
    
    # Add net flow line
    net_flow = monthly.pivot(index='transaction_date', columns='transaction_type', values='investment_amount').fillna(0)
    net_flow['net'] = net_flow['inflow'] - net_flow['outflow']
    
    fig.add_trace(go.Scatter(
        x=net_flow.index,
        y=net_flow['net'].cumsum(),
        name='Cumulative Net Flow',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title='Monthly Fund Flows',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        barmode='relative',
        hovermode='x unified'
    )
    
    return fig

def create_forecast_probability_chart(data):
    """Create a forecast probability visualization."""
    df = data['internal'][data['internal']['status'] == 'forecast'].copy()
    df['expected_date'] = pd.to_datetime(df['expected_date'])
    
    fig = go.Figure()
    
    # Scatter plot for expected inflows
    inflows = df[df['transaction_type'] == 'inflow']
    fig.add_trace(go.Scatter(
        x=inflows['expected_date'],
        y=inflows['expected_amount'],
        mode='markers',
        name='Expected Inflows',
        marker=dict(
            size=10,
            color=inflows['probability'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Probability')
        )
    ))
    
    fig.update_layout(
        title='Forecast Flows by Probability',
        xaxis_title='Expected Date',
        yaxis_title='Expected Amount ($)',
        hovermode='closest'
    )
    
    return fig

def create_fund_type_breakdown(data):
    """Create a fund type breakdown visualization."""
    df = data['fund_admin'].copy()
    by_fund = df.groupby('fund_type')['investment_amount'].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=by_fund.index,
        values=by_fund.values,
        hole=.3
    )])
    
    fig.update_layout(
        title='Investment Distribution by Fund Type'
    )
    
    return fig

def main():
    st.title("Fund Flow Dashboard")
    
    # Initialize processor
    processor = EnhancedExcelProcessor()
    
    # Sidebar for data processing
    st.sidebar.title("Data Processing")
    if st.sidebar.button("Process New Data"):
        success, message, _ = processor.process_new_data()
        st.sidebar.write(f"Status: {'✅ Success' if success else '❌ Failed'}")
        st.sidebar.write(f"Message: {message}")
    
    # Load latest report
    data = load_latest_report()
    if data is None:
        st.warning("No reports found. Please process data first.")
        return
    
    # Dashboard Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Historical Flow Analysis")
        st.plotly_chart(create_monthly_flow_chart(data), use_container_width=True)
    
    with col2:
        st.subheader("Fund Type Distribution")
        st.plotly_chart(create_fund_type_breakdown(data), use_container_width=True)
    
    # Forecast Analysis
    st.subheader("Forecast Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_probability = st.slider("Minimum Probability", 0.0, 1.0, 0.0, 0.1)
    with col2:
        selected_fund_types = st.multiselect(
            "Fund Types",
            options=data['internal']['fund_type'].unique(),
            default=data['internal']['fund_type'].unique()
        )
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now(), datetime.now() + timedelta(days=365)),
            key="forecast_date_range"
        )
    
    # Filter forecast data
    forecast_df = data['internal'][
        (data['internal']['status'] == 'forecast') &
        (data['internal']['probability'] >= min_probability) &
        (data['internal']['fund_type'].isin(selected_fund_types))
    ]
    
    if len(date_range) == 2:
        forecast_df['expected_date'] = pd.to_datetime(forecast_df['expected_date'])
        forecast_df = forecast_df[
            (forecast_df['expected_date'] >= pd.Timestamp(date_range[0])) &
            (forecast_df['expected_date'] <= pd.Timestamp(date_range[1]))
        ]
    
    # Display forecast visualization
    st.plotly_chart(create_forecast_probability_chart({'internal': forecast_df}), use_container_width=True)
    
    # Summary metrics
    st.subheader("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Historical Inflows",
            f"${data['fund_admin'][data['fund_admin']['transaction_type'] == 'inflow']['investment_amount'].sum():,.0f}"
        )
    
    with col2:
        st.metric(
            "Total Historical Outflows",
            f"${data['fund_admin'][data['fund_admin']['transaction_type'] == 'outflow']['investment_amount'].sum():,.0f}"
        )
    
    with col3:
        st.metric(
            "Expected Inflows (Next 12M)",
            f"${forecast_df[forecast_df['transaction_type'] == 'inflow']['expected_amount'].sum():,.0f}"
        )
    
    with col4:
        st.metric(
            "Weighted Expected Inflows",
            f"${(forecast_df[forecast_df['transaction_type'] == 'inflow']['expected_amount'] * forecast_df[forecast_df['transaction_type'] == 'inflow']['probability']).sum():,.0f}"
        )
    
    # Data tables
    st.subheader("Detailed Data")
    tab1, tab2 = st.tabs(["Historical Data", "Forecast Data"])
    
    with tab1:
        st.dataframe(data['fund_admin'])
    
    with tab2:
        st.dataframe(forecast_df)

if __name__ == "__main__":
    main() 