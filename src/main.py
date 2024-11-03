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
        description='MSV - Merge and transform CSV/XLSX files'
    )
    parser.add_argument('--natural', '-n', action='store_true',
                       help='Use natural language interface')
    parser.add_argument('--source', '-s', 
                       help='Source file path (.csv or .xlsx)')
    parser.add_argument('--destination', '-d',
                       help='Destination file path (.csv or .xlsx)')
    parser.add_argument('--match-column', '-m',
                       help='Column to match between files')
    parser.add_argument('--columns', '-c',
                       help='Comma-separated list of columns to copy from source')
    parser.add_argument('--ignore-case', '-i', action='store_true',
                       help='Ignore case when matching')
    parser.add_argument('--join',
                       choices=['left', 'right', 'outer', 'inner', 'left_outer', 'right_outer'],
                       default='left', help='Join type (default: left)')
    parser.add_argument('--output', '-o',
                       help='Output file path (defaults to destination file)')
    parser.add_argument('--source-sheet',
                       help='Sheet name for source Excel file')
    parser.add_argument('--dest-sheet',
                       help='Sheet name for destination Excel file')
    parser.add_argument('--output-sheet',
                       help='Sheet name for output Excel file (defaults to dest-sheet)')
    parser.add_argument('--version', '-v', action='version',
                       version=f'MSV {__version__}')
    
    args = parser.parse_args()
    
    # Only enforce required arguments if not using natural language
    if not args.natural:
        if not all([args.source, args.destination, args.match_column, args.columns]):
            parser.error("the following arguments are required: --source/-s, "
                        "--destination/-d, --match-column/-m, --columns/-c")
    
    return args

def main():
    args = parse_arguments()
    
    try:
        if args.natural:
            print("Enter your request in natural language:")
            print("Examples:")
            print("- merge customers.csv into orders.csv using email column and copy name,phone")
            print("- combine users.xlsx and accounts.xlsx matching on id, copy all fields, use outer join")
            
            query = input("> ")
            request = process_natural_language(query)
            
            # Override the required arguments with values from natural language processing
            args.source = request.source_file
            args.destination = request.destination_file
            args.match_column = request.match_column
            args.columns = ",".join(request.columns_to_copy)
            args.ignore_case = request.ignore_case
            args.join = request.join_type
            args.output = request.output_file
            args.source_sheet = request.source_sheet
            args.dest_sheet = request.dest_sheet
            args.output_sheet = request.output_sheet

        # Read source file
        print(f"📖 Reading source file: {args.source}")
        source_df = read_file(args.source, sheet_name=args.source_sheet)
        
        # Read destination file
        print(f"📖 Reading destination file: {args.destination}")
        dest_df = read_file(args.destination, create_if_missing=True, 
                          sheet_name=args.dest_sheet)
        
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
        
        # Write output
        output_path = args.output or args.destination
        output_sheet = args.output_sheet or args.dest_sheet
        write_file(result_df, output_path, sheet_name=output_sheet)
        print("✨ Merge completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())