# TODO

## Testing
- [ ] Fix right join test failures in [`tests/test_sample_joins.py`](tests/test_sample_joins.py)
  - Issue: KeyError "['name'] not in index"
  - Samples to test:
    - [`samples/customers.csv`](samples/customers.csv): email, name, address, phone
    - [`samples/orders.csv`](samples/orders.csv): email, order_id, amount, date
  - Expected behavior:
    - Should keep all rows from customers
    - Should match case-insensitive email values
    - Should copy name and phone columns correctly
    - Should handle column suffixes (_x, _y)

## Natural Language Testing
- [ ] Add comprehensive test cases for natural language interface:
  - Basic operations:
    - [ ] Test simple merge with default join
    - [ ] Test each join type (left, right, outer, inner)
    - [ ] Test case sensitivity options
  - Excel operations:
    - [ ] Test sheet specification
    - [ ] Test sheet copying
    - [ ] Test multi-sheet operations
  - Advanced queries:
    - [ ] Test complex column mappings
    - [ ] Test output file specification
    - [ ] Test error handling
  - Sample queries to test:
    ```text
    merge customers.csv and orders.csv using email column and copy name,phone
    combine users.xlsx and accounts.xlsx from Sheet1 to Sheet2 using id
    update inventory.xlsx from products.csv using sku, copy price,quantity ignoring case
    merge source.csv to target.csv with outer join using email and copy all fields
    ```

## Test Cases to Add
```python
def test_right_join(self):
    """Test right join (keep all customers)"""
    result = self.merger.merge(
        match_column="email",
        columns_to_copy=["name", "phone"],
        join_type="right"
    )
    
    # Should keep all customers rows

    self.assertEqual(len(result), len(self.customers_df))
    
    # Check case-insensitive matches
    self.assertTrue(
        result[result["email"].str.lower() == "john@example.com"]["name"].notna().any(),
        "Case-insensitive match failed for 'JOHN@example.com'"
    )
    
    # Verify column presence
    self.assertTrue(
        any(col for col in result.columns if "name" in col.lower()),
        f"Name column not found in: {result.columns}"
    )
    self.assertTrue(
        any(col for col in result.columns if "phone" in col.lower()),
        f"Phone column not found in: {result.columns}"
    )

## PyPI Publishing
- [ ] Prepare for PyPI release:
  1. Update version in:
     - [ ] [`setup.py`](setup.py)
     - [ ] [`pyproject.toml`](pyproject.toml)
     - [ ] [`src/version.py`](src/version.py)
  2. Check package structure:
     - [ ] Verify all required files included
     - [ ] Check dependencies in requirements.txt
     - [ ] Update README.md with latest features
  3. Build package:
     ```bash
     python -m pip install --upgrade build
     python -m build
     ```
  4. Test the build:
     - [ ] Create test virtualenv
     - [ ] Install built package
     - [ ] Run integration tests
  5. Upload to TestPyPI:
     ```bash
     python -m pip install --upgrade twine
     python -m twine upload --repository testpypi dist/*
     ```
  6. Test installation from TestPyPI:
     ```bash
     pip install --index-url https://test.pypi.org/simple/ msv
     ```
  7. Upload to PyPI:
     ```bash
     python -m twine upload dist/*
     ```
  8. Verify installation:
     ```bash
     pip install msv
     msv --version
     ```
  9. Post-release:
     - [ ] Tag release in git
     - [ ] Update documentation
     - [ ] Announce release