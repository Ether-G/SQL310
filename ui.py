import os
import sys
from typing import Optional, List, Dict, Any
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Initialize colorama for cross-platform colored output
init()

class InventoryUI:
    def __init__(self, crud_ops, reports):
        """Initialize the UI with CRUD operations and reports."""
        self.crud = crud_ops
        self.reports = reports
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def print_success(self, message: str):
        """Print a success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    def print_error(self, message: str):
        """Print an error message."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    def print_warning(self, message: str):
        """Print a warning message."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    def get_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """Get user input with validation."""
        while True:
            user_input = input(f"{Fore.WHITE}{prompt}: {Style.RESET_ALL}").strip()
            if not user_input and required:
                self.print_error("This field is required.")
                continue
            return user_input if user_input else None
    
    def get_int_input(self, prompt: str, min_value: int = None, max_value: int = None) -> Optional[int]:
        """Get integer input with validation."""
        while True:
            user_input = self.get_input(prompt)
            if user_input is None:
                return None
            
            try:
                value = int(user_input)
                if min_value is not None and value < min_value:
                    self.print_error(f"Value must be at least {min_value}.")
                    continue
                if max_value is not None and value > max_value:
                    self.print_error(f"Value must be at most {max_value}.")
                    continue
                return value
            except ValueError:
                self.print_error("Please enter a valid number.")
    
    def get_float_input(self, prompt: str, min_value: float = None) -> Optional[float]:
        """Get float input with validation."""
        while True:
            user_input = self.get_input(prompt)
            if user_input is None:
                return None
            
            try:
                value = float(user_input)
                if min_value is not None and value < min_value:
                    self.print_error(f"Value must be at least {min_value}.")
                    continue
                return value
            except ValueError:
                self.print_error("Please enter a valid number.")
    
    def display_menu(self, title: str, options: List[Dict[str, str]]) -> int:
        """Display a menu and get user selection."""
        self.print_header(title)
        
        for i, option in enumerate(options, 1):
            print(f"{Fore.YELLOW}{i:2d}.{Style.RESET_ALL} {option['text']}")
        
        print(f"{Fore.YELLOW} 0.{Style.RESET_ALL} Exit")
        
        while True:
            choice = self.get_int_input("\nEnter your choice", 0, len(options))
            if choice is not None:
                return choice
    
    def main_menu(self):
        """Display the main menu."""
        options = [
            {"text": "Manage Products", "action": "products"},
            {"text": "Manage Categories", "action": "categories"},
            {"text": "Manage Suppliers", "action": "suppliers"},
            {"text": "Manage Transactions", "action": "transactions"},
            {"text": "View Reports", "action": "reports"},
            {"text": "Search Products", "action": "search"}
        ]
        
        while True:
            choice = self.display_menu("INVENTORY MANAGEMENT SYSTEM", options)
            
            if choice == 0:
                self.print_success("Thank you for using the Inventory Management System!")
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"{action}_menu")()
    
    def products_menu(self):
        """Display the products management menu."""
        options = [
            {"text": "View All Products", "action": "view_all"},
            {"text": "Add New Product", "action": "add"},
            {"text": "Edit Product", "action": "edit"},
            {"text": "Delete Product", "action": "delete"},
            {"text": "View Product Details", "action": "view"}
        ]
        
        while True:
            choice = self.display_menu("PRODUCTS MANAGEMENT", options)
            
            if choice == 0:
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"product_{action}")()
    
    def product_view_all(self):
        """View all products."""
        self.clear_screen()
        self.print_header("ALL PRODUCTS")
        
        products = self.crud.get_products()
        if not products:
            self.print_warning("No products found.")
            input("\nPress Enter to continue...")
            return
        
        table_data = []
        for product in products:
            table_data.append([
                product['id'],
                product['name'],
                product['category_name'] or 'Uncategorized',
                f"${product['price']:.2f}",
                product['reorder_level']
            ])
        
        headers = ['ID', 'Name', 'Category', 'Price', 'Reorder Level']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        input("\nPress Enter to continue...")
    
    def product_add(self):
        """Add a new product."""
        self.clear_screen()
        self.print_header("ADD NEW PRODUCT")
        
        # Get categories for selection
        categories = self.crud.get_categories()
        if not categories:
            self.print_error("No categories available. Please create a category first.")
            input("\nPress Enter to continue...")
            return
        
        # Display categories
        print("Available Categories:")
        for cat in categories:
            print(f"  {cat['id']}. {cat['name']}")
        print()
        
        # Get product details
        name = self.get_input("Product name")
        if not name:
            return
        
        description = self.get_input("Description (optional)", required=False)
        
        category_id = self.get_int_input("Category ID")
        if category_id is None:
            return
        
        # Validate category exists
        if not any(cat['id'] == category_id for cat in categories):
            self.print_error("Invalid category ID.")
            input("\nPress Enter to continue...")
            return
        
        price = self.get_float_input("Price", min_value=0.0)
        if price is None:
            return
        
        reorder_level = self.get_int_input("Reorder level", min_value=0)
        if reorder_level is None:
            return
        
        # Create product
        product_id = self.crud.create_product(name, description, category_id, price, reorder_level)
        if product_id:
            self.print_success(f"Product '{name}' created successfully with ID {product_id}")
        else:
            self.print_error("Failed to create product.")
        
        input("\nPress Enter to continue...")
    
    def product_edit(self):
        """Edit an existing product."""
        self.clear_screen()
        self.print_header("EDIT PRODUCT")
        
        # Show all products
        products = self.crud.get_products()
        if not products:
            self.print_warning("No products found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Products:")
        for product in products:
            print(f"  {product['id']}. {product['name']} - ${product['price']:.2f}")
        print()
        
        product_id = self.get_int_input("Enter product ID to edit")
        if product_id is None:
            return
        
        # Get product details
        product = self.crud.get_product_by_id(product_id)
        if not product:
            self.print_error("Product not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nEditing product: {product['name']}")
        print("(Press Enter to keep current value)")
        
        # Get updated values
        name = self.get_input(f"Name [{product['name']}]", required=False) or product['name']
        description = self.get_input(f"Description [{product['description'] or 'None'}]", required=False) or product['description']
        
        # Show categories
        categories = self.crud.get_categories()
        print("\nAvailable Categories:")
        for cat in categories:
            print(f"  {cat['id']}. {cat['name']}")
        
        category_id = self.get_int_input(f"Category ID [{product['category_id']}]") or product['category_id']
        price = self.get_float_input(f"Price [${product['price']:.2f}]") or product['price']
        reorder_level = self.get_int_input(f"Reorder level [{product['reorder_level']}]") or product['reorder_level']
        
        # Update product
        if self.crud.update_product(product_id, name, description, category_id, price, reorder_level):
            self.print_success(f"Product '{name}' updated successfully")
        else:
            self.print_error("Failed to update product.")
        
        input("\nPress Enter to continue...")
    
    def product_delete(self):
        """Delete a product."""
        self.clear_screen()
        self.print_header("DELETE PRODUCT")
        
        # Show all products
        products = self.crud.get_products()
        if not products:
            self.print_warning("No products found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Products:")
        for product in products:
            print(f"  {product['id']}. {product['name']}")
        print()
        
        product_id = self.get_int_input("Enter product ID to delete")
        if product_id is None:
            return
        
        # Confirm deletion
        product = self.crud.get_product_by_id(product_id)
        if not product:
            self.print_error("Product not found.")
            input("\nPress Enter to continue...")
            return
        
        confirm = self.get_input(f"Are you sure you want to delete '{product['name']}'? (yes/no)")
        if confirm and confirm.lower() in ['yes', 'y']:
            if self.crud.delete_product(product_id):
                self.print_success(f"Product '{product['name']}' deleted successfully")
            else:
                self.print_error("Failed to delete product.")
        else:
            self.print_warning("Deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def product_view(self):
        """View detailed product information."""
        self.clear_screen()
        self.print_header("PRODUCT DETAILS")
        
        # Show all products
        products = self.crud.get_products()
        if not products:
            self.print_warning("No products found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Products:")
        for product in products:
            print(f"  {product['id']}. {product['name']}")
        print()
        
        product_id = self.get_int_input("Enter product ID to view")
        if product_id is None:
            return
        
        # Get product details
        product = self.crud.get_product_by_id(product_id)
        if not product:
            self.print_error("Product not found.")
            input("\nPress Enter to continue...")
            return
        
        # Get current stock
        current_stock = self.crud.get_product_stock(product_id)
        
        print(f"\n{Fore.CYAN}Product Details:{Style.RESET_ALL}")
        print(f"ID: {product['id']}")
        print(f"Name: {product['name']}")
        print(f"Description: {product['description'] or 'No description'}")
        print(f"Category: {product['category_name'] or 'Uncategorized'}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Reorder Level: {product['reorder_level']}")
        print(f"Current Stock: {current_stock}")
        
        if current_stock <= product['reorder_level']:
            self.print_warning("This product is low in stock!")
        
        input("\nPress Enter to continue...")
    
    def categories_menu(self):
        """Display the categories management menu."""
        options = [
            {"text": "View All Categories", "action": "view_all"},
            {"text": "Add New Category", "action": "add"},
            {"text": "Edit Category", "action": "edit"},
            {"text": "Delete Category", "action": "delete"}
        ]
        
        while True:
            choice = self.display_menu("CATEGORIES MANAGEMENT", options)
            
            if choice == 0:
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"category_{action}")()
    
    def category_view_all(self):
        """View all categories."""
        self.clear_screen()
        self.print_header("ALL CATEGORIES")
        
        categories = self.crud.get_categories()
        if not categories:
            self.print_warning("No categories found.")
            input("\nPress Enter to continue...")
            return
        
        table_data = []
        for category in categories:
            table_data.append([
                category['id'],
                category['name'],
                category['description'] or 'No description'
            ])
        
        headers = ['ID', 'Name', 'Description']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        input("\nPress Enter to continue...")
    
    def category_add(self):
        """Add a new category."""
        self.clear_screen()
        self.print_header("ADD NEW CATEGORY")
        
        name = self.get_input("Category name")
        if not name:
            return
        
        description = self.get_input("Description (optional)", required=False)
        
        category_id = self.crud.create_category(name, description)
        if category_id:
            self.print_success(f"Category '{name}' created successfully with ID {category_id}")
        else:
            self.print_error("Failed to create category.")
        
        input("\nPress Enter to continue...")
    
    def category_edit(self):
        """Edit an existing category."""
        self.clear_screen()
        self.print_header("EDIT CATEGORY")
        
        categories = self.crud.get_categories()
        if not categories:
            self.print_warning("No categories found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Categories:")
        for category in categories:
            print(f"  {category['id']}. {category['name']}")
        print()
        
        category_id = self.get_int_input("Enter category ID to edit")
        if category_id is None:
            return
        
        category = self.crud.get_category_by_id(category_id)
        if not category:
            self.print_error("Category not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nEditing category: {category['name']}")
        print("(Press Enter to keep current value)")
        
        name = self.get_input(f"Name [{category['name']}]", required=False) or category['name']
        description = self.get_input(f"Description [{category['description'] or 'None'}]", required=False) or category['description']
        
        if self.crud.update_category(category_id, name, description):
            self.print_success(f"Category '{name}' updated successfully")
        else:
            self.print_error("Failed to update category.")
        
        input("\nPress Enter to continue...")
    
    def category_delete(self):
        """Delete a category."""
        self.clear_screen()
        self.print_header("DELETE CATEGORY")
        
        categories = self.crud.get_categories()
        if not categories:
            self.print_warning("No categories found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Categories:")
        for category in categories:
            print(f"  {category['id']}. {category['name']}")
        print()
        
        category_id = self.get_int_input("Enter category ID to delete")
        if category_id is None:
            return
        
        category = self.crud.get_category_by_id(category_id)
        if not category:
            self.print_error("Category not found.")
            input("\nPress Enter to continue...")
            return
        
        confirm = self.get_input(f"Are you sure you want to delete '{category['name']}'? (yes/no)")
        if confirm and confirm.lower() in ['yes', 'y']:
            if self.crud.delete_category(category_id):
                self.print_success(f"Category '{category['name']}' deleted successfully")
            else:
                self.print_error("Failed to delete category.")
        else:
            self.print_warning("Deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def suppliers_menu(self):
        """Display the suppliers management menu."""
        options = [
            {"text": "View All Suppliers", "action": "view_all"},
            {"text": "Add New Supplier", "action": "add"},
            {"text": "Edit Supplier", "action": "edit"},
            {"text": "Delete Supplier", "action": "delete"}
        ]
        
        while True:
            choice = self.display_menu("SUPPLIERS MANAGEMENT", options)
            
            if choice == 0:
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"supplier_{action}")()
    
    def supplier_view_all(self):
        """View all suppliers."""
        self.clear_screen()
        self.print_header("ALL SUPPLIERS")
        
        suppliers = self.crud.get_suppliers()
        if not suppliers:
            self.print_warning("No suppliers found.")
            input("\nPress Enter to continue...")
            return
        
        table_data = []
        for supplier in suppliers:
            table_data.append([
                supplier['id'],
                supplier['name'],
                supplier['contact_info'] or 'No contact info',
                supplier['address'] or 'No address'
            ])
        
        headers = ['ID', 'Name', 'Contact Info', 'Address']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        input("\nPress Enter to continue...")
    
    def supplier_add(self):
        """Add a new supplier."""
        self.clear_screen()
        self.print_header("ADD NEW SUPPLIER")
        
        name = self.get_input("Supplier name")
        if not name:
            return
        
        contact_info = self.get_input("Contact info (optional)", required=False)
        address = self.get_input("Address (optional)", required=False)
        
        supplier_id = self.crud.create_supplier(name, contact_info, address)
        if supplier_id:
            self.print_success(f"Supplier '{name}' created successfully with ID {supplier_id}")
        else:
            self.print_error("Failed to create supplier.")
        
        input("\nPress Enter to continue...")
    
    def supplier_edit(self):
        """Edit an existing supplier."""
        self.clear_screen()
        self.print_header("EDIT SUPPLIER")
        
        suppliers = self.crud.get_suppliers()
        if not suppliers:
            self.print_warning("No suppliers found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Suppliers:")
        for supplier in suppliers:
            print(f"  {supplier['id']}. {supplier['name']}")
        print()
        
        supplier_id = self.get_int_input("Enter supplier ID to edit")
        if supplier_id is None:
            return
        
        supplier = self.crud.get_supplier_by_id(supplier_id)
        if not supplier:
            self.print_error("Supplier not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nEditing supplier: {supplier['name']}")
        print("(Press Enter to keep current value)")
        
        name = self.get_input(f"Name [{supplier['name']}]", required=False) or supplier['name']
        contact_info = self.get_input(f"Contact info [{supplier['contact_info'] or 'None'}]", required=False) or supplier['contact_info']
        address = self.get_input(f"Address [{supplier['address'] or 'None'}]", required=False) or supplier['address']
        
        if self.crud.update_supplier(supplier_id, name, contact_info, address):
            self.print_success(f"Supplier '{name}' updated successfully")
        else:
            self.print_error("Failed to update supplier.")
        
        input("\nPress Enter to continue...")
    
    def supplier_delete(self):
        """Delete a supplier."""
        self.clear_screen()
        self.print_header("DELETE SUPPLIER")
        
        suppliers = self.crud.get_suppliers()
        if not suppliers:
            self.print_warning("No suppliers found.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Suppliers:")
        for supplier in suppliers:
            print(f"  {supplier['id']}. {supplier['name']}")
        print()
        
        supplier_id = self.get_int_input("Enter supplier ID to delete")
        if supplier_id is None:
            return
        
        supplier = self.crud.get_supplier_by_id(supplier_id)
        if not supplier:
            self.print_error("Supplier not found.")
            input("\nPress Enter to continue...")
            return
        
        confirm = self.get_input(f"Are you sure you want to delete '{supplier['name']}'? (yes/no)")
        if confirm and confirm.lower() in ['yes', 'y']:
            if self.crud.delete_supplier(supplier_id):
                self.print_success(f"Supplier '{supplier['name']}' deleted successfully")
            else:
                self.print_error("Failed to delete supplier.")
        else:
            self.print_warning("Deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def transactions_menu(self):
        """Display the transactions management menu."""
        options = [
            {"text": "View All Transactions", "action": "view_all"},
            {"text": "Add New Transaction", "action": "add"},
            {"text": "Edit Transaction", "action": "edit"},
            {"text": "Delete Transaction", "action": "delete"}
        ]
        
        while True:
            choice = self.display_menu("TRANSACTIONS MANAGEMENT", options)
            
            if choice == 0:
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"transaction_{action}")()
    
    def transaction_view_all(self):
        """View all transactions."""
        self.clear_screen()
        self.print_header("ALL TRANSACTIONS")
        
        transactions = self.crud.get_transactions()
        if not transactions:
            self.print_warning("No transactions found.")
            input("\nPress Enter to continue...")
            return
        
        table_data = []
        for transaction in transactions:
            table_data.append([
                transaction['id'],
                transaction['product_name'],
                transaction['transaction_type'],
                transaction['quantity'],
                transaction['date'],
                transaction['supplier_name'] or 'N/A',
                transaction['notes'] or ''
            ])
        
        headers = ['ID', 'Product', 'Type', 'Quantity', 'Date', 'Supplier', 'Notes']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        input("\nPress Enter to continue...")
    
    def transaction_add(self):
        """Add a new transaction."""
        self.clear_screen()
        self.print_header("ADD NEW TRANSACTION")
        
        # Get products
        products = self.crud.get_products()
        if not products:
            self.print_error("No products available. Please create a product first.")
            input("\nPress Enter to continue...")
            return
        
        print("Available Products:")
        for product in products:
            print(f"  {product['id']}. {product['name']}")
        print()
        
        product_id = self.get_int_input("Product ID")
        if product_id is None:
            return
        
        # Validate product exists
        if not any(p['id'] == product_id for p in products):
            self.print_error("Invalid product ID.")
            input("\nPress Enter to continue...")
            return
        
        # Get transaction type
        print("\nTransaction Types:")
        print("  1. IN (Stock received)")
        print("  2. OUT (Stock sold/shipped)")
        print("  3. ADJUSTMENT (Stock adjustment)")
        
        type_choice = self.get_int_input("Transaction type (1-3)", 1, 3)
        if type_choice is None:
            return
        
        transaction_types = {1: 'IN', 2: 'OUT', 3: 'ADJUSTMENT'}
        transaction_type = transaction_types[type_choice]
        
        quantity = self.get_int_input("Quantity", min_value=1)
        if quantity is None:
            return
        
        # Get supplier (optional for IN transactions)
        supplier_id = None
        if transaction_type == 'IN':
            suppliers = self.crud.get_suppliers()
            if suppliers:
                print("\nAvailable Suppliers:")
                for supplier in suppliers:
                    print(f"  {supplier['id']}. {supplier['name']}")
                print("  0. No supplier")
                
                supplier_choice = self.get_int_input("Supplier ID (0 for none)", 0, len(suppliers))
                if supplier_choice is not None and supplier_choice > 0:
                    supplier_id = supplier_choice
        
        notes = self.get_input("Notes (optional)", required=False)
        
        # Create transaction
        transaction_id = self.crud.create_transaction(product_id, transaction_type, quantity, supplier_id, notes)
        if transaction_id:
            self.print_success(f"Transaction created successfully with ID {transaction_id}")
        else:
            self.print_error("Failed to create transaction.")
        
        input("\nPress Enter to continue...")
    
    def transaction_edit(self):
        """Edit an existing transaction."""
        self.clear_screen()
        self.print_header("EDIT TRANSACTION")
        
        transactions = self.crud.get_transactions()
        if not transactions:
            self.print_warning("No transactions found.")
            input("\nPress Enter to continue...")
            return
        
        print("Recent Transactions:")
        for transaction in transactions[:10]:  # Show last 10
            print(f"  {transaction['id']}. {transaction['product_name']} - {transaction['transaction_type']} {transaction['quantity']}")
        print()
        
        transaction_id = self.get_int_input("Enter transaction ID to edit")
        if transaction_id is None:
            return
        
        transaction = self.crud.get_transaction_by_id(transaction_id)
        if not transaction:
            self.print_error("Transaction not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nEditing transaction: {transaction['product_name']} - {transaction['transaction_type']} {transaction['quantity']}")
        print("(Press Enter to keep current value)")
        
        # Get products for selection
        products = self.crud.get_products()
        print("\nAvailable Products:")
        for product in products:
            print(f"  {product['id']}. {product['name']}")
        
        product_id = self.get_int_input(f"Product ID [{transaction['product_id']}]") or transaction['product_id']
        
        # Get transaction type
        print("\nTransaction Types:")
        print("  1. IN (Stock received)")
        print("  2. OUT (Stock sold/shipped)")
        print("  3. ADJUSTMENT (Stock adjustment)")
        
        type_choice = self.get_int_input("Transaction type (1-3)", 1, 3)
        if type_choice is None:
            return
        
        transaction_types = {1: 'IN', 2: 'OUT', 3: 'ADJUSTMENT'}
        transaction_type = transaction_types[type_choice]
        
        quantity = self.get_int_input(f"Quantity [{transaction['quantity']}]", min_value=1) or transaction['quantity']
        
        # Get supplier
        supplier_id = transaction['supplier_id']
        if transaction_type == 'IN':
            suppliers = self.crud.get_suppliers()
            if suppliers:
                print("\nAvailable Suppliers:")
                for supplier in suppliers:
                    print(f"  {supplier['id']}. {supplier['name']}")
                print("  0. No supplier")
                
                supplier_choice = self.get_int_input(f"Supplier ID [{supplier_id or 0}]", 0, len(suppliers))
                if supplier_choice is not None:
                    supplier_id = supplier_choice if supplier_choice > 0 else None
        
        notes = self.get_input(f"Notes [{transaction['notes'] or 'None'}]", required=False) or transaction['notes']
        
        # Update transaction
        if self.crud.update_transaction(transaction_id, product_id, transaction_type, quantity, supplier_id, notes):
            self.print_success("Transaction updated successfully")
        else:
            self.print_error("Failed to update transaction.")
        
        input("\nPress Enter to continue...")
    
    def transaction_delete(self):
        """Delete a transaction."""
        self.clear_screen()
        self.print_header("DELETE TRANSACTION")
        
        transactions = self.crud.get_transactions()
        if not transactions:
            self.print_warning("No transactions found.")
            input("\nPress Enter to continue...")
            return
        
        print("Recent Transactions:")
        for transaction in transactions[:10]:  # Show last 10
            print(f"  {transaction['id']}. {transaction['product_name']} - {transaction['transaction_type']} {transaction['quantity']}")
        print()
        
        transaction_id = self.get_int_input("Enter transaction ID to delete")
        if transaction_id is None:
            return
        
        transaction = self.crud.get_transaction_by_id(transaction_id)
        if not transaction:
            self.print_error("Transaction not found.")
            input("\nPress Enter to continue...")
            return
        
        confirm = self.get_input(f"Are you sure you want to delete this transaction? (yes/no)")
        if confirm and confirm.lower() in ['yes', 'y']:
            if self.crud.delete_transaction(transaction_id):
                self.print_success("Transaction deleted successfully")
            else:
                self.print_error("Failed to delete transaction.")
        else:
            self.print_warning("Deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def reports_menu(self):
        """Display the reports menu."""
        options = [
            {"text": "Current Inventory Report", "action": "inventory"},
            {"text": "Low Stock Report", "action": "low_stock"},
            {"text": "Inventory Value Report", "action": "value"},
            {"text": "Transaction History", "action": "transactions"},
            {"text": "Category Report", "action": "category"},
            {"text": "Supplier Report", "action": "supplier"},
            {"text": "Monthly Summary", "action": "monthly"},
            {"text": "Comprehensive Report", "action": "comprehensive"}
        ]
        
        while True:
            choice = self.display_menu("REPORTS", options)
            
            if choice == 0:
                break
            elif 1 <= choice <= len(options):
                action = options[choice - 1]["action"]
                getattr(self, f"report_{action}")()
    
    def report_inventory(self):
        """Display current inventory report."""
        self.clear_screen()
        self.print_header("CURRENT INVENTORY REPORT")
        print(self.reports.generate_inventory_report())
        input("\nPress Enter to continue...")
    
    def report_low_stock(self):
        """Display low stock report."""
        self.clear_screen()
        self.print_header("LOW STOCK REPORT")
        print(self.reports.generate_low_stock_report())
        input("\nPress Enter to continue...")
    
    def report_value(self):
        """Display inventory value report."""
        self.clear_screen()
        self.print_header("INVENTORY VALUE REPORT")
        print(self.reports.generate_inventory_value_report())
        input("\nPress Enter to continue...")
    
    def report_transactions(self):
        """Display transaction history report."""
        self.clear_screen()
        self.print_header("TRANSACTION HISTORY")
        days = self.get_int_input("Number of days to show (default: 30)", min_value=1) or 30
        print(self.reports.generate_transaction_report(days))
        input("\nPress Enter to continue...")
    
    def report_category(self):
        """Display category report."""
        self.clear_screen()
        self.print_header("CATEGORY REPORT")
        print(self.reports.generate_category_report())
        input("\nPress Enter to continue...")
    
    def report_supplier(self):
        """Display supplier report."""
        self.clear_screen()
        self.print_header("SUPPLIER REPORT")
        print(self.reports.generate_supplier_report())
        input("\nPress Enter to continue...")
    
    def report_monthly(self):
        """Display monthly summary report."""
        self.clear_screen()
        self.print_header("MONTHLY SUMMARY REPORT")
        print(self.reports.generate_monthly_summary())
        input("\nPress Enter to continue...")
    
    def report_comprehensive(self):
        """Display comprehensive report."""
        self.clear_screen()
        self.print_header("COMPREHENSIVE REPORT")
        print(self.reports.generate_comprehensive_report())
        input("\nPress Enter to continue...")
    
    def search_menu(self):
        """Display the search menu."""
        self.clear_screen()
        self.print_header("SEARCH PRODUCTS")
        
        search_term = self.get_input("Enter search term")
        if not search_term:
            return
        
        products = self.crud.search_products(search_term)
        if not products:
            self.print_warning(f"No products found matching '{search_term}'")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nFound {len(products)} product(s) matching '{search_term}':")
        table_data = []
        for product in products:
            table_data.append([
                product['id'],
                product['name'],
                product['category_name'] or 'Uncategorized',
                f"${product['price']:.2f}",
                product['reorder_level']
            ])
        
        headers = ['ID', 'Name', 'Category', 'Price', 'Reorder Level']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        input("\nPress Enter to continue...") 