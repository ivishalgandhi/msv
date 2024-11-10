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
    """Write DataFrame to CSV or XLSX with improved error handling"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        if output_path.endswith('.csv'):
            df.to_csv(output_path, index=False)
            print(f"✓ Written to CSV: {output_path}")
            
        elif output_path.endswith('.xlsx'):
            mode = 'a' if os.path.exists(output_path) else 'w'
            try:
                with pd.ExcelWriter(output_path, mode=mode, if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name or 'Sheet1', index=False)
                print(f"✓ Written to Excel: {output_path} (sheet: {sheet_name or 'Sheet1'})")
            except Exception as excel_error:
                print(f"⚠️ Excel write failed, trying new file: {str(excel_error)}")
                df.to_excel(output_path, sheet_name=sheet_name or 'Sheet1', index=False)
        else:
            raise ValueError(f"Unsupported file format for {output_path}")
            
    except Exception as e:
        raise Exception(f"Error writing to {output_path}: {str(e)}")

def read_file(file_path: Union[str, Path], sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read CSV or XLSX file into a pandas DataFrame."""
    try:
        # Convert Path to string
        file_path = str(file_path)
        
        if not os.path.exists(file_path):
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