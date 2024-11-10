# Create samples/create_excel_samples.py

import pandas as pd
from pathlib import Path

def create_sample_excel_files():
    samples_dir = Path(__file__).parent
    
    # Create customers.xlsx
    customers_df = pd.DataFrame({
        'email': [
            'john@example.com',
            'jane@example.com', 
            'bob@example.com',
            'alice@example.com',
            'mary@example.com'
        ],
        'name': [
            'John Doe',
            'Jane Smith',
            'Bob Wilson',
            'Alice Brown',
            'Mary Johnson'
        ],
        'address': [
            '123 Main St',
            '456 Oak Rd',
            '789 Pine Ave',
            '321 Elm St',
            '654 Maple Dr'
        ],
        'phone': [
            '555-0101',
            '555-0102',
            '555-0103',
            '555-0104',
            '555-0105'
        ]
    })
    
    # Save customers.xlsx with multiple sheets
    with pd.ExcelWriter(samples_dir / 'customers.xlsx') as writer:
        customers_df.to_excel(writer, sheet_name='Customers', index=False)
        # Add a sheet with filtered data
        customers_df[['email', 'name']].to_excel(writer, sheet_name='Basic Info', index=False)
        # Add a sheet with different case
        customers_df.columns = [col.upper() for col in customers_df.columns]
        customers_df.to_excel(writer, sheet_name='UPPERCASE', index=False)
    
    # Create orders.xlsx
    orders_df = pd.DataFrame({
        'email': [
            'john@example.com',
            'jane@example.com',
            'bob@example.com',
            'alice@example.com'
        ],
        'order_id': [
            'ORD-001',
            'ORD-002',
            'ORD-003',
            'ORD-004'
        ],
        'amount': [
            100.0,
            200.0,
            150.0,
            300.0
        ],
        'date': [
            '2024-01-15',
            '2024-01-16',
            '2024-01-17',
            '2024-01-18'
        ]
    })
    
    # Save orders.xlsx with multiple sheets
    with pd.ExcelWriter(samples_dir / 'orders.xlsx') as writer:
        orders_df.to_excel(writer, sheet_name='Orders', index=False)
        # Add a sheet with monthly data
        orders_df['month'] = pd.to_datetime(orders_df['date']).dt.strftime('%B')
        orders_df.to_excel(writer, sheet_name='Monthly', index=False)
        # Add a sheet with case variations
        orders_df.columns = [col.title() for col in orders_df.columns]
        orders_df.to_excel(writer, sheet_name='Title Case', index=False)

if __name__ == '__main__':
    create_sample_excel_files()