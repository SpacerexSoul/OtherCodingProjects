import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set plot style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

def load_filtered_data():
    """Load the filtered time series data"""
    print("Loading filtered time series data...")
    
    # Load interpolated yield pivot tables (with missing values handled)
    corp_yield_pivot = pd.read_csv('../data/filtered/corp_yield_pivot_interp.csv', parse_dates=['Date'], index_col='Date')
    gov_yield_pivot = pd.read_csv('../data/filtered/gov_yield_pivot_interp.csv', parse_dates=['Date'], index_col='Date')
    
    # Load filtered corporate bonds without missing yields
    corp_bonds = pd.read_csv('../data/filtered/corp_bonds_no_missing_yield.csv', parse_dates=['Date'], index_col='Date')
    
    # Load filtered government bonds without missing volumes
    gov_bonds = pd.read_csv('../data/filtered/gov_bonds_no_missing_volume.csv', parse_dates=['Date'], index_col='Date')
    
    print(f"Loaded filtered time series data successfully")
    
    return {
        'corp_yield_pivot': corp_yield_pivot,
        'gov_yield_pivot': gov_yield_pivot,
        'corp_bonds': corp_bonds,
        'gov_bonds': gov_bonds
    }

def calculate_rolling_statistics(filtered_data):
    """Calculate rolling statistics for time series data"""
    print("\nCalculating rolling statistics...")
    
    # Calculate 7-day rolling mean for corporate bond yields
    corp_rolling_mean_7d = filtered_data['corp_yield_pivot'].rolling(window=7).mean()
    
    # Calculate 30-day rolling mean for corporate bond yields
    corp_rolling_mean_30d = filtered_data['corp_yield_pivot'].rolling(window=30).mean()
    
    # Calculate 7-day rolling standard deviation for corporate bond yields
    corp_rolling_std_7d = filtered_data['corp_yield_pivot'].rolling(window=7).std()
    
    # Calculate 7-day rolling mean for government bond yields
    gov_rolling_mean_7d = filtered_data['gov_yield_pivot'].rolling(window=7).mean()
    
    # Calculate 30-day rolling mean for government bond yields
    gov_rolling_mean_30d = filtered_data['gov_yield_pivot'].rolling(window=30).mean()
    
    # Calculate 7-day rolling standard deviation for government bond yields
    gov_rolling_std_7d = filtered_data['gov_yield_pivot'].rolling(window=7).std()
    
    print(f"Calculated rolling statistics for corporate and government bond yields")
    
    return {
        'corp_rolling_mean_7d': corp_rolling_mean_7d,
        'corp_rolling_mean_30d': corp_rolling_mean_30d,
        'corp_rolling_std_7d': corp_rolling_std_7d,
        'gov_rolling_mean_7d': gov_rolling_mean_7d,
        'gov_rolling_mean_30d': gov_rolling_mean_30d,
        'gov_rolling_std_7d': gov_rolling_std_7d
    }

def calculate_aggregate_statistics(filtered_data):
    """Calculate aggregate statistics for time series data"""
    print("\nCalculating aggregate statistics...")
    
    # Resample corporate bonds to monthly frequency and calculate statistics
    corp_monthly = filtered_data['corp_bonds'].resample('M')
    corp_monthly_mean = corp_monthly['Yield'].mean().reset_index()
    corp_monthly_max = corp_monthly['Yield'].max().reset_index()
    corp_monthly_min = corp_monthly['Yield'].min().reset_index()
    corp_monthly_median = corp_monthly['Yield'].median().reset_index()
    corp_monthly_sum = corp_monthly['Volume'].sum().reset_index()
    
    # Resample government bonds to monthly frequency and calculate statistics
    gov_monthly = filtered_data['gov_bonds'].resample('M')
    gov_monthly_mean = gov_monthly['Yield'].mean().reset_index()
    gov_monthly_max = gov_monthly['Yield'].max().reset_index()
    gov_monthly_min = gov_monthly['Yield'].min().reset_index()
    gov_monthly_median = gov_monthly['Yield'].median().reset_index()
    gov_monthly_sum = gov_monthly['Volume'].sum().reset_index()
    
    # Resample corporate bonds to quarterly frequency and calculate statistics
    corp_quarterly = filtered_data['corp_bonds'].resample('Q')
    corp_quarterly_mean = corp_quarterly['Yield'].mean().reset_index()
    corp_quarterly_max = corp_quarterly['Yield'].max().reset_index()
    corp_quarterly_min = corp_quarterly['Yield'].min().reset_index()
    corp_quarterly_median = corp_quarterly['Yield'].median().reset_index()
    corp_quarterly_sum = corp_quarterly['Volume'].sum().reset_index()
    
    # Resample government bonds to quarterly frequency and calculate statistics
    gov_quarterly = filtered_data['gov_bonds'].resample('Q')
    gov_quarterly_mean = gov_quarterly['Yield'].mean().reset_index()
    gov_quarterly_max = gov_quarterly['Yield'].max().reset_index()
    gov_quarterly_min = gov_quarterly['Yield'].min().reset_index()
    gov_quarterly_median = gov_quarterly['Yield'].median().reset_index()
    gov_quarterly_sum = gov_quarterly['Volume'].sum().reset_index()
    
    print(f"Calculated monthly and quarterly aggregate statistics for corporate and government bonds")
    
    # Calculate sector-wise statistics for corporate bonds
    corp_sector_stats = filtered_data['corp_bonds'].groupby('Sector').agg({
        'Yield': ['mean', 'max', 'min', 'median', 'std'],
        'Volume': ['mean', 'sum', 'max', 'min']
    })
    
    # Calculate term-wise statistics for government bonds
    gov_term_stats = filtered_data['gov_bonds'].groupby('Term').agg({
        'Yield': ['mean', 'max', 'min', 'median', 'std'],
        'Volume': ['mean', 'sum', 'max', 'min']
    })
    
    print(f"Calculated sector-wise statistics for corporate bonds and term-wise statistics for government bonds")
    
    return {
        'corp_monthly_mean': corp_monthly_mean,
        'corp_monthly_max': corp_monthly_max,
        'corp_monthly_min': corp_monthly_min,
        'corp_monthly_median': corp_monthly_median,
        'corp_monthly_sum': corp_monthly_sum,
        'gov_monthly_mean': gov_monthly_mean,
        'gov_monthly_max': gov_monthly_max,
        'gov_monthly_min': gov_monthly_min,
        'gov_monthly_median': gov_monthly_median,
        'gov_monthly_sum': gov_monthly_sum,
        'corp_quarterly_mean': corp_quarterly_mean,
        'corp_quarterly_max': corp_quarterly_max,
        'corp_quarterly_min': corp_quarterly_min,
        'corp_quarterly_median': corp_quarterly_median,
        'corp_quarterly_sum': corp_quarterly_sum,
        'gov_quarterly_mean': gov_quarterly_mean,
        'gov_quarterly_max': gov_quarterly_max,
        'gov_quarterly_min': gov_quarterly_min,
        'gov_quarterly_median': gov_quarterly_median,
        'gov_quarterly_sum': gov_quarterly_sum,
        'corp_sector_stats': corp_sector_stats,
        'gov_term_stats': gov_term_stats
    }

def calculate_correlation_statistics(filtered_data):
    """Calculate correlation statistics between different bonds"""
    print("\nCalculating correlation statistics...")
    
    # Calculate correlation between corporate bond yields
    corp_yield_corr = filtered_data['corp_yield_pivot'].corr()
    
    # Calculate correlation between government bond yields
    gov_yield_corr = filtered_data['gov_yield_pivot'].corr()
    
    # Calculate correlation between corporate and government bond yields
    # First, we need to align the dates
    combined_yields = pd.concat([
        filtered_data['corp_yield_pivot'].mean(axis=1).rename('Corp_Avg'),
        filtered_data['gov_yield_pivot'].mean(axis=1).rename('Gov_Avg')
    ], axis=1)
    combined_corr = combined_yields.corr()
    
    print(f"Calculated correlation statistics for bond yields")
    
    return {
        'corp_yield_corr': corp_yield_corr,
        'gov_yield_corr': gov_yield_corr,
        'combined_corr': combined_corr
    }

def calculate_volatility_statistics(filtered_data, rolling_stats):
    """Calculate volatility statistics for bond yields"""
    print("\nCalculating volatility statistics...")
    
    # Calculate daily returns (percentage change) for corporate bond yields
    corp_daily_returns = filtered_data['corp_yield_pivot'].pct_change().dropna()
    
    # Calculate daily returns (percentage change) for government bond yields
    gov_daily_returns = filtered_data['gov_yield_pivot'].pct_change().dropna()
    
    # Calculate 30-day rolling volatility (standard deviation of returns) for corporate bonds
    corp_rolling_vol_30d = corp_daily_returns.rolling(window=30).std()
    
    # Calculate 30-day rolling volatility (standard deviation of returns) for government bonds
    gov_rolling_vol_30d = gov_daily_returns.rolling(window=30).std()
    
    # Calculate average volatility by bond
    corp_avg_vol = corp_daily_returns.std().reset_index()
    corp_avg_vol.columns = ['BondID', 'Volatility']
    
    gov_avg_vol = gov_daily_returns.std().reset_index()
    gov_avg_vol.columns = ['BondID', 'Volatility']
    
    print(f"Calculated volatility statistics for bond yields")
    
    return {
        'corp_daily_returns': corp_daily_returns,
        'gov_daily_returns': gov_daily_returns,
        'corp_rolling_vol_30d': corp_rolling_vol_30d,
        'gov_rolling_vol_30d': gov_rolling_vol_30d,
        'corp_avg_vol': corp_avg_vol,
        'gov_avg_vol': gov_avg_vol
    }

def save_statistics(stats_data):
    """Save the calculated statistics to files"""
    # Create a directory for statistics if it doesn't exist
    os.makedirs('../data/statistics', exist_ok=True)
    
    # Save rolling statistics
    stats_data['corp_rolling_mean_7d'].to_csv('../data/statistics/corp_rolling_mean_7d.csv')
    stats_data['corp_rolling_mean_30d'].to_csv('../data/statistics/corp_rolling_mean_30d.csv')
    stats_data['corp_rolling_std_7d'].to_csv('../data/statistics/corp_rolling_std_7d.csv')
    stats_data['gov_rolling_mean_7d'].to_csv('../data/statistics/gov_rolling_mean_7d.csv')
    stats_data['gov_rolling_mean_30d'].to_csv('../data/statistics/gov_rolling_mean_30d.csv')
    stats_data['gov_rolling_std_7d'].to_csv('../data/statistics/gov_rolling_std_7d.csv')
    
    # Save aggregate statistics
    stats_data['corp_monthly_mean'].to_csv('../data/statistics/corp_monthly_mean.csv', index=False)
    stats_data['corp_monthly_max'].to_csv('../data/statistics/corp_monthly_max.csv', index=False)
    stats_data['corp_quarterly_mean'].to_csv('../data/statistics/corp_quarterly_mean.csv', index=False)
    stats_data['gov_monthly_mean'].to_csv('../data/statistics/gov_monthly_mean.csv', index=False)
    stats_data['gov_monthly_max'].to_csv('../data/statistics/gov_monthly_max.csv', index=False)
    stats_data['gov_quarterly_mean'].to_csv('../data/statistics/gov_quarterly_mean.csv', index=False)
    
    # Save correlation statistics
    stats_data['corp_yield_corr'].to_csv('../data/statistics/corp_yield_corr.csv')
    stats_data['gov_yield_corr'].to_csv('../data/statistics/gov_yield_corr.csv')
    stats_data['combined_corr'].to_csv('../data/statistics/combined_corr.csv')
    
    # Save volatility statistics
    stats_data['corp_rolling_vol_30d'].to_csv('../data/statistics/corp_rolling_vol_30d.csv')
    stats_data['gov_rolling_vol_30d'].to_csv('../data/statistics/gov_rolling_vol_30d.csv')
    stats_data['corp_avg_vol'].to_csv('../data/statistics/corp_avg_vol.csv', index=False)
    stats_data['gov_avg_vol'].to_csv('../data/statistics/gov_avg_vol.csv', index=False)
    
    # Save sector and term statistics
    stats_data['corp_sector_stats'].to_csv('../data/statistics/corp_sector_stats.csv')
    stats_data['gov_term_stats'].to_csv('../data/statistics/gov_term_stats.csv')
    
    print("\nStatistics saved to data/statistics directory")

if __name__ == "__main__":
    # Load filtered data
    filtered_data = load_filtered_data()
    
    # Calculate rolling statistics
    rolling_stats = calculate_rolling_statistics(filtered_data)
    
    # Calculate aggregate statistics
    aggregate_stats = calculate_aggregate_statistics(filtered_data)
    
    # Calculate correlation statistics
    correlation_stats = calculate_correlation_statistics(filtered_data)
    
    # Calculate volatility statistics
    volatility_stats = calculate_volatility_statistics(filtered_data, rolling_stats)
    
    # Combine all statistics
    all_stats = {}
    all_stats.update(rolling_stats)
    all_stats.update(aggregate_stats)
    all_stats.update(correlation_stats)
    all_stats.update(volatility_stats)
    
    # Save statistics
    save_statistics(all_stats)
    
    print("\nTime-based statistics calculation completed successfully!")
