import pandas as pd
from typing import List, Dict, Literal

JoinType = Literal['left', 'right', 'outer', 'inner', 'left_outer', 'right_outer']

class DataMerger:
    def __init__(self, source_df: pd.DataFrame, dest_df: pd.DataFrame):
        self.source_df = source_df
        self.dest_df = dest_df

    def merge(self, match_column: str, columns_to_copy: List[str], 
             ignore_case: bool = False, join_type: JoinType = 'left') -> pd.DataFrame:
        """
        Merge data from source to destination DataFrame based on match_column.
        
        Args:
            match_column: Column name to match between source and destination
            columns_to_copy: List of column names from source to copy to destination
            ignore_case: Whether to ignore case when matching
            join_type: Type of join to perform:
                - 'left': Keep all rows from destination (default)
                - 'right': Keep all rows from source
                - 'outer': Keep all rows from both files
                - 'inner': Keep only matching rows
                - 'left_outer': Same as 'left' (alias for pandas compatibility)
                - 'right_outer': Same as 'right' (alias for pandas compatibility)
        """
        # Validate columns exist in source
        missing_cols = [col for col in columns_to_copy if col not in self.source_df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in source file: {', '.join(missing_cols)}")

        # For empty destination DataFrame, create it with necessary columns
        if self.dest_df.empty:
            # Create DataFrame with match column
            self.dest_df = pd.DataFrame(columns=[match_column])
            # Copy unique values from source match column
            unique_values = self.source_df[match_column].unique()
            self.dest_df[match_column] = unique_values
            print(f"Created new destination file with {len(unique_values)} rows")

        # Create copies for case-insensitive matching if needed
        if ignore_case:
            self.source_df = self.source_df.copy()
            self.dest_df = self.dest_df.copy()
            self.source_df[match_column] = self.source_df[match_column].str.lower()
            self.dest_df[match_column] = self.dest_df[match_column].str.lower()

        # Normalize join type (handle aliases)
        if join_type == 'left_outer':
            join_type = 'left'
        elif join_type == 'right_outer':
            join_type = 'right'

        # Perform the merge based on join type
        if join_type == 'right':
            # For right join, swap source and destination
            result = pd.merge(
                self.source_df,
                self.dest_df,
                on=match_column,
                how='left'
            )
            # Reorder columns to match destination-first pattern
            dest_cols = [col for col in self.dest_df.columns if col != match_column]
            source_cols = [col for col in columns_to_copy if col not in dest_cols]
            result = result[[match_column] + dest_cols + source_cols]
        else:
            result = pd.merge(
                self.dest_df,
                self.source_df[columns_to_copy + [match_column]],
                on=match_column,
                how=join_type
            )

        # Report new columns
        new_columns = set(columns_to_copy) - set(self.dest_df.columns)
        if new_columns:
            print(f"Added new columns: {', '.join(sorted(new_columns))}")

        # Report row changes
        rows_before = len(self.dest_df)
        rows_after = len(result)
        if rows_after != rows_before:
            print(f"Rows changed: {rows_before} → {rows_after} ({rows_after - rows_before:+d})")

        return result