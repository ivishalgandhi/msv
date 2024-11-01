import unittest
import pandas as pd
import os
from src.file_handlers import read_file, write_file

class TestFileHandlers(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.test_df = pd.DataFrame({
            'email': ['john@example.com', 'jane@example.com'],
            'name': ['John Doe', 'Jane Smith']
        })
        
        # Create test Excel file with multiple sheets
        self.excel_path = 'test_multi_sheet.xlsx'
        with pd.ExcelWriter(self.excel_path) as writer:
            self.test_df.to_excel(writer, sheet_name='Sheet1', index=False)
            self.test_df.to_excel(writer, sheet_name='Users', index=False)
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
        
        test_files = ['test_output.csv', 'test_output.xlsx']
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_read_csv(self):
        # Write test CSV
        self.test_df.to_csv('test_output.csv', index=False)
        
        # Read and verify
        df = read_file('test_output.csv')
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['email', 'name'])

    def test_read_excel_default_sheet(self):
        df = read_file(self.excel_path)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['email', 'name'])

    def test_read_excel_specific_sheet(self):
        df = read_file(self.excel_path, sheet_name='Users')
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['email', 'name'])

    def test_read_excel_nonexistent_sheet(self):
        with self.assertRaises(ValueError):
            read_file(self.excel_path, sheet_name='NonexistentSheet')

    def test_write_csv(self):
        write_file(self.test_df, 'test_output.csv')
        self.assertTrue(os.path.exists('test_output.csv'))
        
        # Verify content
        df = pd.read_csv('test_output.csv')
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['email', 'name'])

    def test_write_excel_new_sheet(self):
        write_file(self.test_df, 'test_output.xlsx', sheet_name='TestSheet')
        self.assertTrue(os.path.exists('test_output.xlsx'))
        
        # Verify content
        df = pd.read_excel('test_output.xlsx', sheet_name='TestSheet')
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ['email', 'name'])

    def test_write_excel_existing_sheet(self):
        # Write initial data
        write_file(self.test_df, 'test_output.xlsx', sheet_name='Sheet1')
        
        # Write updated data
        updated_df = pd.DataFrame({
            'email': ['bob@example.com'],
            'name': ['Bob Wilson']
        })
        write_file(updated_df, 'test_output.xlsx', sheet_name='Sheet1')
        
        # Verify content is updated
        df = pd.read_excel('test_output.xlsx', sheet_name='Sheet1')
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'Bob Wilson')

    def test_create_missing_destination(self):
        df = read_file('nonexistent.xlsx', create_if_missing=True)
        self.assertTrue(df.empty)
        self.assertIsInstance(df, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()