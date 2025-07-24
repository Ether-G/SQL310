#!/usr/bin/env python3
"""
Inventory Management System
CSE 310 - Applied Programming - Module 6
SQL Relational Databases Project

Author: Ether-G
Date: 07/19/2025

This system provides a comprehensive inventory management solution using SQLite
with full CRUD operations, reporting, and analytics capabilities.
"""

import sys
import os
from database import InventoryDatabase
from crud_operations import CRUDOperations
from reports import InventoryReports
from ui import InventoryUI

def main():
    """Main application entry point."""
    print("=" * 60)
    print("           INVENTORY MANAGEMENT SYSTEM")
    print("=" * 60)
    print("CSE 310 - Applied Programming - Module 6")
    print("SQL Relational Databases Project")
    print("Author: Ether-G")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\nInitializing database...")
        db = InventoryDatabase("inventory.db")
        
        # Initialize CRUD operations and reports
        crud = CRUDOperations(db)
        reports = InventoryReports(db)
        
        # Check if database is empty and seed with sample data
        products = crud.get_products()
        if not products:
            print("Database is empty. Seeding with sample data...")
            db.seed_sample_data()
            print("Sample data loaded successfully!")
        
        # Initialize and start UI
        ui = InventoryUI(crud, reports)
        ui.main_menu()
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        print("Thank you for using the Inventory Management System!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your database configuration and try again.")
    finally:
        # Clean up database connection
        if 'db' in locals():
            db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main() 