# Bond Time Series Analysis Project
## Final Report

## Table of Contents
1. [Introduction](#introduction)
2. [Data Overview](#data-overview)
3. [Time Series Analysis](#time-series-analysis)
4. [Data Filtering and Manipulation](#data-filtering-and-manipulation)
5. [Statistical Analysis](#statistical-analysis)
6. [Merged Datasets Analysis](#merged-datasets-analysis)
7. [Visualizations](#visualizations)
8. [Conclusions](#conclusions)

## Introduction

This report presents a comprehensive analysis of time series data for corporate and government bonds. The project demonstrates various techniques for handling, analyzing, and visualizing bond data over time, including handling missing values, calculating statistics, and merging datasets.

The analysis focuses on two main datasets:
- Corporate bonds from various sectors (Technology, Energy, Finance, Manufacturing, Healthcare)
- Government bonds with different terms (1, 2, 5, 10, and 30 years)

The data spans a two-year period from January 2020 to December 2021, providing a rich dataset for time series analysis.

## Data Overview

### Corporate Bonds Dataset
The corporate bonds dataset contains 3,650 records with the following key attributes:
- BondID: Unique identifier for each bond (CORP001-CORP005)
- BondName: Descriptive name of the bond
- Rating: Credit rating of the bond
- Yield: Bond yield percentage
- Volume: Trading volume
- Sector: Industry sector (Technology, Energy, Finance, Manufacturing, Healthcare)

The dataset contains 188 missing yield values (5.2%) and 380 missing volume values (10.4%), which were handled through various techniques during the analysis.

### Government Bonds Dataset
The government bonds dataset also contains 3,650 records with the following key attributes:
- BondID: Unique identifier for each bond (GOV01Y-GOV30Y)
- BondName: Descriptive name of the bond
- Term: Bond term in years (1, 2, 5, 10, 30)
- Yield: Bond yield percentage
- Volume: Trading volume
- Country: Issuing country (USA)

The dataset contains 91 missing yield values (2.5%) and 178 missing volume values (4.9%).

## Time Series Analysis

### Time Series Indices Creation
To facilitate time series analysis, we created various time-based indices and aggregations:

1. **Daily Time Series**: Set the Date column as the index for both datasets to enable time-based operations.

2. **Pivot Tables**: Created pivot tables with Date as the index and BondID as columns, with Yield values in the cells. This transformation allows for easier comparison of yields across different bonds over time.

3. **Monthly Aggregations**:
   - Calculated monthly average yields for corporate bonds by sector
   - Calculated monthly average yields for government bonds by term

4. **Weekly Aggregations**:
   - Calculated weekly average yields for both corporate and government bonds

5. **Quarterly Aggregations**:
   - Calculated quarterly average yields for both corporate and government bonds

These time series transformations provided different temporal perspectives on the bond data, enabling analysis at various time scales.

## Data Filtering and Manipulation

Several filtering and manipulation techniques were applied to the time series data:

### Date Range Filtering
- Filtered data for specific time periods (Q1 2020 and Q3 2021) to analyze how bond yields changed during different economic conditions.
- Corporate bonds Q1 2020: 455 records
- Government bonds Q1 2020: 455 records
- Corporate bonds Q3 2021: 460 records
- Government bonds Q3 2021: 460 records

### Condition-Based Filtering
- Corporate bonds with yield > 4.0: 785 records
- Government bonds with yield > 2.0: 1070 records
- Corporate bonds with volume > 7000: 1038 records
- Government bonds with volume > 35000: 1136 records
- Technology sector bonds: 730 records
- Government bonds with term > 10 years: 730 records

### Record Removal
- Removed corporate bonds with missing yield values: 188 records removed
- Removed government bonds with missing volume values: 178 records removed
- Removed corporate bonds from Energy sector: 730 records removed
- Removed government bonds with 1-year term: 730 records removed

### Missing Value Handling
Several techniques were applied to handle missing values in the time series data:

1. **Forward Fill**: Propagated the last valid observation forward to fill gaps
2. **Backward Fill**: Used next valid observation to fill gaps
3. **Linear Interpolation**: Interpolated values linearly between existing data points
4. **Mean Imputation**: Filled missing values with the mean of the column

The linear interpolation method proved most effective, reducing missing values in corporate bonds from 188 to 0 and in government bonds from 91 to 1.

## Statistical Analysis

### Rolling Statistics
Rolling statistics were calculated to analyze trends and patterns over time:

1. **Rolling Means**:
   - 7-day rolling mean for both corporate and government bond yields
   - 30-day rolling mean for both corporate and government bond yields

2. **Rolling Standard Deviations**:
   - 7-day rolling standard deviation for both corporate and government bond yields

These rolling statistics helped smooth out short-term fluctuations and highlight longer-term trends in the bond yields.

### Aggregate Statistics
Various aggregate statistics were calculated for different time periods:

1. **Monthly Statistics**:
   - Mean, maximum, minimum, and median yields for each month
   - Total trading volume for each month

2. **Quarterly Statistics**:
   - Mean, maximum, minimum, and median yields for each quarter
   - Total trading volume for each quarter

3. **Sector-wise Statistics for Corporate Bonds**:
   - Mean, maximum, minimum, median, and standard deviation of yields by sector
   - Mean, sum, maximum, and minimum of trading volume by sector

4. **Term-wise Statistics for Government Bonds**:
   - Mean, maximum, minimum, median, and standard deviation of yields by term
   - Mean, sum, maximum, and minimum of trading volume by term

### Correlation Analysis
Correlation analysis was performed to understand the relationships between different bonds:

1. **Corporate Bond Yield Correlations**: Analyzed how yields of different corporate bonds correlate with each other
2. **Government Bond Yield Correlations**: Analyzed how yields of different government bonds correlate with each other
3. **Corporate-Government Yield Correlations**: Analyzed the correlation between average corporate and government bond yields

### Volatility Analysis
Volatility statistics were calculated to measure the variability in bond yields:

1. **Daily Returns**: Calculated percentage changes in yields for both corporate and government bonds
2. **30-day Rolling Volatility**: Calculated the standard deviation of returns over a 30-day window
3. **Average Volatility by Bond**: Calculated the overall volatility for each bond

## Merged Datasets Analysis

Several merged datasets were created to analyze relationships between corporate and government bonds:

### Daily Merged Dataset
- Combined daily average yields and volumes for corporate and government bonds
- Calculated the yield spread (difference between corporate and government yields)
- Calculated the volume ratio (ratio of corporate to government volumes)

### Pivot Tables Merged Dataset
- Combined the corporate and government bond yield pivot tables
- Renamed columns to avoid conflicts and maintain clarity

### Monthly Merged Dataset
- Combined monthly statistics for corporate and government bonds
- Calculated the monthly yield spread

### Sector-Term Merged Dataset
- Created a cross-reference between corporate bond sectors and government bond terms
- Calculated yield differences and volume ratios between sectors and terms
- This dataset provides insights into how different corporate sectors perform relative to government bonds of different terms

## Visualizations

Various visualizations were created to illustrate the time series patterns and relationships in the bond data:

### Yield Comparisons
- Daily corporate vs government bond yields
- Corporate-government yield spread over time
- Monthly corporate vs government bond yields
- Monthly corporate-government yield spread

### Volume Comparisons
- Daily corporate vs government bond trading volumes
- Corporate-to-government volume ratio over time

### Correlation Analysis
- Corporate bond yield correlation heatmap
- Government bond yield correlation heatmap

### Volatility Analysis
- Corporate bond yield volatility bar chart
- Government bond yield volatility bar chart

### Rolling Statistics
- Corporate bond 30-day rolling average yield
- Government bond 30-day rolling average yield

### Sector and Term Analysis
- Sector-term yield difference heatmap
- Average yield by corporate bond sector
- Average yield by government bond term

### Missing Data Handling
- Original vs interpolated data for corporate bonds
- Original vs interpolated data for government bonds

All visualizations are available in the `visualizations` directory, with an HTML index file (`index.html`) providing an organized view of all plots.

## Conclusions

This bond time series analysis project demonstrated various techniques for handling, analyzing, and visualizing time series data for corporate and government bonds. Key findings and accomplishments include:

1. **Effective Missing Data Handling**: Successfully applied various techniques to handle missing values in the time series data, with linear interpolation proving most effective.

2. **Time-Based Aggregations**: Created multiple time-based aggregations (daily, weekly, monthly, quarterly) to analyze bond data at different temporal scales.

3. **Statistical Insights**: Calculated comprehensive statistics including rolling means, volatility measures, and correlations to understand patterns and relationships in bond yields.

4. **Sector and Term Analysis**: Analyzed how different corporate sectors perform relative to government bonds of different terms, providing insights into sector-specific risk premiums.

5. **Visualization of Time Series Patterns**: Created a comprehensive set of visualizations that illustrate the temporal patterns, relationships, and statistical properties of the bond data.

The techniques and approaches demonstrated in this project can be applied to real-world bond data for investment analysis, risk management, and economic forecasting.
