import pandas as pd
import os
from typing import Union, Optional
from pathlib import Path

def read_file(file_path: Union[str, Path], create_if_missing: bool = False, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read CSV or XLSX file into a pandas DataFrame."""
    try:
        # Convert Path to string
        file_path = str(file_path)
        
        if not os.path.exists(file_path):
            if create_if_missing:
                print(f"File {file_path} doesn't exist. Creating empty DataFrame.")
                return pd.DataFrame()
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            try:
                if sheet_name:
                    return pd.read_excel(file_path, sheet_name=sheet_name)
                # If no sheet specified, read first sheet but show available sheets
                available_sheets = pd.ExcelFile(file_path).sheet_names
                print(f"Available sheets: {', '.join(available_sheets)}")
                return pd.read_excel(file_path)
            except ValueError as e:
                available_sheets = pd.ExcelFile(file_path).sheet_names
                raise ValueError(f"Sheet error: {str(e)}. Available sheets: {', '.join(available_sheets)}")
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
    except Exception as e:
        raise Exception(f"Error reading {file_path}: {str(e)}")

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