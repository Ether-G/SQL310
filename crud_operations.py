from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class CRUDOperations:
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    # Category CRUD Operations
    def create_category(self, name: str, description: str = None) -> int:
        """Create a new category."""
        try:
            self.db.cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error creating category: {e}")
            return None
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        self.db.cursor.execute("SELECT * FROM categories ORDER BY name")
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        self.db.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        result = self.db.cursor.fetchone()
        return dict(result) if result else None
    
    def update_category(self, category_id: int, name: str, description: str = None) -> bool:
        """Update a category."""
        try:
            self.db.cursor.execute(
                "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                (name, description, category_id)
            )
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating category: {e}")
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category (only if no products are using it)."""
        try:
            # Check if category is being used by any products
            self.db.cursor.execute(
                "SELECT COUNT(*) FROM products WHERE category_id = ?",
                (category_id,)
            )
            if self.db.cursor.fetchone()[0] > 0:
                print("Cannot delete category: Products are using this category")
                return False
            
            self.db.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    # Supplier CRUD Operations
    def create_supplier(self, name: str, contact_info: str = None, address: str = None) -> int:
        """Create a new supplier."""
        try:
            self.db.cursor.execute(
                "INSERT INTO suppliers (name, contact_info, address) VALUES (?, ?, ?)",
                (name, contact_info, address)
            )
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return None
    
    def get_suppliers(self) -> List[Dict[str, Any]]:
        """Get all suppliers."""
        self.db.cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Get supplier by ID."""
        self.db.cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        result = self.db.cursor.fetchone()
        return dict(result) if result else None
    
    def update_supplier(self, supplier_id: int, name: str, contact_info: str = None, address: str = None) -> bool:
        """Update a supplier."""
        try:
            self.db.cursor.execute(
                "UPDATE suppliers SET name = ?, contact_info = ?, address = ? WHERE id = ?",
                (name, contact_info, address, supplier_id)
            )
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return False
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete a supplier (only if no transactions are using it)."""
        try:
            # Check if supplier is being used by any transactions
            self.db.cursor.execute(
                "SELECT COUNT(*) FROM inventory_transactions WHERE supplier_id = ?",
                (supplier_id,)
            )
            if self.db.cursor.fetchone()[0] > 0:
                print("Cannot delete supplier: Transactions are using this supplier")
                return False
            
            self.db.cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False
    
    # Product CRUD Operations
    def create_product(self, name: str, description: str, category_id: int, price: float, reorder_level: int = 10) -> int:
        """Create a new product."""
        try:
            self.db.cursor.execute(
                "INSERT INTO products (name, description, category_id, price, reorder_level) VALUES (?, ?, ?, ?, ?)",
                (name, description, category_id, price, reorder_level)
            )
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error creating product: {e}")
            return None
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Get all products with category information."""
        query = '''
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            ORDER BY p.name
        '''
        self.db.cursor.execute(query)
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID with category information."""
        query = '''
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.id = ?
        '''
        self.db.cursor.execute(query, (product_id,))
        result = self.db.cursor.fetchone()
        return dict(result) if result else None
    
    def update_product(self, product_id: int, name: str, description: str, category_id: int, price: float, reorder_level: int) -> bool:
        """Update a product."""
        try:
            self.db.cursor.execute(
                "UPDATE products SET name = ?, description = ?, category_id = ?, price = ?, reorder_level = ? WHERE id = ?",
                (name, description, category_id, price, reorder_level, product_id)
            )
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product (only if no transactions exist for it)."""
        try:
            # Check if product has any transactions
            self.db.cursor.execute(
                "SELECT COUNT(*) FROM inventory_transactions WHERE product_id = ?",
                (product_id,)
            )
            if self.db.cursor.fetchone()[0] > 0:
                print("Cannot delete product: Transactions exist for this product")
                return False
            
            self.db.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    # Transaction CRUD Operations
    def create_transaction(self, product_id: int, transaction_type: str, quantity: int, supplier_id: int = None, notes: str = None) -> int:
        """Create a new inventory transaction."""
        try:
            # Validate transaction type
            if transaction_type not in ['IN', 'OUT', 'ADJUSTMENT']:
                raise ValueError("Transaction type must be 'IN', 'OUT', or 'ADJUSTMENT'")
            
            self.db.cursor.execute(
                "INSERT INTO inventory_transactions (product_id, transaction_type, quantity, supplier_id, notes) VALUES (?, ?, ?, ?, ?)",
                (product_id, transaction_type, quantity, supplier_id, notes)
            )
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
    
    def get_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent transactions with product and supplier information."""
        query = '''
            SELECT 
                t.*,
                p.name as product_name,
                s.name as supplier_name
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.id
            LEFT JOIN suppliers s ON t.supplier_id = s.id
            ORDER BY t.date DESC
            LIMIT ?
        '''
        self.db.cursor.execute(query, (limit,))
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID with product and supplier information."""
        query = '''
            SELECT 
                t.*,
                p.name as product_name,
                s.name as supplier_name
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.id
            LEFT JOIN suppliers s ON t.supplier_id = s.id
            WHERE t.id = ?
        '''
        self.db.cursor.execute(query, (transaction_id,))
        result = self.db.cursor.fetchone()
        return dict(result) if result else None
    
    def update_transaction(self, transaction_id: int, product_id: int, transaction_type: str, quantity: int, supplier_id: int = None, notes: str = None) -> bool:
        """Update a transaction."""
        try:
            # Validate transaction type
            if transaction_type not in ['IN', 'OUT', 'ADJUSTMENT']:
                raise ValueError("Transaction type must be 'IN', 'OUT', or 'ADJUSTMENT'")
            
            self.db.cursor.execute(
                "UPDATE inventory_transactions SET product_id = ?, transaction_type = ?, quantity = ?, supplier_id = ?, notes = ? WHERE id = ?",
                (product_id, transaction_type, quantity, supplier_id, notes, transaction_id)
            )
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return False
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        try:
            self.db.cursor.execute("DELETE FROM inventory_transactions WHERE id = ?", (transaction_id,))
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    # Additional helper methods
    def get_product_stock(self, product_id: int) -> int:
        """Get current stock level for a specific product."""
        query = '''
            SELECT 
                COALESCE(SUM(CASE WHEN transaction_type = 'IN' THEN quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN transaction_type = 'OUT' THEN quantity ELSE 0 END), 0) as current_stock
            FROM inventory_transactions 
            WHERE product_id = ?
        '''
        self.db.cursor.execute(query, (product_id,))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0
    
    def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        """Search products by name or description."""
        query = '''
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.name LIKE ? OR p.description LIKE ?
            ORDER BY p.name
        '''
        search_pattern = f"%{search_term}%"
        self.db.cursor.execute(query, (search_pattern, search_pattern))
        return [dict(row) for row in self.db.cursor.fetchall()] 