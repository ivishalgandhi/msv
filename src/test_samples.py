import unittest
import pandas as pd
from pathlib import Path
import os

class TestSamples(unittest.TestCase):
    def setUp(self):
        # Get the samples directory path
        self.samples_dir = Path(__file__).parent.parent / "samples"
        self.customers_path = self.samples_dir / "customers.csv"
        self.orders_path = self.samples_dir / "orders.csv"

    def test_sample_files_exist(self):
        """Test that sample files exist"""
        self.assertTrue(self.customers_path.exists(), "customers.csv not found")
        self.assertTrue(self.orders_path.exists(), "orders.csv not found")

    def test_customers_file_structure(self):
        """Test customers.csv structure and content"""
        df = pd.read_csv(self.customers_path)
        
        # Check columns
        expected_columns = ["email", "name", "address", "phone"]
        self.assertEqual(list(df.columns), expected_columns)
        
        # Check data types
        self.assertEqual(df["email"].dtype, "object")
        self.assertEqual(df["name"].dtype, "object")
        
        # Check not empty
        self.assertGreater(len(df), 0, "customers.csv is empty")
        
        # Check sample data
        self.assertTrue(any(df["email"].str.contains("@example.com")))

    def test_orders_file_structure(self):
        """Test orders.csv structure and content"""
        df = pd.read_csv(self.orders_path)
        
        # Check columns
        expected_columns = ["email", "order_id", "amount", "date"]
        self.assertEqual(list(df.columns), expected_columns)
        
        # Check data types
        self.assertEqual(df["email"].dtype, "object")
        self.assertEqual(df["order_id"].str.startswith("ORD-").all(), True)
        
        # Check not empty
        self.assertGreater(len(df), 0, "orders.csv is empty")
        
        # Test data relationships
        self.assertTrue(df["amount"].astype(float).all(), "Invalid amount values")
        self.assertTrue(pd.to_datetime(df["date"], errors='coerce').notna().all(), 
                       "Invalid date values")

    def test_file_relationships(self):
        """Test relationships between sample files"""
        customers = pd.read_csv(self.customers_path)
        orders = pd.read_csv(self.orders_path)
        
        # Check email as foreign key
        customer_emails = set(customers["email"].str.lower())
        order_emails = set(orders["email"].str.lower())
        
        # Some orders should match customers
        common_emails = customer_emails.intersection(order_emails)
        self.assertGreater(len(common_emails), 0, 
                          "No matching emails between customers and orders")

if __name__ == '__main__':
    unittest.main()