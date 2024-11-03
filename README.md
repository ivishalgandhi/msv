# MSV - Merge Source Values

A powerful CLI tool for merging and transforming CSV/XLSX files with natural language support.

## Features
- Merge data from CSV and Excel files
- Case-sensitive or case-insensitive matching
- Multiple join types (left, right, outer, inner)
- Excel sheet support
- Natural language interface
- Column mapping with custom names

## Installation
```bash
pip install msv
```

## Usage

### Command Line

```bash
msv --source customers.csv --destination orders.csv --match-column email --columns "name,phone"
```

### Natural Language Interface

```bash
msv --natural
> merge customers.csv and orders.csv using email column, copy name and phone, ignore case
```

### Options

- `--source, -s`: Source file path (.csv or .xlsx)
- `--destination, -d`: Destination file path (.csv or .xlsx)
- `--match-column, -m`: Column to match between files
- `--columns, -c`: Columns to copy (comma-separated)
- `--ignore-case, -i`: Ignore case when matching
- `--join`: Join type (left, outer, inner)
- `--output, -o`: Custom output file path
- `--source-sheet`: Sheet name for source Excel file
- `--dest-sheet`: Sheet name for destination Excel file
- `--output-sheet`: Sheet name for output Excel file (defaults to dest-sheet)

### Excel Sheet Support

When working with Excel files (.xlsx), you can specify sheet names:

```bash
# Merge specific sheets from Excel files
msv \
  --source users.xlsx \
  --destination accounts.xlsx \
  --match-column email \
  --columns "name,phone" \
  --source-sheet Users \
  --dest-sheet Accounts

# Write to a different output sheet
msv \
  --source data.xlsx \
  --destination report.xlsx \
  --match-column id \
  --columns "value,category" \
  --source-sheet Raw \
  --dest-sheet Current \
  --output-sheet "March 2024"
```

If no sheet is specified:
- For source files: Uses the first sheet
- For destination files: Uses the first sheet or creates "Sheet1"
- Available sheets are listed when reading Excel files

## Configuration

The application supports multiple AI providers for natural language processing. Configure your preferred settings in `config.toml`:

1. Copy the example configuration file:
```bash
cp config.toml.example config.toml
```

## Development

### Requirements

- Python 3.7+
- pandas
- openpyxl
 
### Running Tests
```bash
python -m unittest discover tests
```

## License

MIT