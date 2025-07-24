from typing import List, Dict, Any
from datetime import datetime, timedelta
from tabulate import tabulate

class InventoryReports:
    def __init__(self, db):
        """Initialize with database connection."""
        self.db = db
    
    def generate_inventory_report(self) -> str:
        """Generate a comprehensive inventory report."""
        inventory = self.db.get_current_inventory()
        
        if not inventory:
            return "No inventory data available."
        
        # Prepare data for tabulation
        table_data = []
        for item in inventory:
            table_data.append([
                item['id'],
                item['name'],
                item['category_name'] or 'Uncategorized',
                item['current_stock'],
                f"${item['price']:.2f}",
                item['reorder_level'],
                f"${item['current_stock'] * item['price']:.2f}"
            ])
        
        headers = ['ID', 'Product', 'Category', 'Stock', 'Price', 'Reorder Level', 'Total Value']
        return tabulate(table_data, headers=headers, tablefmt='grid')
    
    def generate_low_stock_report(self) -> str:
        """Generate a report of products below reorder level."""
        low_stock = self.db.get_low_stock_products()
        
        if not low_stock:
            return "No products are currently low in stock."
        
        table_data = []
        for item in low_stock:
            table_data.append([
                item['id'],
                item['name'],
                item['category_name'] or 'Uncategorized',
                item['current_stock'],
                item['reorder_level'],
                item['reorder_level'] - item['current_stock']
            ])
        
        headers = ['ID', 'Product', 'Category', 'Current Stock', 'Reorder Level', 'Need to Order']
        return tabulate(table_data, headers=headers, tablefmt='grid')
    
    def generate_inventory_value_report(self) -> str:
        """Generate a report showing total inventory value and statistics."""
        value_data = self.db.get_inventory_value()
        
        report = "=== INVENTORY VALUE REPORT ===\n\n"
        report += f"Total Inventory Value: ${value_data['total_value']:.2f}\n"
        report += f"Average Product Price: ${value_data['avg_price']:.2f}\n"
        report += f"Total Products: {value_data['total_products']}\n\n"
        
        # Get top 5 most valuable products
        query = '''
            SELECT 
                p.name,
                c.name as category_name,
                COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) as current_stock,
                p.price,
                (COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                 COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0)) * p.price as total_value
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory_transactions t ON p.id = t.product_id
            GROUP BY p.id, p.name, c.name, p.price
            HAVING current_stock > 0
            ORDER BY total_value DESC
            LIMIT 5
        '''
        
        self.db.cursor.execute(query)
        top_products = self.db.cursor.fetchall()
        
        if top_products:
            report += "Top 5 Most Valuable Products:\n"
            table_data = []
            for product in top_products:
                table_data.append([
                    product[0],  # name
                    product[1] or 'Uncategorized',  # category
                    product[2],  # stock
                    f"${product[3]:.2f}",  # price
                    f"${product[4]:.2f}"  # total value
                ])
            
            headers = ['Product', 'Category', 'Stock', 'Price', 'Total Value']
            report += tabulate(table_data, headers=headers, tablefmt='grid')
        
        return report
    
    def generate_transaction_report(self, days: int = 30) -> str:
        """Generate a report of recent transactions."""
        transactions = self.db.get_transaction_history(days)
        
        if not transactions:
            return f"No transactions found in the last {days} days."
        
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
        return tabulate(table_data, headers=headers, tablefmt='grid')
    
    def generate_category_report(self) -> str:
        """Generate a report showing inventory by category."""
        query = '''
            SELECT 
                c.name as category_name,
                COUNT(p.id) as product_count,
                SUM(current_stock) as total_stock,
                AVG(p.price) as avg_price,
                SUM(current_stock * p.price) as total_value
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN (
                SELECT 
                    p.id as product_id,
                    COALESCE(SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END), 0) as current_stock
                FROM products p
                LEFT JOIN inventory_transactions t ON p.id = t.product_id
                GROUP BY p.id
            ) stock ON p.id = stock.product_id
            GROUP BY c.id, c.name
            ORDER BY total_value DESC
        '''
        
        self.db.cursor.execute(query)
        categories = self.db.cursor.fetchall()
        
        if not categories:
            return "No category data available."
        
        table_data = []
        for category in categories:
            table_data.append([
                category[0] or 'Uncategorized',
                category[1] or 0,
                category[2] or 0,
                f"${category[3]:.2f}" if category[3] else '$0.00',
                f"${category[4]:.2f}" if category[4] else '$0.00'
            ])
        
        headers = ['Category', 'Products', 'Total Stock', 'Avg Price', 'Total Value']
        return tabulate(table_data, headers=headers, tablefmt='grid')
    
    def generate_supplier_report(self) -> str:
        """Generate a report showing transactions by supplier."""
        query = '''
            SELECT 
                s.name as supplier_name,
                COUNT(t.id) as transaction_count,
                SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END) as total_received,
                SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END) as total_shipped,
                COUNT(DISTINCT t.product_id) as products_handled
            FROM suppliers s
            LEFT JOIN inventory_transactions t ON s.id = t.supplier_id
            GROUP BY s.id, s.name
            ORDER BY transaction_count DESC
        '''
        
        self.db.cursor.execute(query)
        suppliers = self.db.cursor.fetchall()
        
        if not suppliers:
            return "No supplier data available."
        
        table_data = []
        for supplier in suppliers:
            table_data.append([
                supplier[0],
                supplier[1] or 0,
                supplier[2] or 0,
                supplier[3] or 0,
                supplier[4] or 0
            ])
        
        headers = ['Supplier', 'Transactions', 'Total Received', 'Total Shipped', 'Products Handled']
        return tabulate(table_data, headers=headers, tablefmt='grid')
    
    def generate_monthly_summary(self) -> str:
        """Generate a monthly summary report."""
        # Get current month's transactions
        query = '''
            SELECT 
                strftime('%Y-%m', t.date) as month,
                COUNT(t.id) as total_transactions,
                SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END) as total_in,
                SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END) as total_out,
                COUNT(DISTINCT t.product_id) as products_affected
            FROM inventory_transactions t
            WHERE t.date >= datetime('now', 'start of month')
            GROUP BY strftime('%Y-%m', t.date)
        '''
        
        self.db.cursor.execute(query)
        monthly_data = self.db.cursor.fetchone()
        
        if not monthly_data:
            return "No transactions found for the current month."
        
        report = "=== MONTHLY SUMMARY REPORT ===\n\n"
        report += f"Month: {monthly_data[0]}\n"
        report += f"Total Transactions: {monthly_data[1]}\n"
        report += f"Total Items Received: {monthly_data[2]}\n"
        report += f"Total Items Shipped: {monthly_data[3]}\n"
        report += f"Products Affected: {monthly_data[4]}\n"
        report += f"Net Change: {monthly_data[2] - monthly_data[3]}\n\n"
        
        # Get top products by transaction volume this month
        query = '''
            SELECT 
                p.name,
                COUNT(t.id) as transaction_count,
                SUM(CASE WHEN t.transaction_type = 'IN' THEN t.quantity ELSE 0 END) as received,
                SUM(CASE WHEN t.transaction_type = 'OUT' THEN t.quantity ELSE 0 END) as shipped
            FROM products p
            JOIN inventory_transactions t ON p.id = t.product_id
            WHERE t.date >= datetime('now', 'start of month')
            GROUP BY p.id, p.name
            ORDER BY transaction_count DESC
            LIMIT 5
        '''
        
        self.db.cursor.execute(query)
        top_products = self.db.cursor.fetchall()
        
        if top_products:
            report += "Top 5 Products by Transaction Volume (This Month):\n"
            table_data = []
            for product in top_products:
                table_data.append([
                    product[0],
                    product[1],
                    product[2],
                    product[3]
                ])
            
            headers = ['Product', 'Transactions', 'Received', 'Shipped']
            report += tabulate(table_data, headers=headers, tablefmt='grid')
        
        return report
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report combining all reports."""
        report = "=" * 60 + "\n"
        report += "           INVENTORY MANAGEMENT SYSTEM REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Inventory Value Summary
        value_data = self.db.get_inventory_value()
        report += f"Total Inventory Value: ${value_data['total_value']:.2f}\n"
        report += f"Total Products: {value_data['total_products']}\n"
        report += f"Average Product Price: ${value_data['avg_price']:.2f}\n\n"
        
        # Low Stock Alert
        low_stock = self.db.get_low_stock_products()
        if low_stock:
            report += f"⚠️  LOW STOCK ALERT: {len(low_stock)} products need reordering!\n\n"
        
        # Current Inventory
        report += "CURRENT INVENTORY:\n"
        report += "-" * 30 + "\n"
        report += self.generate_inventory_report() + "\n\n"
        
        # Low Stock Report
        if low_stock:
            report += "LOW STOCK PRODUCTS:\n"
            report += "-" * 30 + "\n"
            report += self.generate_low_stock_report() + "\n\n"
        
        # Category Summary
        report += "INVENTORY BY CATEGORY:\n"
        report += "-" * 30 + "\n"
        report += self.generate_category_report() + "\n\n"
        
        # Recent Transactions
        report += "RECENT TRANSACTIONS (Last 30 Days):\n"
        report += "-" * 30 + "\n"
        report += self.generate_transaction_report(30) + "\n\n"
        
        # Monthly Summary
        report += "MONTHLY SUMMARY:\n"
        report += "-" * 30 + "\n"
        report += self.generate_monthly_summary() + "\n"
        
        report += "=" * 60 + "\n"
        report += f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60
        
        return report 