import unittest
import pandas as pd
from src.data_merger import DataMerger

class TestDataMerger(unittest.TestCase):
    def setUp(self):
        self.source_data = pd.DataFrame({
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'phone': ['555-0101', '555-0102', '555-0103']
        })
        
        self.dest_data = pd.DataFrame({
            'email': ['JOHN@EXAMPLE.COM', 'jane@example.com', 'alice@example.com'],
            'order_id': ['ORD-001', 'ORD-002', 'ORD-003']
        })
        
    def test_all_join_types(self):
        merger = DataMerger(self.source_data, self.dest_data)
        join_types = ['left', 'right', 'outer', 'inner']
        expected_rows = {
            'left': 3,   # Keep all destination rows
            'right': 3,  # Keep all source rows
            'outer': 4,  # Keep all unique rows
            'inner': 2   # Keep only matching rows
        }
        
        for join_type in join_types:
            result = merger.merge(
                match_column='email',
                columns_to_copy=['name', 'phone'],
                join_type=join_type
            )
            self.assertEqual(len(result), expected_rows[join_type])
            
    def test_case_sensitivity(self):
        merger = DataMerger(self.source_data, self.dest_data)
        
        # Without ignore_case
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name'],
            ignore_case=False
        )
        self.assertEqual(len(result[result['name'].notna()]), 1)
        
        # With ignore_case
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name'],
            ignore_case=True
        )
        self.assertEqual(len(result[result['name'].notna()]), 2)
        
    def test_empty_dataframes(self):
        empty_df = pd.DataFrame(columns=['email', 'name'])
        
        # Empty source
        merger = DataMerger(empty_df, self.dest_data)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name']
        )
        self.assertEqual(len(result), len(self.dest_data))
        
        # Empty destination
        merger = DataMerger(self.source_data, empty_df)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name']
        )
        self.assertEqual(len(result), len(self.source_data))
        
    def test_error_handling(self):
        merger = DataMerger(self.source_data, self.dest_data)
        
        # Test invalid column
        with self.assertRaises(ValueError):
            merger.merge(
                match_column='email',
                columns_to_copy=['nonexistent']
            )
            
        # Test invalid join type
        with self.assertRaises(ValueError):
            merger.merge(
                match_column='email',
                columns_to_copy=['name'],
                join_type='invalid'
            )

if __name__ == '__main__':
    unittest.main()