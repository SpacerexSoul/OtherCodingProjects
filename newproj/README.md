# Investor Flow Manager

A tool to track and manage investor fund flows by combining fund admin data with internal forecasts.

## Overview

This system helps manage investor cash flows by:

1. **Automatically importing fund admin data** (historical actuals that arrive on the 15th of each month)
2. **Maintaining forecasts** for future flows that are manually entered
3. **Generating reports and visualizations** for analysis
4. **Validating data** to catch errors and duplicates

## Directory Structure

```
data/
  ├── fund_admin_updates/        # Place fund admin Excel files here
  │   └── processed/             # Processed fund admin files are moved here
  ├── internal_tracker/          # Contains the combined tracker file
  └── reports/                   # Generated reports and visualizations
```

## Usage

### 1. Processing Fund Admin Data

1. Place fund admin Excel files in the `data/fund_admin_updates/` folder
2. Run the manager:
   ```
   python investor_flow_manager.py
   ```
3. The system will automatically:
   - Process any new fund admin files
   - Update the internal tracker with new actual flows
   - Preserve all forecast data
   - Generate reports
   - Move processed files to the `processed/` folder

### 2. Adding Forecasts

You can add forecasts manually when running the manager:

1. Run the manager:
   ```
   python investor_flow_manager.py
   ```
2. When prompted to add a forecast, enter `y`
3. Enter the forecast details:
   - Investor ID
   - Investor Name
   - Fund Type
   - Amount
   - Date (YYYY-MM-DD)
   - Transaction Type (inflow/outflow)
   - Notes (optional)

### 3. Reports

The system automatically generates:

1. `summary_report.xlsx` - Detailed summary of flows by investor
2. `monthly_flows.png` - Chart showing monthly net flows (actuals vs forecasts)
3. `investor_flows.png` - Chart showing net flows by investor

## Fund Admin File Format

Fund admin Excel files should have the following columns:

- `investor_id` - Unique identifier for the investor
- `investor_name` - Name of the investor
- `fund_type` - Type of fund
- `investment_amount` - Amount of the flow
- `transaction_date` - Date of the transaction
- `transaction_type` - Either "inflow" or "outflow"

## Requirements

- Python 3.6+
- pandas
- numpy
- matplotlib
- openpyxl

Install requirements:
```
pip install -r requirements.txt
``` 