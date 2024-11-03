#!/usr/bin/env python3

import argparse
import pandas as pd
from typing import List, Literal, Optional
from .file_handlers import read_file, write_file
from .data_merger import DataMerger
from .version import __version__
from .natural_language import process_natural_language

JoinType = Literal['left', 'right', 'outer', 'inner', 'left_outer', 'right_outer']

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='MSV - Merge and transform CSV/XLSX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  msv -s customers.csv -d orders.csv -m email -c "name,phone"
  msv -s users.xlsx -d accounts.xlsx -m email -c "fullName:name" -i --join outer --source-sheet Users --dest-sheet Accounts
  msv -s data1.csv -d data2.csv -m id -c "field1,field2" -o result.csv --join inner
  msv -s products.xlsx -d inventory.xlsx -m sku -c "name,price" --join right --source-sheet Products --dest-sheet Current
        '''
    )
    parser.add_argument('--source', '-s', required=True, help='Source file path (.csv or .xlsx)')
    parser.add_argument('--destination', '-d', required=True, help='Destination file path (.csv or .xlsx)')
    parser.add_argument('--match-column', '-m', required=True, help='Column to match between files')
    parser.add_argument('--columns', '-c', required=True, help='Comma-separated list of columns to copy from source')
    parser.add_argument('--ignore-case', '-i', action='store_true', help='Ignore case when matching')
    parser.add_argument('--join', choices=['left', 'right', 'outer', 'inner', 'left_outer', 'right_outer'],
                      default='left', help='Join type (default: left)')
    parser.add_argument('--output', '-o', help='Output file path (defaults to destination file)')
    parser.add_argument('--source-sheet', help='Sheet name for source Excel file')
    parser.add_argument('--dest-sheet', help='Sheet name for destination Excel file')
    parser.add_argument('--output-sheet', help='Sheet name for output Excel file (defaults to dest-sheet)')
    parser.add_argument('--version', '-v', action='version', version=f'MSV {__version__}')
    parser.add_argument('--natural', '-n', action='store_true', help='Use natural language interface')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    try:
        if args.natural:
            print("Enter your request in natural language:")
            print("Examples:")
            print("- merge customers.csv into orders.csv using email column and copy name,phone")
            print("- combine users.xlsx and accounts.xlsx matching on id, copy all fields, use outer join")
            print("- update inventory.xlsx from products.csv using sku, copy price,quantity to Sheet1")
            
            query = input("> ")
            request = process_natural_language(query)

            # Read source file
            print(f"📖 Reading source file: {request.source_file}")
            source_df = read_file(request.source_file, sheet_name=request.source_sheet)
            
            # Read destination file
            print(f"📖 Reading destination file: {request.destination_file}")
            dest_df = read_file(request.destination_file, create_if_missing=True, 
                              sheet_name=request.dest_sheet)
            
            # Process merge
            merger = DataMerger(source_df, dest_df)
            result_df = merger.merge(
                match_column=request.match_column,
                columns_to_copy=request.columns_to_copy,
                ignore_case=request.ignore_case,
                join_type=request.join_type
            )
            
            # Write output
            output_path = request.output_file or request.destination_file
            output_sheet = request.output_sheet or request.dest_sheet
            write_file(result_df, output_path, sheet_name=output_sheet)
            
        else:
            # Existing CLI argument handling...
            print(f"📖 Reading source file: {args.source}")
            source_df = read_file(args.source, sheet_name=args.source_sheet)
            
            # Read destination file (create if doesn't exist)
            print(f"📖 Reading destination file: {args.destination}")
            dest_df = read_file(args.destination, create_if_missing=True, sheet_name=args.dest_sheet)
            
            # Get columns to copy
            columns_to_copy = [col.strip() for col in args.columns.split(',')]
            
            # Initialize merger and process files
            merger = DataMerger(source_df, dest_df)
            result_df = merger.merge(
                match_column=args.match_column,
                columns_to_copy=columns_to_copy,
                ignore_case=args.ignore_case,
                join_type=args.join
            )
            
            # Determine output path (use destination file if output not specified)
            output_path = args.output or args.destination
            
            # Determine output sheet (use dest-sheet if output-sheet not specified)
            output_sheet = args.output_sheet or args.dest_sheet
            
            # Write output
            write_file(result_df, output_path, sheet_name=output_sheet)
            
        print("✨ Merge completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())