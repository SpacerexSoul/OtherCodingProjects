#!/usr/bin/env python3
"""
Fully Normalized E-commerce Database Schema

This script demonstrates a fully normalized (BCNF) relational database schema
for an e-commerce system using SQLite.
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("ecommerce_schema.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class EcommerceDatabase:
    """Implementation of a fully normalized e-commerce database schema"""
    
    def __init__(self, db_path="ecommerce.db"):
        """Initialize the database with the specified path"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish connection to the SQLite database"""
        try:
            # Connect to the database
            self.conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Use row factory for dictionary-like results
            self.conn.row_factory = sqlite3.Row
            
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return False
    
    def initialize_schema(self) -> bool:
        """Create the fully normalized database schema"""
        try:
            # Create customers table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                registration_date DATE DEFAULT CURRENT_DATE,
                last_login TIMESTAMP
            )
            """)
            
            # Create addresses table (normalized from customers)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                address_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                address_type TEXT NOT NULL,  -- 'billing' or 'shipping'
                street_address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                postal_code TEXT NOT NULL,
                country TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                UNIQUE (customer_id, address_type, street_address)
            )
            """)
            
            # Create product categories table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                parent_category_id INTEGER,
                FOREIGN KEY (parent_category_id) REFERENCES product_categories(category_id)
            )
            """)
            
            # Create products table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                created_date DATE DEFAULT CURRENT_DATE,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
            )
            """)
            
            # Create product_attributes table (normalized from products)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_attributes (
                attribute_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
            """)
            
            # Create product_attribute_values table (normalized from products)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_attribute_values (
                product_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (product_id, attribute_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                FOREIGN KEY (attribute_id) REFERENCES product_attributes(attribute_id) ON DELETE CASCADE
            )
            """)
            
            # Create product_variants table (normalized from products)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                variant_id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            )
            """)
            
            # Create variant_attributes table (normalized from product_variants)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS variant_attributes (
                variant_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (variant_id, attribute_id),
                FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE,
                FOREIGN KEY (attribute_id) REFERENCES product_attributes(attribute_id) ON DELETE CASCADE
            )
            """)
            
            # Create orders table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'pending',
                billing_address_id INTEGER NOT NULL,
                shipping_address_id INTEGER NOT NULL,
                shipping_method TEXT,
                shipping_cost DECIMAL(10, 2) DEFAULT 0,
                tax_amount DECIMAL(10, 2) DEFAULT 0,
                total_amount DECIMAL(10, 2) NOT NULL,
                payment_method TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id),
                FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
            )
            """)
            
            # Create order_items table (normalized from orders)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                variant_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price DECIMAL(10, 2) NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id)
            )
            """)
            
            # Create payment_transactions table (normalized from orders)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                transaction_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method TEXT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status TEXT NOT NULL,
                reference_code TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
            """)
            
            # Create product_reviews table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                review_id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified_purchase BOOLEAN DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                UNIQUE (product_id, customer_id)
            )
            """)
            
            # Create indexes for performance
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_customer ON addresses(customer_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON products(category_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_variant_product ON product_variants(product_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_customer ON orders(customer_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_status ON orders(status)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_item_order ON order_items(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_item_variant ON order_items(variant_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_order ON payment_transactions(order_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_product ON product_reviews(product_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_customer ON product_reviews(customer_id)")
            
            self.conn.commit()
            logging.info("Database schema initialized successfully")
            return True
        except sqlite3.Error as e:
            logging.error(f"Schema initialization error: {e}")
            self.conn.rollback()
            return False
    
    def insert_sample_data(self) -> bool:
        """Insert sample data into the database"""
        try:
            # Insert product categories
            categories = [
                (1, "Electronics", "Electronic devices and accessories", None),
                (2, "Computers", "Computers and accessories", 1),
                (3, "Smartphones", "Mobile phones and accessories", 1),
                (4, "Clothing", "Apparel and fashion items", None),
                (5, "Men's Clothing", "Men's apparel", 4),
                (6, "Women's Clothing", "Women's apparel", 4)
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO product_categories (category_id, name, description, parent_category_id)
            VALUES (?, ?, ?, ?)
            """, categories)
            
            # Insert product attributes
            attributes = [
                (1, "Color", "Product color"),
                (2, "Size", "Product size"),
                (3, "Material", "Product material"),
                (4, "Storage", "Storage capacity"),
                (5, "RAM", "Memory capacity")
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO product_attributes (attribute_id, name, description)
            VALUES (?, ?, ?)
            """, attributes)
            
            # Insert products
            products = [
                (1, "LAPTOP-001", "Professional Laptop", "High-performance laptop for professionals", 2),
                (2, "PHONE-001", "Smartphone X", "Latest smartphone with advanced features", 3),
                (3, "TSHIRT-001", "Cotton T-Shirt", "Comfortable cotton t-shirt", 5)
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO products (product_id, sku, name, description, category_id)
            VALUES (?, ?, ?, ?, ?)
            """, products)
            
            # Insert product attribute values
            product_attr_values = [
                (1, 4, "512GB"),  # Laptop storage
                (1, 5, "16GB"),   # Laptop RAM
                (2, 1, "Black"),  # Phone color
                (2, 4, "128GB"),  # Phone storage
                (3, 1, "Blue"),   # T-shirt color
                (3, 3, "Cotton")  # T-shirt material
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO product_attribute_values (product_id, attribute_id, value)
            VALUES (?, ?, ?)
            """, product_attr_values)
            
            # Insert product variants
            variants = [
                (1, 1, "LAPTOP-001-SLV", "Professional Laptop - Silver", 1299.99, 10),
                (2, 1, "LAPTOP-001-BLK", "Professional Laptop - Black", 1299.99, 15),
                (3, 2, "PHONE-001-BLK-128", "Smartphone X - Black 128GB", 899.99, 20),
                (4, 2, "PHONE-001-WHT-128", "Smartphone X - White 128GB", 899.99, 15),
                (5, 3, "TSHIRT-001-BLU-S", "Cotton T-Shirt - Blue Small", 19.99, 25),
                (6, 3, "TSHIRT-001-BLU-M", "Cotton T-Shirt - Blue Medium", 19.99, 30),
                (7, 3, "TSHIRT-001-BLU-L", "Cotton T-Shirt - Blue Large", 19.99, 20)
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO product_variants (variant_id, product_id, sku, name, price, stock_quantity)
            VALUES (?, ?, ?, ?, ?, ?)
            """, variants)
            
            # Insert variant attributes
            variant_attr_values = [
                (1, 1, "Silver"),  # Laptop color - Silver
                (2, 1, "Black"),   # Laptop color - Black
                (3, 1, "Black"),   # Phone color - Black
                (4, 1, "White"),   # Phone color - White
                (5, 1, "Blue"),    # T-shirt color - Blue
                (6, 1, "Blue"),    # T-shirt color - Blue
                (7, 1, "Blue"),    # T-shirt color - Blue
                (5, 2, "Small"),   # T-shirt size - Small
                (6, 2, "Medium"),  # T-shirt size - Medium
                (7, 2, "Large")    # T-shirt size - Large
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO variant_attributes (variant_id, attribute_id, value)
            VALUES (?, ?, ?)
            """, variant_attr_values)
            
            # Insert customers
            customers = [
                (1, "john.doe@example.com", "hashed_password_1", "John", "Doe", "555-123-4567"),
                (2, "jane.smith@example.com", "hashed_password_2", "Jane", "Smith", "555-987-6543")
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO customers (customer_id, email, password_hash, first_name, last_name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
            """, customers)
            
            # Insert addresses
            addresses = [
                (1, 1, "billing", "123 Main St", "New York", "NY", "10001", "USA", 1),
                (2, 1, "shipping", "123 Main St", "New York", "NY", "10001", "USA", 1),
                (3, 2, "billing", "456 Oak Ave", "San Francisco", "CA", "94102", "USA", 1),
                (4, 2, "shipping", "789 Pine St", "San Francisco", "CA", "94103", "USA", 1)
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO addresses (address_id, customer_id, address_type, street_address, city, state, postal_code, country, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, addresses)
            
            # Insert orders
            orders = [
                (1, 1, "2023-01-15 10:30:00", "completed", 1, 2, "Standard Shipping", 10.00, 105.00, 1414.99, "Credit Card", None),
                (2, 2, "2023-02-20 14:45:00", "shipped", 3, 4, "Express Shipping", 20.00, 72.00, 991.99, "PayPal", "Leave at door")
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO orders (order_id, customer_id, order_date, status, billing_address_id, shipping_address_id, 
                                 shipping_method, shipping_cost, tax_amount, total_amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, orders)
            
            # Insert order items
            order_items = [
                (1, 1, 1, 1, 1299.99, 1299.99),  # Order 1, Laptop Silver
                (2, 2, 3, 1, 899.99, 899.99)     # Order 2, Phone Black
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO order_items (order_item_id, order_id, variant_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            """, order_items)
            
            # Insert payment transactions
            payments = [
                (1, 1, "2023-01-15 10:35:00", "Credit Card", 1414.99, "completed", "TXN123456"),
                (2, 2, "2023-02-20 14:50:00", "PayPal", 991.99, "completed", "TXN789012")
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO payment_transactions (transaction_id, order_id, transaction_date, payment_method, amount, status, reference_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, payments)
            
            # Insert product reviews
            reviews = [
                (1, 1, 1, 5, "Excellent laptop, very fast and reliable.", "2023-01-30 09:15:00", 1),
                (2, 2, 2, 4, "Great phone, good camera but battery life could be better.", "2023-03-05 16:20:00", 1)
            ]
            
            self.cursor.executemany("""
            INSERT OR IGNORE INTO product_reviews (review_id, product_id, customer_id, rating, review_text, review_date, is_verified_purchase)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, reviews)
            
            self.conn.commit()
            logging.info("Sample data inserted successfully")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error inserting sample data: {e}")
            self.conn.rollback()
            return False
    
    def execute_sample_queries(self):
        """Execute and display results of sample queries demonstrating the normalized schema"""
        try:
            print("\n=== Sample Queries on Normalized Schema ===\n")
            
            # Query 1: Get product details with category
            print("Query 1: Product details with category")
            self.cursor.execute("""
            SELECT p.product_id, p.name, p.sku, p.description, c.name as category_name
            FROM products p
            JOIN product_categories c ON p.category_id = c.category_id
            """)
            
            for row in self.cursor.fetchall():
                print(f"Product: {row['name']} (SKU: {row['sku']})")
                print(f"Category: {row['category_name']}")
                print(f"Description: {row['description']}")
                print()
            
            # Query 2: Get product variants with attributes
            print("Query 2: Product variants with attributes")
            self.cursor.execute("""
            SELECT p.name as product_name, v.name as variant_name, v.sku, v.price, v.stock_quantity,
                   a.name as attribute_name, va.value as attribute_value
            FROM product_variants v
            JOIN products p ON v.product_id = p.product_id
            JOIN variant_attributes va ON v.variant_id = va.variant_id
            JOIN product_attributes a ON va.attribute_id = a.attribute_id
            ORDER BY p.name, v.name, a.name
            """)
            
            current_variant = None
            for row in self.cursor.fetchall():
                if current_variant != row['variant_name']:
                    current_variant = row['variant_name']
                    print(f"\nVariant: {row['variant_name']} (SKU: {row['sku']})")
                    print(f"Product: {row['product_name']}")
                    print(f"Price: ${row['price']}, Stock: {row['stock_quantity']}")
                    print("Attributes:")
                
                print(f"  - {row['attribute_name']}: {row['attribute_value']}")
            
            # Query 3: Get order details with customer and items
            print("\nQuery 3: Order details with customer and items")
            self.cursor.execute("""
            SELECT o.order_id, o.order_date, o.status, o.total_amount,
                   c.first_name || ' ' || c.last_name as customer_name,
                   a_ship.street_address || ', ' || a_ship.city || ', ' || a_ship.state || ' ' || a_ship.postal_code as shipping_address,
                   p.name as product_name, v.name as variant_name, oi.quantity, oi.unit_price, oi.subtotal
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN addresses a_ship ON o.shipping_address_id = a_ship.address_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN product_variants v ON oi.variant_id = v.variant_id
            JOIN products p ON v.product_id = p.product_id
            ORDER BY o.order_date DESC, o.order_id
            """)
            
            current_order = None
            for row in self.cursor.fetchall():
                if current_order != row['order_id']:
                    current_order = row['order_id']
                    print(f"\nOrder #{row['order_id']} - {row['order_date']} - {row['status']}")
                    print(f"Customer: {row['customer_name']}")
                    print(f"Shipping Address: {row['shipping_address']}")
                    print(f"Total Amount: ${row['total_amount']}")
                    print("Items:")
                
                print(f"  - {row['variant_name']} x {row['quantity']} @ ${row['unit_price']} each = ${row['subtotal']}")
            
            # Query 4: Get product reviews with customer information
            print("\nQuery 4: Product reviews with customer information")
            self.cursor.execute("""
            SELECT p.name as product_name, r.rating, r.review_text, r.review_date,
                   c.first_name || ' ' || c.last_name as customer_name,
                   r.is_verified_purchase
            FROM product_reviews r
            JOIN products p ON r.product_id = p.product_id
            JOIN customers c ON r.customer_id = c.customer_id
            ORDER BY r.review_date DESC
            """)
            
            for row in self.cursor.fetchall():
                print(f"\nProduct: {row['product_name']}")
                print(f"Rating: {row['rating']}/5 stars")
                print(f"Review by: {row['customer_name']} on {row['review_date']}")
                print(f"Verified Purchase: {'Yes' if row['is_verified_purchase'] else 'No'}")
                print(f"Review: {row['review_text']}")
            
            # Query 5: Get sales by category
            print("\nQuery 5: Sales by category")
            self.cursor.execute("""
            SELECT c.name as category_name, COUNT(oi.order_item_id) as num_orders, 
                   SUM(oi.quantity) as total_quantity, SUM(oi.subtotal) as total_sales
            FROM order_items oi
            JOIN product_variants v ON oi.variant_id = v.variant_id
            JOIN products p ON v.product_id = p.product_id
            JOIN product_categories c ON p.category_id = c.category_id
            GROUP BY c.category_id
            ORDER BY total_sales DESC
            """)
            
            print("Category Sales Summary:")
            for row in self.cursor.fetchall():
                print(f"  - {row['category_name']}: {row['num_orders']} orders, {row['total_quantity']} items, ${row['total_sales']} total")
            
            print("\n=== End of Sample Queries ===\n")
        except sqlite3.Error as e:
            logging.error(f"Error executing sample queries: {e}")
    
    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")


def main():
    """Main function to demonstrate the normalized database schema"""
    # Initialize the database
    db = EcommerceDatabase()
    
    if not db.connect():
        sys.exit(1)
    
    # Create the schema
    db.initialize_schema()
    
    # Insert sample data
    db.insert_sample_data()
    
    # Execute sample queries
    db.execute_sample_queries()
    
    # Close the connection
    db.close()


if __name__ == "__main__":
    main() 