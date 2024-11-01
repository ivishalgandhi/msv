import pandas as pd
import os
from typing import Union, Optional

def read_file(file_path: str, create_if_missing: bool = False, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read CSV or XLSX file into a pandas DataFrame.
    
    Args:
        file_path: Path to the file
        create_if_missing: Whether to create an empty DataFrame if file doesn't exist
        sheet_name: Sheet name for Excel files (ignored for CSV)
    """
    try:
        # If file doesn't exist and create_if_missing is True, return empty DataFrame
        if not os.path.exists(file_path):
            if create_if_missing:
                print(f"Destination file {file_path} doesn't exist. Will create new file.")
                return pd.DataFrame()
            else:
                raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            if sheet_name:
                try:
                    return pd.read_excel(file_path, sheet_name=sheet_name)
                except ValueError:
                    available_sheets = pd.ExcelFile(file_path).sheet_names
                    raise ValueError(
                        f"Sheet '{sheet_name}' not found. Available sheets: {', '.join(available_sheets)}"
                    )
            else:
                # List available sheets if none specified
                available_sheets = pd.ExcelFile(file_path).sheet_names
                print(f"No sheet specified. Using first sheet. Available sheets: {', '.join(available_sheets)}")
                return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
    except Exception as e:
        if not isinstance(e, (FileNotFoundError, ValueError)):
            raise Exception(f"Error reading {file_path}: {str(e)}")
        raise

def write_file(df: pd.DataFrame, output_path: str, sheet_name: Optional[str] = None):
    """Write DataFrame to CSV or XLSX.
    
    Args:
        df: DataFrame to write
        output_path: Path to write to
        sheet_name: Sheet name for Excel files (ignored for CSV)
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        if output_path.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif output_path.endswith('.xlsx'):
            # If file exists, try to update specific sheet
            if os.path.exists(output_path) and sheet_name:
                try:
                    with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name=sheet_name or 'Sheet1', index=False)
                except:  # If append fails, write new file
                    df.to_excel(output_path, sheet_name=sheet_name or 'Sheet1', index=False)
            else:
                df.to_excel(output_path, sheet_name=sheet_name or 'Sheet1', index=False)
        print(f"Successfully wrote output to {output_path}" + (f" (sheet: {sheet_name})" if sheet_name else ""))
    except Exception as e:
        raise Exception(f"Error writing output: {str(e)}")