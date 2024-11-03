import unittest
import pandas as pd
from pathlib import Path
from src.file_handlers import read_file
from src.data_merger import DataMerger

class TestSampleJoins(unittest.TestCase):
    def setUp(self):
        """Set up test data from sample files"""
        samples_dir = Path(__file__).parent.parent / "samples"
        self.customers_df = read_file(str(samples_dir / "customers.csv"))
        self.orders_df = read_file(str(samples_dir / "orders.csv"))
        self.merger = DataMerger(self.customers_df, self.orders_df)

    def test_left_join(self):
        """Test left join (keep all orders)"""
        result = self.merger.merge(
            match_column="email",
            columns_to_copy=["name", "phone"],
            join_type="left"
        )
        # Should keep all orders rows
        self.assertEqual(len(result), len(self.orders_df))
        # Check if columns exist (handling potential suffixes)
        self.assertTrue(
            any("name" in col for col in result.columns) and 
            any("phone" in col for col in result.columns)
        )

    def test_right_join(self):
        """Test right join (keep all customers)"""
        # First verify both dataframes have the required columns
        self.assertTrue("email" in self.customers_df.columns, 
                       f"Match column 'email' not found in customers. Available: {list(self.customers_df.columns)}")
        self.assertTrue("email" in self.orders_df.columns,
                       f"Match column 'email' not found in orders. Available: {list(self.orders_df.columns)}")
        
        try:
            # Perform right join - should keep all records from customers
            result = self.merger.merge(
                match_column="email",
                columns_to_copy=["name", "phone"],  # These columns are from customers.csv
                join_type="right"
            )
            
            # Should keep all customers rows
            self.assertEqual(len(result), len(self.customers_df))
            
            # Verify both copied columns exist in result (with potential suffixes)
            result_columns = list(result.columns)
            self.assertTrue(
                any("name" in col for col in result_columns) and
                any("phone" in col for col in result_columns),
                f"Expected columns not found. Available: {result_columns}"
            )
            
            # Verify order columns are also present
            self.assertTrue(
                "order_id" in result_columns and
                "amount" in result_columns and
                "date" in result_columns,
                f"Order columns missing. Available: {result_columns}"
            )
            
        except Exception as e:
            self.fail(f"Merge operation failed: {str(e)}\n"
                     f"Customers columns: {list(self.customers_df.columns)}\n"
                     f"Orders columns: {list(self.orders_df.columns)}")

    def test_outer_join(self):
        """Test outer join (keep all records)"""
        result = self.merger.merge(
            match_column="email",
            columns_to_copy=["name", "phone"],
            join_type="outer"
        )
        # Should include all unique emails
        unique_emails = set(self.customers_df["email"]).union(set(self.orders_df["email"]))
        self.assertEqual(len(result), len(unique_emails))

    def test_inner_join(self):
        """Test inner join (keep only matches)"""
        result = self.merger.merge(
            match_column="email",
            columns_to_copy=["name", "phone"],
            join_type="inner"
        )
        # Should only include matching emails
        matching_emails = set(self.customers_df["email"]).intersection(set(self.orders_df["email"]))
        self.assertEqual(len(result), len(matching_emails))

    def test_case_sensitivity(self):
        """Test case-sensitive and insensitive matching"""
        # Case-sensitive (default)
        result_sensitive = self.merger.merge(
            match_column="email",
            columns_to_copy=["name"],
            ignore_case=False
        )
        
        # Case-insensitive
        result_insensitive = self.merger.merge(
            match_column="email",
            columns_to_copy=["name"],
            ignore_case=True
        )
        
        # Get actual name column (handling suffixes)
        name_col_sensitive = next(col for col in result_sensitive.columns if "name" in col)
        name_col_insensitive = next(col for col in result_insensitive.columns if "name" in col)
        
        # Case-insensitive should find more matches
        self.assertGreaterEqual(
            result_insensitive[name_col_insensitive].notna().sum(),
            result_sensitive[name_col_sensitive].notna().sum()
        )

    def test_column_copying(self):
        """Test copying different columns"""
        # Single column
        result_single = self.merger.merge(
            match_column="email",
            columns_to_copy=["name"],
            join_type="left"
        )
        # Check if name column exists (handling suffixes)
        self.assertTrue(any("name" in col for col in result_single.columns))
        
        # Multiple columns
        result_multiple = self.merger.merge(
            match_column="email",
            columns_to_copy=["name", "phone"],
            join_type="left"
        )
        # Check if both columns exist (handling suffixes)
        self.assertTrue(
            any("name" in col for col in result_multiple.columns) and
            any("phone" in col for col in result_multiple.columns)
        )

if __name__ == "__main__":
    unittest.main()