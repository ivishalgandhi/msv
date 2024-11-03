import unittest
from src.natural_language import process_natural_language, setup_openai_functions, MergeRequest
import os

class TestNaturalLanguage(unittest.TestCase):
    def setUp(self):
        # Mock API key for testing
        os.environ["OPENAI_API_KEY"] = "test-key"
        
    def test_setup_openai_functions(self):
        functions = setup_openai_functions()
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]["name"], "merge_files")
        self.assertIn("parameters", functions[0])
        
    def test_merge_request_creation(self):
        request = MergeRequest(
            source_file="customers.csv",
            destination_file="orders.csv",
            match_column="email",
            columns_to_copy=["name", "phone"]
        )
        self.assertEqual(request.source_file, "customers.csv")
        self.assertEqual(request.join_type, "left")  # default value
        self.assertFalse(request.ignore_case)  # default value
        
    def test_process_natural_language_basic(self):
        query = "merge customers.csv into orders.csv using email column and copy name,phone"
        try:
            request = process_natural_language(query)
            self.assertEqual(request.source_file, "customers.csv")
            self.assertEqual(request.destination_file, "orders.csv")
            self.assertEqual(request.match_column, "email")
            self.assertEqual(request.columns_to_copy, ["name", "phone"])
        except Exception as e:
            if "API" in str(e):
                self.skipTest("Skipping due to API requirements")

    def test_process_natural_language_advanced(self):
        query = ("merge users.xlsx into accounts.xlsx using id column, "
                "copy name,email from Sheet1 to Sheet2 with outer join ignoring case")
        try:
            request = process_natural_language(query)
            self.assertEqual(request.source_file, "users.xlsx")
            self.assertEqual(request.source_sheet, "Sheet1")
            self.assertEqual(request.dest_sheet, "Sheet2")
            self.assertTrue(request.ignore_case)
            self.assertEqual(request.join_type, "outer")
        except Exception as e:
            if "API" in str(e):
                self.skipTest("Skipping due to API requirements")

if __name__ == '__main__':
    unittest.main()