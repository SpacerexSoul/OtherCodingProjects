# Excel Data Processor

This application processes investor relations Excel sheets by comparing and combining data from multiple sources. It includes both a command-line interface and a web-based frontend for easy file management and data visualization.

## Directory Structure

- `data/old_sheet/`: Contains the historical Excel sheets
- `data/unprocessed/`: Place new Excel files here for processing
- `data/processed/`: Processed files are moved here automatically

## Setup

### 1. Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```
This will open a web interface where you can:
- Drag and drop Excel files
- View current and historical data
- Process new files with visual feedback
- Compare data before processing

### Command Line Interface
1. Place the existing Excel sheet in `data/old_sheet/` directory
2. Place new Excel files in `data/unprocessed/` directory
3. Run the processor:
```bash
python excel_processor.py
```

## Features

- Automatic column name matching (case and space insensitive)
- Duplicate detection and prevention
- Missing column handling
- Data validation
- Historical version tracking
- Web interface for easy file management
- Interactive data visualization

## File Requirements

### Old Sheet (Base Data)
Must contain some or all of these columns (case insensitive):
- Investor Name
- Investment Amount
- Investment Date
- Fund Type
- Status
- Contact Email
- Last Updated

### New Sheet
- Can contain any subset of the columns from the old sheet
- Column names can vary in case and spacing
- Will be validated against the old sheet structure

## Testing

Run the test suite:
```bash
python -m unittest test_excel_processor.py -v
```

Create test data:
```bash
python create_test_files.py 