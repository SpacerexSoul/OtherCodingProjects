import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

def load_merged_data():
    """Load the merged datasets"""
    print("Loading merged datasets...")
    
    # Load merged daily data
    merged_daily = pd.read_csv('../data/merged/merged_daily.csv')
    merged_daily['Date'] = pd.to_datetime(merged_daily['Date'])
    
    # Load merged pivot data
    merged_pivots = pd.read_csv('../data/merged/merged_pivots.csv')
    merged_pivots['Date'] = pd.to_datetime(merged_pivots['Date'])
    
    # Load merged monthly data
    merged_monthly = pd.read_csv('../data/merged/merged_monthly.csv')
    merged_monthly['Date'] = pd.to_datetime(merged_monthly['Date'])
    
    # Load merged sector-term data
    merged_sector_term = pd.read_csv('../data/merged/merged_sector_term.csv')
    merged_sector_term['Date'] = pd.to_datetime(merged_sector_term['Date'])
    
    print(f"Loaded merged datasets successfully")
    
    return {
        'merged_daily': merged_daily,
        'merged_pivots': merged_pivots,
        'merged_monthly': merged_monthly,
        'merged_sector_term': merged_sector_term
    }

def load_statistics_data():
    """Load the statistics data"""
    print("Loading statistics data...")
    
    # Load correlation data
    corp_yield_corr = pd.read_csv('../data/statistics/corp_yield_corr.csv', index_col=0)
    gov_yield_corr = pd.read_csv('../data/statistics/gov_yield_corr.csv', index_col=0)
    
    # Load volatility data
    corp_avg_vol = pd.read_csv('../data/statistics/corp_avg_vol.csv')
    gov_avg_vol = pd.read_csv('../data/statistics/gov_avg_vol.csv')
    
    # Load rolling statistics
    corp_rolling_mean_30d = pd.read_csv('../data/statistics/corp_rolling_mean_30d.csv', index_col=0)
    corp_rolling_mean_30d.index = pd.to_datetime(corp_rolling_mean_30d.index)
    
    gov_rolling_mean_30d = pd.read_csv('../data/statistics/gov_rolling_mean_30d.csv', index_col=0)
    gov_rolling_mean_30d.index = pd.to_datetime(gov_rolling_mean_30d.index)
    
    # Load sector and term statistics
    corp_sector_stats = pd.read_csv('../data/statistics/corp_sector_stats.csv')
    gov_term_stats = pd.read_csv('../data/statistics/gov_term_stats.csv')
    
    print(f"Loaded statistics data successfully")
    
    return {
        'corp_yield_corr': corp_yield_corr,
        'gov_yield_corr': gov_yield_corr,
        'corp_avg_vol': corp_avg_vol,
        'gov_avg_vol': gov_avg_vol,
        'corp_rolling_mean_30d': corp_rolling_mean_30d,
        'gov_rolling_mean_30d': gov_rolling_mean_30d,
        'corp_sector_stats': corp_sector_stats,
        'gov_term_stats': gov_term_stats
    }

def create_yield_comparison_plots(merged_data):
    """Create yield comparison plots"""
    print("\nCreating yield comparison plots...")
    
    # Create directory for visualizations
    os.makedirs('../visualizations', exist_ok=True)
    
    # Plot daily corporate vs government yields
    plt.figure(figsize=(14, 8))
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['CorpYield'], label='Corporate Bonds')
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['GovYield'], label='Government Bonds')
    plt.title('Corporate vs Government Bond Yields (Daily Average)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Yield (%)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/daily_yield_comparison.png')
    plt.close()
    
    # Plot yield spread over time
    plt.figure(figsize=(14, 8))
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['YieldSpread'], color='purple')
    plt.title('Corporate-Government Yield Spread Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Yield Spread (%)', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/yield_spread_over_time.png')
    plt.close()
    
    # Plot monthly yield comparison
    plt.figure(figsize=(14, 8))
    plt.plot(merged_data['merged_monthly']['Date'], merged_data['merged_monthly']['CorpYield'], label='Corporate Bonds')
    plt.plot(merged_data['merged_monthly']['Date'], merged_data['merged_monthly']['GovYield'], label='Government Bonds')
    plt.title('Corporate vs Government Bond Yields (Monthly Average)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Yield (%)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/monthly_yield_comparison.png')
    plt.close()
    
    # Plot monthly spread
    plt.figure(figsize=(14, 8))
    plt.bar(merged_data['merged_monthly']['Date'], merged_data['merged_monthly']['MonthlySpread'], color='teal')
    plt.title('Monthly Corporate-Government Yield Spread', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Monthly Spread (%)', fontsize=12)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('../visualizations/monthly_yield_spread.png')
    plt.close()
    
    print(f"Created yield comparison plots")
    
    return ['daily_yield_comparison.png', 'yield_spread_over_time.png', 
            'monthly_yield_comparison.png', 'monthly_yield_spread.png']

def create_volume_comparison_plots(merged_data):
    """Create volume comparison plots"""
    print("\nCreating volume comparison plots...")
    
    # Plot daily corporate vs government volumes
    plt.figure(figsize=(14, 8))
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['CorpVolume'], label='Corporate Bonds')
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['GovVolume'], label='Government Bonds')
    plt.title('Corporate vs Government Bond Trading Volumes (Daily Average)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Volume', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/daily_volume_comparison.png')
    plt.close()
    
    # Plot volume ratio over time
    plt.figure(figsize=(14, 8))
    plt.plot(merged_data['merged_daily']['Date'], merged_data['merged_daily']['VolumeRatio'], color='orange')
    plt.title('Corporate-to-Government Volume Ratio Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Volume Ratio (Corp/Gov)', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/volume_ratio_over_time.png')
    plt.close()
    
    print(f"Created volume comparison plots")
    
    return ['daily_volume_comparison.png', 'volume_ratio_over_time.png']

def create_correlation_heatmaps(stats_data):
    """Create correlation heatmaps"""
    print("\nCreating correlation heatmaps...")
    
    # Corporate bond yield correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(stats_data['corp_yield_corr'], annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title('Corporate Bond Yield Correlation Matrix', fontsize=16)
    plt.tight_layout()
    plt.savefig('../visualizations/corp_yield_correlation.png')
    plt.close()
    
    # Government bond yield correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(stats_data['gov_yield_corr'], annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title('Government Bond Yield Correlation Matrix', fontsize=16)
    plt.tight_layout()
    plt.savefig('../visualizations/gov_yield_correlation.png')
    plt.close()
    
    print(f"Created correlation heatmaps")
    
    return ['corp_yield_correlation.png', 'gov_yield_correlation.png']

def create_volatility_plots(stats_data):
    """Create volatility plots"""
    print("\nCreating volatility plots...")
    
    # Corporate bond volatility bar chart
    plt.figure(figsize=(12, 8))
    sns.barplot(x='BondID', y='Volatility', data=stats_data['corp_avg_vol'])
    plt.title('Corporate Bond Yield Volatility', fontsize=16)
    plt.xlabel('Bond ID', fontsize=12)
    plt.ylabel('Volatility (Standard Deviation of Returns)', fontsize=12)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('../visualizations/corp_bond_volatility.png')
    plt.close()
    
    # Government bond volatility bar chart
    plt.figure(figsize=(12, 8))
    sns.barplot(x='BondID', y='Volatility', data=stats_data['gov_avg_vol'])
    plt.title('Government Bond Yield Volatility', fontsize=16)
    plt.xlabel('Bond ID', fontsize=12)
    plt.ylabel('Volatility (Standard Deviation of Returns)', fontsize=12)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('../visualizations/gov_bond_volatility.png')
    plt.close()
    
    print(f"Created volatility plots")
    
    return ['corp_bond_volatility.png', 'gov_bond_volatility.png']

def create_rolling_statistics_plots(stats_data):
    """Create rolling statistics plots"""
    print("\nCreating rolling statistics plots...")
    
    # Corporate bond 30-day rolling mean
    plt.figure(figsize=(14, 8))
    for column in stats_data['corp_rolling_mean_30d'].columns:
        plt.plot(stats_data['corp_rolling_mean_30d'].index, stats_data['corp_rolling_mean_30d'][column], label=column)
    plt.title('Corporate Bond 30-Day Rolling Average Yield', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('30-Day Rolling Average Yield (%)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/corp_rolling_mean_30d.png')
    plt.close()
    
    # Government bond 30-day rolling mean
    plt.figure(figsize=(14, 8))
    for column in stats_data['gov_rolling_mean_30d'].columns:
        plt.plot(stats_data['gov_rolling_mean_30d'].index, stats_data['gov_rolling_mean_30d'][column], label=column)
    plt.title('Government Bond 30-Day Rolling Average Yield', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('30-Day Rolling Average Yield (%)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/gov_rolling_mean_30d.png')
    plt.close()
    
    print(f"Created rolling statistics plots")
    
    return ['corp_rolling_mean_30d.png', 'gov_rolling_mean_30d.png']

def create_sector_term_plots(merged_data):
    """Create sector and term analysis plots"""
    print("\nCreating sector and term analysis plots...")
    
    # Load the original prepared datasets to get sector and term data
    corp_bonds = pd.read_csv('../data/prepared/corp_bonds_prepared.csv')
    corp_bonds['Date'] = pd.to_datetime(corp_bonds['Date'])
    
    gov_bonds = pd.read_csv('../data/prepared/gov_bonds_prepared.csv')
    gov_bonds['Date'] = pd.to_datetime(gov_bonds['Date'])
    
    # Filter sector-term data for a specific date for visualization
    specific_date = '2021-06-30'
    sector_term_snapshot = merged_data['merged_sector_term'][
        merged_data['merged_sector_term']['Date'] == specific_date
    ]
    
    # Create a pivot table for the heatmap
    sector_term_pivot = sector_term_snapshot.pivot(
        index='Sector',
        columns='Term',
        values='YieldDiff'
    )
    
    # Sector-Term yield difference heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(sector_term_pivot, annot=True, cmap='RdBu_r', center=0)
    plt.title(f'Sector-Term Yield Difference Heatmap ({specific_date})', fontsize=16)
    plt.xlabel('Government Bond Term (Years)', fontsize=12)
    plt.ylabel('Corporate Bond Sector', fontsize=12)
    plt.tight_layout()
    plt.savefig('../visualizations/sector_term_yield_diff.png')
    plt.close()
    
    # Calculate average yield by sector
    sector_avg_yield = corp_bonds.groupby('Sector')['Yield'].mean().reset_index()
    
    # Corporate bond sector statistics
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Sector', y='Yield', data=sector_avg_yield)
    plt.title('Average Yield by Corporate Bond Sector', fontsize=16)
    plt.xlabel('Sector', fontsize=12)
    plt.ylabel('Average Yield (%)', fontsize=12)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('../visualizations/sector_avg_yield.png')
    plt.close()
    
    # Calculate average yield by term
    term_avg_yield = gov_bonds.groupby('Term')['Yield'].mean().reset_index()
    
    # Government bond term statistics
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Term', y='Yield', data=term_avg_yield)
    plt.title('Average Yield by Government Bond Term', fontsize=16)
    plt.xlabel('Term (Years)', fontsize=12)
    plt.ylabel('Average Yield (%)', fontsize=12)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig('../visualizations/term_avg_yield.png')
    plt.close()
    
    print(f"Created sector and term analysis plots")
    
    return ['sector_term_yield_diff.png', 'sector_avg_yield.png', 'term_avg_yield.png']

def create_missing_data_visualization(merged_data):
    """Create visualizations related to missing data handling"""
    print("\nCreating missing data visualizations...")
    
    # Load the original pivot tables to show missing values
    corp_yield_pivot_original = pd.read_csv('../data/time_series/corp_yield_pivot.csv', parse_dates=['Date'], index_col='Date')
    gov_yield_pivot_original = pd.read_csv('../data/time_series/gov_yield_pivot.csv', parse_dates=['Date'], index_col='Date')
    
    # Load the interpolated pivot tables
    corp_yield_pivot_interp = pd.read_csv('../data/filtered/corp_yield_pivot_interp.csv', parse_dates=['Date'], index_col='Date')
    gov_yield_pivot_interp = pd.read_csv('../data/filtered/gov_yield_pivot_interp.csv', parse_dates=['Date'], index_col='Date')
    
    # Select a specific bond to visualize missing data handling
    corp_bond_id = 'CORP001'
    gov_bond_id = 'GOV05Y'
    
    # Plot original vs interpolated data for corporate bond
    plt.figure(figsize=(14, 8))
    plt.plot(corp_yield_pivot_original.index, corp_yield_pivot_original[corp_bond_id], 'o-', label='Original Data', alpha=0.7)
    plt.plot(corp_yield_pivot_interp.index, corp_yield_pivot_interp[corp_bond_id], 'o-', label='Interpolated Data', alpha=0.7)
    plt.title(f'Original vs Interpolated Data for {corp_bond_id}', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Yield (%)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/corp_missing_data_handling.png')
    plt.close()
    
    # Plot original vs interpolated data for government bond
    plt.figure(figsize=(14, 8))
    plt.plot(gov_yield_pivot_original.index, gov_yield_pivot_original[gov_bond_id], 'o-', label='Original Data', alpha=0.7)
    plt.plot(gov_yield_pivot_interp.index, gov_yield_pivot_interp[gov_bond_id], 'o-', label='Interpolated Data', alpha=0.7)
    plt.title(f'Original vs Interpolated Data for {gov_bond_id}', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Yield (%)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../visualizations/gov_missing_data_handling.png')
    plt.close()
    
    print(f"Created missing data visualizations")
    
    return ['corp_missing_data_handling.png', 'gov_missing_data_handling.png']

def create_visualization_index(all_visualizations):
    """Create an HTML index of all visualizations"""
    print("\nCreating visualization index...")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bond Time Series Analysis Visualizations</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            h2 {
                color: #555;
<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>