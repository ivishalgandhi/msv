import unittest
import pandas as pd
import os
from src.file_handlers import read_file, write_file

class TestFileHandlers(unittest.TestCase):
    def setUp(self):
        self.test_df = pd.DataFrame({
            'email': ['test@example.com'],
            'name': ['Test User']
        })
        
        # Create test files
        self.csv_path = 'test_data.csv'
        self.excel_path = 'test_data.xlsx'
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(self.excel_path) as writer:
            self.test_df.to_excel(writer, sheet_name='Sheet1', index=False)
            self.test_df.to_excel(writer, sheet_name='Custom', index=False)
            
    def tearDown(self):
        # Clean up test files
        for file in [self.csv_path, self.excel_path, 'output.csv', 'output.xlsx']:
            if os.path.exists(file):
                os.remove(file)
                
    def test_read_csv_basic(self):
        self.test_df.to_csv(self.csv_path, index=False)
        df = read_file(self.csv_path)
        self.assertEqual(len(df), 1)
        self.assertEqual(list(df.columns), ['email', 'name'])
        
    def test_read_excel_sheets(self):
        # Default sheet
        df = read_file(self.excel_path)
        self.assertEqual(len(df), 1)
        
        # Specific sheet
        df = read_file(self.excel_path, sheet_name='Custom')
        self.assertEqual(len(df), 1)
        
        # Invalid sheet
        with self.assertRaises(ValueError):
            read_file(self.excel_path, sheet_name='NonExistent')
            
    def test_write_operations(self):
        # Write CSV
        write_file(self.test_df, 'output.csv')
        self.assertTrue(os.path.exists('output.csv'))
        
        # Write Excel with sheet
        write_file(self.test_df, 'output.xlsx', sheet_name='TestSheet')
        self.assertTrue(os.path.exists('output.xlsx'))
        df = pd.read_excel('output.xlsx', sheet_name='TestSheet')
        self.assertEqual(len(df), 1)
        
    def test_file_creation(self):
        # Test create_if_missing
        df = read_file('nonexistent.csv', create_if_missing=True)
        self.assertTrue(df.empty)
        
        # Test without create_if_missing
        with self.assertRaises(FileNotFoundError):
            read_file('nonexistent.csv')

if __name__ == '__main__':
    unittest.main()