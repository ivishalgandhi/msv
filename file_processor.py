import csv
import sys
from typing import List, Dict, Tuple, Optional, Set
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

@dataclass
class ColumnMapping:
    source_column: str
    dest_column: str

class FileReader:
    @staticmethod
    def read_csv(file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            sys.exit(1)

class FileWriter:
    @staticmethod
    def write_csv(data: List[Dict], output_path: str, all_fields: Set[str]):
        if not data:
            print("No data to write")
            return
            
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(all_fields))
                writer.writeheader()
                writer.writerows(data)
            print(f"Successfully wrote output to {output_path}")
        except Exception as e:
            print(f"Error writing output: {str(e)}")
            sys.exit(1)

class DataMerger:
    def __init__(self, ignore_case: bool = False):
        self.ignore_case = ignore_case

    def merge_data(self, source_data: List[Dict], dest_data: List[Dict], 
                  match_column: str, column_mappings: List[ColumnMapping]) -> Tuple[List[Dict], Set[str]]:
        # Create lookup dictionary from source data
        source_lookup = {}
        for row in source_data:
            key = row[match_column].lower() if self.ignore_case else row[match_column]
            source_lookup[key] = row
        
        # Get all existing field names from destination data
        all_fields = set()
        if dest_data:
            all_fields.update(dest_data[0].keys())
        
        # Add new destination columns to field set
        for mapping in column_mappings:
            all_fields.add(mapping.dest_column)
        
        # Merge data
        result = []
        for dest_row in dest_data:
            new_row = dest_row.copy()
            # Initialize new columns with empty string
            for mapping in column_mappings:
                if mapping.dest_column not in new_row:
                    new_row[mapping.dest_column] = ""
                    
            match_key = dest_row[match_column].lower() if self.ignore_case else dest_row[match_column]
            
            if match_key in source_lookup:
                source_row = source_lookup[match_key]
                for mapping in column_mappings:
                    if mapping.source_column in source_row:
                        new_row[mapping.dest_column] = source_row[mapping.source_column]
            result.append(new_row)
            
        return result, all_fields

class NaturalLanguageParser:
    @staticmethod
    def parse_query(query: str) -> Tuple[str, str, str, List[ColumnMapping], bool]:
        query = query.lower()
        
        # Default values
        source_path = ""
        dest_path = ""
        match_column = ""
        column_mappings = []
        ignore_case = "ignore case" in query or "case insensitive" in query
        
        # Extract file paths
        words = query.split()
        for word in words:
            if word.endswith(('.csv', '.xlsx')):
                if not source_path:
                    source_path = word
                elif not dest_path:
                    dest_path = word
        
        return source_path, dest_path, match_column, column_mappings, ignore_case

class FileProcessor:
    def __init__(self):
        self.reader = FileReader()
        self.writer = FileWriter()
        self.merger = None
    
    def process_files(self, source_path: str, dest_path: str, match_column: str,
                     column_mappings: List[ColumnMapping], ignore_case: bool = False,
                     output_path: str = 'output.csv'):
        # Initialize merger with case sensitivity setting
        self.merger = DataMerger(ignore_case)
        
        # Read input files
        source_data = self.reader.read_csv(source_path)
        dest_data = self.reader.read_csv(dest_path)
        
        # Validate source columns exist
        source_columns = set(source_data[0].keys()) if source_data else set()
        for mapping in column_mappings:
            if mapping.source_column not in source_columns:
                print(f"Warning: Source column '{mapping.source_column}' not found in source file")
                continue
        
        # Merge data and get all fields including new columns
        result, all_fields = self.merger.merge_data(source_data, dest_data, match_column, column_mappings)
        
        # Write output with all fields
        self.writer.write_csv(result, output_path, all_fields)
        
        # Print information about new columns
        dest_columns = set(dest_data[0].keys()) if dest_data else set()
        new_columns = set(mapping.dest_column for mapping in column_mappings) - dest_columns
        if new_columns:
            print(f"\nCreated new columns: {', '.join(sorted(new_columns))}")

def parse_column_mappings(mapping_str: str) -> List[ColumnMapping]:
    """Parse column mappings from string format 'source1:dest1,source2:dest2'"""
    mappings = []
    if not mapping_str:
        return mappings
        
    pairs = mapping_str.split(',')
    for pair in pairs:
        if ':' in pair:
            source, dest = pair.strip().split(':')
            mappings.append(ColumnMapping(source.strip(), dest.strip()))
        else:
            # If no destination specified, use same column name
            mappings.append(ColumnMapping(pair.strip(), pair.strip()))
    return mappings

def setup_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Process CSV/XLSX files with column mapping support')
    parser.add_argument('--natural', '-n', help='Use natural language input', action='store_true')
    parser.add_argument('--source', '-s', help='Source file path')
    parser.add_argument('--destination', '-d', help='Destination file path')
    parser.add_argument('--match-column', '-m', help='Column to match between files')
    parser.add_argument('--column-mappings', '-c', 
                       help='Column mappings (format: source1:dest1,source2:dest2)')
    parser.add_argument('--ignore-case', '-i', help='Ignore case when matching', 
                       action='store_true')
    parser.add_argument('--output', '-o', help='Output file path', default='output.csv')
    return parser

def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    processor = FileProcessor()
    
    if args.natural:
        print("Enter your request in natural language")
        print("Example: merge source.csv and dest.csv using email column, "
              "copy order_date:dest_order_date,amount:total_amount, ignore case")
        query = input("> ")
        source_path, dest_path, match_column, column_mappings, ignore_case = (
            NaturalLanguageParser.parse_query(query)
        )
        
        # Ask for missing information
        if not source_path:
            source_path = input("Source file path: ")
        if not dest_path:
            dest_path = input("Destination file path: ")
        if not match_column:
            match_column = input("Column to match: ")
        if not column_mappings:
            mapping_str = input("Column mappings (source:dest,source2:dest2): ")
            column_mappings = parse_column_mappings(mapping_str)
    else:
        source_path = args.source
        dest_path = args.destination
        match_column = args.match_column
        column_mappings = parse_column_mappings(args.column_mappings)
        ignore_case = args.ignore_case
    
    # Process files
    processor.process_files(
        source_path,
        dest_path,
        match_column,
        column_mappings,
        ignore_case,
        args.output
    )

if __name__ == "__main__":
    main()