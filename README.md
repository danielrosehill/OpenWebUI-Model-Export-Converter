# OpenWebUI Model Export Converter

A collection of Python scripts for processing and streamlining model exports from OpenWebUI. These scripts help to create more condensed backups of model collections and improve portability by removing OpenWebUI-specific elements.

## Created: March 19, 2025

**Note:** Accuracy after this date cannot be guaranteed as OpenWebUI might change its data format. As of the creation date, these scripts have been validated with the current OpenWebUI export format.

## Purpose

The primary purpose of these scripts is to:

1. Streamline backing up model collections in a more condensed fashion
2. Remove OpenWebUI-specific elements that might not be required when importing elsewhere
3. Improve the portability of models across different platforms

## Scripts

### 1. JSON to CSV Converter (`scripts/json_to_csv.py`)

This script creates a streamlined CSV export from the JSON data, capturing the essential information:
- Model name
- Description
- System prompt

The CSV format is more compact and easier to review than the original JSON structure.

### 2. JSON Simplifier (`scripts/simplify_json.py`)

This script converts the original JSON format into a more streamlined version, keeping only the essential information:
- Model name
- System prompt
- Description

It also includes an option to filter out entries containing personal information.

## How to Use

1. Place your OpenWebUI model export JSON file in the `input` directory as `input.json`
2. Run either script from the command line:

```bash
# For CSV conversion
python scripts/json_to_csv.py

# For JSON simplification
python scripts/simplify_json.py
```

3. Find the output files in the `output` directory with timestamps in their filenames

## Directory Structure

```
.
├── input/            # Place your input JSON files here
├── output/           # Processed files will be saved here
├── sample-data/      # Sample input data for reference
├── screenshots/      # Screenshots for documentation
├── scripts/          # The processing scripts
│   ├── json_to_csv.py
│   └── simplify_json.py
└── requirements.txt  # Project dependencies
```

## Dependencies

The scripts use only standard Python libraries:
- json
- csv
- os
- sys
- datetime
- argparse (for simplify_json.py)

Optional enhancements:
- pandas (for more advanced data manipulation)
- tqdm (for progress bars when processing large files)

## Sample Data

The repository includes sample data in `sample-data/sample-input.json` to demonstrate the expected input format.

## Disclaimer

These scripts are designed to work with the OpenWebUI export format as of March 19, 2025. Future updates to OpenWebUI may change the data format, which could affect the functionality of these scripts.
