import unittest
import pandas as pd
from src.data_merger import DataMerger

class TestDataMerger(unittest.TestCase):
    def setUp(self):
        # Sample source data
        self.source_data = pd.DataFrame({
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'phone': ['555-0101', '555-0102', '555-0103']
        })
        
        # Sample destination data
        self.dest_data = pd.DataFrame({
            'email': ['JOHN@EXAMPLE.COM', 'jane@example.com', 'alice@example.com'],
            'order_id': ['ORD-001', 'ORD-002', 'ORD-003']
        })

    def test_left_join(self):
        merger = DataMerger(self.source_data, self.dest_data)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name', 'phone'],
            ignore_case=True,
            join_type='left'
        )
        
        self.assertEqual(len(result), 3)  # Should maintain destination rows
        self.assertTrue('name' in result.columns)
        self.assertTrue('phone' in result.columns)
        self.assertEqual(result.iloc[0]['name'], 'John Doe')  # Case-insensitive match

    def test_outer_join(self):
        merger = DataMerger(self.source_data, self.dest_data)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name', 'phone'],
            join_type='outer'
        )
        
        self.assertEqual(len(result), 4)  # All unique emails from both sources
        self.assertTrue(pd.isna(result[result['email'] == 'bob@example.com']['order_id'].iloc[0]))

    def test_inner_join(self):
        merger = DataMerger(self.source_data, self.dest_data)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name', 'phone'],
            ignore_case=True,
            join_type='inner'
        )
        
        self.assertEqual(len(result), 2)  # Only matching rows
        self.assertEqual(set(result['email']), {'JOHN@EXAMPLE.COM', 'jane@example.com'})

    def test_case_sensitivity(self):
        # Test without ignore_case
        merger = DataMerger(self.source_data, self.dest_data)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name', 'phone'],
            ignore_case=False,
            join_type='inner'
        )
        
        self.assertEqual(len(result), 1)  # Only exact matches
        self.assertEqual(result.iloc[0]['email'], 'jane@example.com')

    def test_missing_columns(self):
        merger = DataMerger(self.source_data, self.dest_data)
        with self.assertRaises(ValueError):
            merger.merge(
                match_column='email',
                columns_to_copy=['name', 'nonexistent_column'],
                join_type='left'
            )

    def test_empty_destination(self):
        empty_dest = pd.DataFrame(columns=['email', 'order_id'])
        merger = DataMerger(self.source_data, empty_dest)
        result = merger.merge(
            match_column='email',
            columns_to_copy=['name', 'phone'],
            join_type='left'
        )
        
        self.assertEqual(len(result), 3)  # Should contain all source rows
        self.assertTrue(all(pd.isna(result['order_id'])))

if __name__ == '__main__':
    unittest.main()