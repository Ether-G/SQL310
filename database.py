import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

class InventoryDatabase:
    def __init__(self, db_path: str = "inventory.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()
        
        # Enable foreign key constraints
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create all necessary tables if they don't exist."""
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_info TEXT,
                address TEXT
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                price REAL NOT NULL,
                reorder_level INTEGER DEFAULT 10,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Inventory transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL CHECK (transaction_type IN ('IN', 'OUT', 'ADJUSTMENT')),
                quantity INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                supplier_id INTEGER,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        self.conn.commit()
    
    def seed_sample_data(self):
        """Seed the database with sample data for testing."""
        # Insert sample categories
        categories = [
            ("Electronics", "Electronic devices and components"),
            ("Clothing", "Apparel and accessories"),
            ("Books", "Books and publications"),
            ("Home & Garden", "Home improvement and garden supplies")
        ]
        
        for category in categories:
            self.cursor.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                category
            )
        
        # Insert sample suppliers
        suppliers = [
            ("TechCorp Inc.", "contact@techcorp.com", "123 Tech Street, Silicon Valley, CA"),
            ("Fashion Forward", "orders@fashionforward.com", "456 Fashion Ave, New York, NY"),
            ("BookWorld", "sales@bookworld.com", "789 Library Lane, Boston, MA"),
            ("Home Depot", "orders@homedepot.com", "321 Hardware Road, Atlanta, GA")
        ]
        
        for supplier in suppliers:
            self.cursor.execute(
                "INSERT OR IGNORE INTO suppliers (name, contact_info, address) VALUES (?, ?, ?)",
                supplier
            )
        
        # Insert sample products
        products = [
            ("Laptop", "High-performance laptop", 1, 999.99, 5),
            ("T-Shirt", "Cotton t-shirt", 2, 19.99, 20),
            ("Python Programming Book", "Learn Python programming", 3, 49.99, 10),
            ("Garden Hose", "50ft garden hose", 4, 29.99, 15)
        ]
        
        for product in products:
            self.cursor.execute(
                "INSERT OR IGNORE INTO products (name, description, category_id, price, reorder_level) VALUES (?, ?, ?, ?, ?)",
                product
            )
        
        # Insert sample transactions
        transactions = [
            (1, "IN", 10, 1, "Initial stock"),
            (2, "IN", 50, 2, "Initial stock"),
            (3, "IN", 25, 3, "Initial stock"),
            (4, "IN", 30, 4, "Initial stock"),
            (1, "OUT", 2, None, "Customer sale"),
            (2, "OUT", 5, None, "Customer sale")
        ]
        
        for transaction in transactions:
            self.cursor.execute(
                "INSERT OR IGNORE INTO inventory_transactions (product_id, transaction_type, quantity, supplier_id, notes) VALUES (?, ?, ?, ?, ?)",
                transaction
            )
        
        self.conn.commit()
    
    def get_current_inventory(self) -> List[Dict[str, Any]]:
        """Get current inventory levels for all products."""
        query = '''
            SELECT 
                p.id,
                p.name,
                p.description,
                c.name as category_name,
                p.price,
                p.reorder_level,
                COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) as current_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory_transactions t ON p.id = t.product_id
            GROUP BY p.id, p.name, p.description, c.name, p.price, p.reorder_level
            ORDER BY p.name
        '''
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Get products that are below their reorder level."""
        query = '''
            SELECT 
                p.id,
                p.name,
                p.description,
                c.name as category_name,
                p.price,
                p.reorder_level,
                COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) as current_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory_transactions t ON p.id = t.product_id
            GROUP BY p.id, p.name, p.description, c.name, p.price, p.reorder_level
            HAVING current_stock <= p.reorder_level
            ORDER BY current_stock ASC
        '''
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_inventory_value(self) -> Dict[str, float]:
        """Calculate total inventory value and average price."""
        query = '''
            SELECT 
                SUM(current_stock * price) as total_value,
                AVG(price) as avg_price,
                COUNT(*) as total_products
            FROM (
                SELECT 
                    p.price,
                    COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) as current_stock
                FROM products p
                LEFT JOIN inventory_transactions t ON p.id = t.product_id
                GROUP BY p.id, p.price
            )
        '''
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        if result:
            return {
                'total_value': result[0] or 0.0,
                'avg_price': result[1] or 0.0,
                'total_products': result[2] or 0
            }
        return {'total_value': 0.0, 'avg_price': 0.0, 'total_products': 0}
    
    def get_transaction_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent transaction history."""
        query = '''
            SELECT 
                t.id,
                p.name as product_name,
                t.transaction_type,
                t.quantity,
                t.date,
                s.name as supplier_name,
                t.notes
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.id
            LEFT JOIN suppliers s ON t.supplier_id = s.id
            WHERE t.date >= datetime('now', '-{} days')
            ORDER BY t.date DESC
        '''.format(days)
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()] 