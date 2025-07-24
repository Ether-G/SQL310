#!/usr/bin/env python3
"""
Test Runner for Inventory Management System
CSE 310 - Applied Programming - Module 6

This script provides an easy way to run the unit tests with different options.

Author: Ether-G
"""

import sys
import os
import subprocess
import argparse

def run_tests(verbose=False, performance=False, coverage=False):
    """Run the test suite with specified options."""
    
    print("="*60)
    print("INVENTORY MANAGEMENT SYSTEM - TEST RUNNER")
    print("="*60)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: It appears you're not in a virtual environment.")
        print("Consider activating your virtual environment first.")
        print()
    
    # Check if required modules exist
    required_modules = ['database', 'crud_operations', 'reports', 'ui']
    missing_modules = []
    
    for module in required_modules:
        if not os.path.exists(f"{module}.py"):
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Missing required modules: {', '.join(missing_modules)}")
        print("Please ensure all project files are present.")
        return False
    
    # Build test command
    cmd = [sys.executable, "test_inventory_system.py"]
    
    if verbose:
        print("Running tests in verbose mode...")
    
    if coverage:
        print("Running tests with coverage analysis...")
        try:
            import coverage
            cmd = [sys.executable, "-m", "coverage", "run", "--source=.", "test_inventory_system.py"]
        except ImportError:
            print("Coverage module not found. Install with: pip install coverage")
            return False
    
    # Run tests
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\nTests completed successfully!")
            
            if coverage:
                print("\nGenerating coverage report...")
                subprocess.run([sys.executable, "-m", "coverage", "report"])
                subprocess.run([sys.executable, "-m", "coverage", "html"])
                print("Coverage report generated in htmlcov/index.html")
            
            return True
        else:
            print(f"\nTests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_specific_test(test_name):
    """Run a specific test by name."""
    print(f"Running specific test: {test_name}")
    
    cmd = [sys.executable, "-m", "unittest", f"test_inventory_system.TestInventorySystem.{test_name}"]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running test: {e}")
        return False

def list_tests():
    """List all available tests."""
    print("Available tests:")
    print("-" * 40)
    
    tests = [
        "test_database_initialization",
        "test_category_crud_operations",
        "test_supplier_crud_operations", 
        "test_product_crud_operations",
        "test_transaction_crud_operations",
        "test_inventory_calculations",
        "test_product_search",
        "test_reports_generation",
        "test_database_queries",
        "test_data_integrity",
        "test_edge_cases",
        "test_deletion_constraints",
        "test_sample_data_integrity"
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"{i:2d}. {test}")
    
    print(f"\nTotal: {len(tests)} tests")

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Test runner for Inventory Management System")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("-p", "--performance", action="store_true", help="Include performance tests")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage analysis")
    parser.add_argument("-l", "--list", action="store_true", help="List all available tests")
    parser.add_argument("-t", "--test", help="Run a specific test by name")
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    if args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    
    # Run full test suite
    success = run_tests(verbose=args.verbose, performance=args.performance, coverage=args.coverage)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 