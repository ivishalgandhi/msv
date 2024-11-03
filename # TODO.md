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