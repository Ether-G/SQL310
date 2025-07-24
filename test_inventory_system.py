#!/usr/bin/env python3
"""
Unit Tests for Inventory Management System
CSE 310 - Applied Programming - Module 6

This test suite covers all functionality of the inventory management system
including CRUD operations, database operations, reports, and edge cases.

Author: Ether-G
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# Import the modules to test
from database import InventoryDatabase
from crud_operations import CRUDOperations
from reports import InventoryReports

class TestInventorySystem(unittest.TestCase):
    """Test suite for the Inventory Management System."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database for testing
        self.test_db_path = "test_inventory.db"
        self.db = InventoryDatabase(self.test_db_path)
        self.crud = CRUDOperations(self.db)
        self.reports = InventoryReports(self.db)
        
        # Seed with test data
        self.db.seed_sample_data()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Close database connection
        if hasattr(self, 'db'):
            self.db.close()
        
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_initialization(self):
        """Test database initialization and table creation."""
        # Test that tables exist
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.db.cursor.fetchall()]
        
        expected_tables = ['categories', 'suppliers', 'products', 'inventory_transactions']
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_category_crud_operations(self):
        """Test CRUD operations for categories."""
        # Test Create
        category_id = self.crud.create_category("Test Category", "Test Description")
        self.assertIsNotNone(category_id)
        self.assertGreater(category_id, 0)
        
        # Test Read
        category = self.crud.get_category_by_id(category_id)
        self.assertIsNotNone(category)
        self.assertEqual(category['name'], "Test Category")
        self.assertEqual(category['description'], "Test Description")
        
        # Test Update
        success = self.crud.update_category(category_id, "Updated Category", "Updated Description")
        self.assertTrue(success)
        
        updated_category = self.crud.get_category_by_id(category_id)
        self.assertEqual(updated_category['name'], "Updated Category")
        self.assertEqual(updated_category['description'], "Updated Description")
        
        # Test Delete
        success = self.crud.delete_category(category_id)
        self.assertTrue(success)
        
        deleted_category = self.crud.get_category_by_id(category_id)
        self.assertIsNone(deleted_category)
    
    def test_supplier_crud_operations(self):
        """Test CRUD operations for suppliers."""
        # Test Create
        supplier_id = self.crud.create_supplier("Test Supplier", "test@supplier.com", "123 Test St")
        self.assertIsNotNone(supplier_id)
        self.assertGreater(supplier_id, 0)
        
        # Test Read
        supplier = self.crud.get_supplier_by_id(supplier_id)
        self.assertIsNotNone(supplier)
        self.assertEqual(supplier['name'], "Test Supplier")
        self.assertEqual(supplier['contact_info'], "test@supplier.com")
        self.assertEqual(supplier['address'], "123 Test St")
        
        # Test Update
        success = self.crud.update_supplier(supplier_id, "Updated Supplier", "updated@supplier.com", "456 Updated St")
        self.assertTrue(success)
        
        updated_supplier = self.crud.get_supplier_by_id(supplier_id)
        self.assertEqual(updated_supplier['name'], "Updated Supplier")
        self.assertEqual(updated_supplier['contact_info'], "updated@supplier.com")
        self.assertEqual(updated_supplier['address'], "456 Updated St")
        
        # Test Delete
        success = self.crud.delete_supplier(supplier_id)
        self.assertTrue(success)
        
        deleted_supplier = self.crud.get_supplier_by_id(supplier_id)
        self.assertIsNone(deleted_supplier)
    
    def test_product_crud_operations(self):
        """Test CRUD operations for products."""
        # Get a category first
        categories = self.crud.get_categories()
        self.assertGreater(len(categories), 0)
        category_id = categories[0]['id']
        
        # Test Create
        product_id = self.crud.create_product("Test Product", "Test Description", category_id, 99.99, 5)
        self.assertIsNotNone(product_id)
        self.assertGreater(product_id, 0)
        
        # Test Read
        product = self.crud.get_product_by_id(product_id)
        self.assertIsNotNone(product)
        self.assertEqual(product['name'], "Test Product")
        self.assertEqual(product['description'], "Test Description")
        self.assertEqual(product['price'], 99.99)
        self.assertEqual(product['reorder_level'], 5)
        
        # Test Update
        success = self.crud.update_product(product_id, "Updated Product", "Updated Description", category_id, 149.99, 10)
        self.assertTrue(success)
        
        updated_product = self.crud.get_product_by_id(product_id)
        self.assertEqual(updated_product['name'], "Updated Product")
        self.assertEqual(updated_product['description'], "Updated Description")
        self.assertEqual(updated_product['price'], 149.99)
        self.assertEqual(updated_product['reorder_level'], 10)
        
        # Test Delete
        success = self.crud.delete_product(product_id)
        self.assertTrue(success)
        
        deleted_product = self.crud.get_product_by_id(product_id)
        self.assertIsNone(deleted_product)
    
    def test_transaction_crud_operations(self):
        """Test CRUD operations for transactions."""
        # Get a product first
        products = self.crud.get_products()
        self.assertGreater(len(products), 0)
        product_id = products[0]['id']
        
        # Get a supplier
        suppliers = self.crud.get_suppliers()
        self.assertGreater(len(suppliers), 0)
        supplier_id = suppliers[0]['id']
        
        # Test Create
        transaction_id = self.crud.create_transaction(product_id, "IN", 10, supplier_id, "Test transaction")
        self.assertIsNotNone(transaction_id)
        self.assertGreater(transaction_id, 0)
        
        # Test Read
        transaction = self.crud.get_transaction_by_id(transaction_id)
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['product_id'], product_id)
        self.assertEqual(transaction['transaction_type'], "IN")
        self.assertEqual(transaction['quantity'], 10)
        self.assertEqual(transaction['supplier_id'], supplier_id)
        self.assertEqual(transaction['notes'], "Test transaction")
        
        # Test Update
        success = self.crud.update_transaction(transaction_id, product_id, "OUT", 5, None, "Updated transaction")
        self.assertTrue(success)
        
        updated_transaction = self.crud.get_transaction_by_id(transaction_id)
        self.assertEqual(updated_transaction['transaction_type'], "OUT")
        self.assertEqual(updated_transaction['quantity'], 5)
        self.assertEqual(updated_transaction['notes'], "Updated transaction")
        
        # Test Delete
        success = self.crud.delete_transaction(transaction_id)
        self.assertTrue(success)
        
        deleted_transaction = self.crud.get_transaction_by_id(transaction_id)
        self.assertIsNone(deleted_transaction)
    
    def test_inventory_calculations(self):
        """Test inventory stock calculations."""
        # Get a product
        products = self.crud.get_products()
        self.assertGreater(len(products), 0)
        product_id = products[0]['id']
        
        # Get initial stock
        initial_stock = self.crud.get_product_stock(product_id)
        
        # Add stock
        self.crud.create_transaction(product_id, "IN", 10, None, "Test stock in")
        stock_after_in = self.crud.get_product_stock(product_id)
        self.assertEqual(stock_after_in, initial_stock + 10)
        
        # Remove stock
        self.crud.create_transaction(product_id, "OUT", 3, None, "Test stock out")
        stock_after_out = self.crud.get_product_stock(product_id)
        self.assertEqual(stock_after_out, initial_stock + 10 - 3)
    
    def test_product_search(self):
        """Test product search functionality."""
        # Search for existing products
        results = self.crud.search_products("Laptop")
        self.assertGreater(len(results), 0)
        self.assertIn("Laptop", results[0]['name'])
        
        # Search for non-existent products
        results = self.crud.search_products("NonExistentProduct")
        self.assertEqual(len(results), 0)
        
        # Search by description
        results = self.crud.search_products("Python")
        self.assertGreater(len(results), 0)
    
    def test_reports_generation(self):
        """Test report generation functionality."""
        # Test inventory report
        inventory_report = self.reports.generate_inventory_report()
        self.assertIsInstance(inventory_report, str)
        self.assertGreater(len(inventory_report), 0)
        
        # Test low stock report
        low_stock_report = self.reports.generate_low_stock_report()
        self.assertIsInstance(low_stock_report, str)
        
        # Test inventory value report
        value_report = self.reports.generate_inventory_value_report()
        self.assertIsInstance(value_report, str)
        self.assertGreater(len(value_report), 0)
        
        # Test transaction report
        transaction_report = self.reports.generate_transaction_report(30)
        self.assertIsInstance(transaction_report, str)
        
        # Test category report
        category_report = self.reports.generate_category_report()
        self.assertIsInstance(category_report, str)
        self.assertGreater(len(category_report), 0)
        
        # Test supplier report
        supplier_report = self.reports.generate_supplier_report()
        self.assertIsInstance(supplier_report, str)
        
        # Test monthly summary
        monthly_report = self.reports.generate_monthly_summary()
        self.assertIsInstance(monthly_report, str)
        
        # Test comprehensive report
        comprehensive_report = self.reports.generate_comprehensive_report()
        self.assertIsInstance(comprehensive_report, str)
        self.assertGreater(len(comprehensive_report), 0)
    
    def test_database_queries(self):
        """Test complex database queries."""
        # Test current inventory query
        inventory = self.db.get_current_inventory()
        self.assertIsInstance(inventory, list)
        self.assertGreater(len(inventory), 0)
        
        # Test low stock products query
        low_stock = self.db.get_low_stock_products()
        self.assertIsInstance(low_stock, list)
        
        # Test inventory value calculation
        value_data = self.db.get_inventory_value()
        self.assertIsInstance(value_data, dict)
        self.assertIn('total_value', value_data)
        self.assertIn('avg_price', value_data)
        self.assertIn('total_products', value_data)
        
        # Test transaction history
        transactions = self.db.get_transaction_history(30)
        self.assertIsInstance(transactions, list)
    
    def test_data_integrity(self):
        """Test data integrity constraints."""
        # Test unique category names
        self.crud.create_category("Unique Category")
        # Try to create another category with the same name
        category_id = self.crud.create_category("Unique Category")
        self.assertIsNone(category_id)  # Should fail due to unique constraint
        
        # Test foreign key constraints
        # Try to create a product with non-existent category
        product_id = self.crud.create_product("Test", "Test", 99999, 10.0, 5)
        self.assertIsNone(product_id)  # Should fail due to foreign key constraint
        
        # Test transaction type validation
        products = self.crud.get_products()
        if products:
            product_id = products[0]['id']
            # Try to create transaction with invalid type
            transaction_id = self.crud.create_transaction(product_id, "INVALID", 10)
            self.assertIsNone(transaction_id)  # Should fail due to check constraint
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with empty data
        empty_db = InventoryDatabase("empty_test.db")
        empty_crud = CRUDOperations(empty_db)
        
        # Test getting products from empty database
        products = empty_crud.get_products()
        self.assertEqual(len(products), 0)
        
        # Test getting categories from empty database
        categories = empty_crud.get_categories()
        self.assertEqual(len(categories), 0)
        
        # Test reports with empty data
        empty_reports = InventoryReports(empty_db)
        inventory_report = empty_reports.generate_inventory_report()
        self.assertIn("No inventory data available", inventory_report)
        
        # Clean up
        empty_db.close()
        if os.path.exists("empty_test.db"):
            os.remove("empty_test.db")
    
    def test_deletion_constraints(self):
        """Test deletion constraints and dependencies."""
        # Get a category that has products
        categories = self.crud.get_categories()
        self.assertGreater(len(categories), 0)
        category_id = categories[0]['id']
        
        # Try to delete a category that has products
        success = self.crud.delete_category(category_id)
        self.assertFalse(success)  # Should fail due to foreign key constraint
        
        # Get a product that has transactions
        products = self.crud.get_products()
        self.assertGreater(len(products), 0)
        product_id = products[0]['id']
        
        # Try to delete a product that has transactions
        success = self.crud.delete_product(product_id)
        self.assertFalse(success)  # Should fail due to foreign key constraint
        
        # Get a supplier that has transactions
        suppliers = self.crud.get_suppliers()
        self.assertGreater(len(suppliers), 0)
        supplier_id = suppliers[0]['id']
        
        # Try to delete a supplier that has transactions
        success = self.crud.delete_supplier(supplier_id)
        self.assertFalse(success)  # Should fail due to foreign key constraint
    
    def test_sample_data_integrity(self):
        """Test that sample data is properly loaded and consistent."""
        # Check that sample data exists
        categories = self.crud.get_categories()
        self.assertGreaterEqual(len(categories), 4)  # Should have at least 4 categories
        
        suppliers = self.crud.get_suppliers()
        self.assertGreaterEqual(len(suppliers), 4)  # Should have at least 4 suppliers
        
        products = self.crud.get_products()
        self.assertGreaterEqual(len(products), 4)  # Should have at least 4 products
        
        transactions = self.crud.get_transactions()
        self.assertGreaterEqual(len(transactions), 6)  # Should have at least 6 transactions
        
        # Check that products have valid category references
        for product in products:
            if product['category_id']:
                category = self.crud.get_category_by_id(product['category_id'])
                self.assertIsNotNone(category)
        
        # Check that transactions have valid product references
        for transaction in transactions:
            product = self.crud.get_product_by_id(transaction['product_id'])
            self.assertIsNotNone(product)
            
            if transaction['supplier_id']:
                supplier = self.crud.get_supplier_by_id(transaction['supplier_id'])
                self.assertIsNotNone(supplier)

def run_performance_tests():
    """Run performance tests to ensure the system can handle larger datasets."""
    print("\n" + "="*60)
    print("PERFORMANCE TESTS")
    print("="*60)
    
    # Create a test database
    test_db = InventoryDatabase("performance_test.db")
    crud = CRUDOperations(test_db)
    
    try:
        # Test with larger datasets
        print("Creating 100 categories...")
        for i in range(100):
            crud.create_category(f"Category {i}", f"Description {i}")
        
        print("Creating 50 suppliers...")
        for i in range(50):
            crud.create_supplier(f"Supplier {i}", f"contact{i}@test.com", f"Address {i}")
        
        print("Creating 200 products...")
        categories = crud.get_categories()
        for i in range(200):
            category_id = categories[i % len(categories)]['id']
            crud.create_product(f"Product {i}", f"Description {i}", category_id, 10.0 + i, 5)
        
        print("Creating 500 transactions...")
        products = crud.get_products()
        suppliers = crud.get_suppliers()
        for i in range(500):
            product_id = products[i % len(products)]['id']
            supplier_id = suppliers[i % len(suppliers)]['id'] if i % 2 == 0 else None
            transaction_type = "IN" if i % 3 == 0 else "OUT"
            crud.create_transaction(product_id, transaction_type, 1 + (i % 10), supplier_id, f"Transaction {i}")
        
        print("Generating reports...")
        reports = InventoryReports(test_db)
        
        start_time = datetime.now()
        inventory_report = reports.generate_inventory_report()
        end_time = datetime.now()
        print(f"Inventory report: {(end_time - start_time).total_seconds():.3f}s")
        
        start_time = datetime.now()
        comprehensive_report = reports.generate_comprehensive_report()
        end_time = datetime.now()
        print(f"Comprehensive report: {(end_time - start_time).total_seconds():.3f}s")
        
        print("Performance tests completed")
        
    finally:
        test_db.close()
        if os.path.exists("performance_test.db"):
            os.remove("performance_test.db")

if __name__ == '__main__':
    # Run unit tests
    print("="*60)
    print("INVENTORY MANAGEMENT SYSTEM - UNIT TESTS")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestInventorySystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    # Run performance tests if all unit tests pass
    if result.wasSuccessful():
        run_performance_tests()
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("="*60) 