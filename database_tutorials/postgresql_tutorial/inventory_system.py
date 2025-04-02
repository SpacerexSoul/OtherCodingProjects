#!/usr/bin/env python3
"""
PostgreSQL Inventory Management System

A production-grade implementation of an inventory management system using PostgreSQL.
Features advanced PostgreSQL capabilities, connection pooling, and transaction management.
"""

import os
import sys
import logging
import psycopg2
import psycopg2.extras
import psycopg2.pool
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("inventory_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class InventorySystem:
    """PostgreSQL-based inventory management system implementation"""
    
    def __init__(self):
        """Initialize the inventory system with database connection parameters"""
        self.host = os.environ.get("POSTGRES_HOST", "localhost")
        self.port = os.environ.get("POSTGRES_PORT", "5432")
        self.dbname = os.environ.get("POSTGRES_DB", "inventory")
        self.user = os.environ.get("POSTGRES_USER", "postgres")
        self.password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        
        self.connection_pool = None
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish connection pool to PostgreSQL database"""
        try:
            # Create connection string
            dsn = f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"
            
            # Create a connection pool with min 1, max 10 connections
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn)
            
            # Test the connection
            conn = self.get_connection()
            if conn:
                self.return_connection(conn)
                logging.info(f"Connected to PostgreSQL database: {self.dbname} on {self.host}")
                return True
            return False
        except psycopg2.Error as e:
            logging.error(f"Database connection error: {e}")
            return False
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            conn = self.connection_pool.getconn()
            # Set autocommit to False for transaction control
            conn.autocommit = False
            return conn
        except psycopg2.Error as e:
            logging.error(f"Error getting connection from pool: {e}")
            return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.connection_pool.putconn(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logging.info("Closed all database connections")
    
    def initialize_schema(self) -> bool:
        """Create tables, indexes, and stored procedures if they don't exist"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create product categories table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create products table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                sku VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category_id INTEGER REFERENCES product_categories(category_id),
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                cost DECIMAL(10, 2) CHECK (cost >= 0),
                weight DECIMAL(8, 2),
                dimensions VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create warehouses table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                manager VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create inventory table (tracks stock levels)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
                quantity INTEGER NOT NULL DEFAULT 0,
                min_stock_level INTEGER DEFAULT 0,
                max_stock_level INTEGER,
                last_stock_check TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (product_id, warehouse_id)
            )
            """)
            
            # Create inventory transactions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                transaction_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
                quantity INTEGER NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                reference_id VARCHAR(50),
                notes TEXT,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100)
            )
            """)
            
            # Create suppliers table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                contact_name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create purchase orders table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_id SERIAL PRIMARY KEY,
                supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_delivery TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                total_amount DECIMAL(12, 2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create purchase order items table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS po_items (
                item_id SERIAL PRIMARY KEY,
                po_id INTEGER NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                received_quantity INTEGER DEFAULT 0,
                warehouse_id INTEGER REFERENCES warehouses(warehouse_id)
            )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON products(category_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory(warehouse_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_product ON inventory_transactions(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_date ON inventory_transactions(transaction_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_supplier ON purchase_orders(supplier_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_items_po ON po_items(po_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_items_product ON po_items(product_id)")
            
            # Create a function to update the updated_at timestamp
            cursor.execute("""
            CREATE OR REPLACE FUNCTION update_modified_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """)
            
            # Create triggers for updated_at timestamps
            for table in ["product_categories", "products", "warehouses", "inventory", "purchase_orders", "suppliers"]:
                cursor.execute(f"""
                DROP TRIGGER IF EXISTS update_{table}_timestamp ON {table};
                CREATE TRIGGER update_{table}_timestamp
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_modified_column();
                """)
            
            # Create a function for inventory transactions
            cursor.execute("""
            CREATE OR REPLACE FUNCTION process_inventory_transaction(
                p_product_id INTEGER,
                p_warehouse_id INTEGER,
                p_quantity INTEGER,
                p_transaction_type VARCHAR,
                p_reference_id VARCHAR,
                p_notes TEXT,
                p_created_by VARCHAR
            )
            RETURNS INTEGER AS $$
            DECLARE
                v_transaction_id INTEGER;
                v_current_quantity INTEGER;
                v_new_quantity INTEGER;
            BEGIN
                -- Insert the transaction record
                INSERT INTO inventory_transactions (
                    product_id, warehouse_id, quantity, transaction_type,
                    reference_id, notes, created_by
                ) VALUES (
                    p_product_id, p_warehouse_id, p_quantity, p_transaction_type,
                    p_reference_id, p_notes, p_created_by
                ) RETURNING transaction_id INTO v_transaction_id;
                
                -- Get current inventory level
                SELECT quantity INTO v_current_quantity
                FROM inventory
                WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;
                
                IF NOT FOUND THEN
                    -- No inventory record exists, create one
                    IF p_transaction_type IN ('receive', 'adjustment_add') THEN
                        v_new_quantity := p_quantity;
                    ELSE
                        RAISE EXCEPTION 'Cannot remove inventory that does not exist';
                    END IF;
                    
                    INSERT INTO inventory (product_id, warehouse_id, quantity)
                    VALUES (p_product_id, p_warehouse_id, v_new_quantity);
                ELSE
                    -- Update existing inventory
                    IF p_transaction_type IN ('receive', 'adjustment_add') THEN
                        v_new_quantity := v_current_quantity + p_quantity;
                    ELSIF p_transaction_type IN ('ship', 'adjustment_subtract') THEN
                        v_new_quantity := v_current_quantity - p_quantity;
                        IF v_new_quantity < 0 THEN
                            RAISE EXCEPTION 'Insufficient inventory';
                        END IF;
                    ELSE
                        RAISE EXCEPTION 'Unknown transaction type: %', p_transaction_type;
                    END IF;
                    
                    UPDATE inventory
                    SET quantity = v_new_quantity, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;
                END IF;
                
                RETURN v_transaction_id;
            END;
            $$ LANGUAGE plpgsql;
            """)
            
            conn.commit()
            logging.info("Database schema initialized successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Schema initialization error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def add_category(self, name: str, description: Optional[str] = None) -> Optional[int]:
        """
        Add a new product category
        
        Args:
            name: Category name
            description: Category description
            
        Returns:
            int: Category ID if successful, None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO product_categories (name, description)
            VALUES (%s, %s)
            RETURNING category_id
            """, (name, description))
            
            category_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"Added new category: {name} (ID: {category_id})")
            return category_id
        except psycopg2.Error as e:
            logging.error(f"Error adding category: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_categories(self) -> List[Dict]:
        """
        Retrieve all product categories
        
        Returns:
            List[Dict]: List of categories
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cursor.execute("""
            SELECT category_id, name, description, created_at, updated_at
            FROM product_categories
            ORDER BY name
            """)
            
            categories = [dict(row) for row in cursor.fetchall()]
            return categories
        except psycopg2.Error as e:
            logging.error(f"Error retrieving categories: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def add_product(self, sku: str, name: str, price: Decimal, 
                  category_id: Optional[int] = None, description: Optional[str] = None,
                  cost: Optional[Decimal] = None, weight: Optional[Decimal] = None,
                  dimensions: Optional[str] = None) -> Optional[int]:
        """
        Add a new product
        
        Args:
            sku: Stock keeping unit (unique identifier)
            name: Product name
            price: Selling price
            category_id: Category ID (optional)
            description: Product description
            cost: Product cost
            weight: Product weight
            dimensions: Product dimensions
            
        Returns:
            int: Product ID if successful, None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO products (sku, name, price, category_id, description, cost, weight, dimensions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING product_id
            """, (sku, name, price, category_id, description, cost, weight, dimensions))
            
            product_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"Added new product: {name} (ID: {product_id})")
            return product_id
        except psycopg2.Error as e:
            logging.error(f"Error adding product: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_product(self, product_id: Optional[int] = None, sku: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve a product by ID or SKU
        
        Args:
            product_id: Product ID
            sku: Product SKU
            
        Returns:
            Dict: Product data or None if not found
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if product_id:
                cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN product_categories c ON p.category_id = c.category_id
                WHERE p.product_id = %s
                """, (product_id,))
            elif sku:
                cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN product_categories c ON p.category_id = c.category_id
                WHERE p.sku = %s
                """, (sku,))
            else:
                logging.error("Either product_id or sku must be provided")
                return None
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return dict(row)
        except psycopg2.Error as e:
            logging.error(f"Error retrieving product: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """
        Update product information
        
        Args:
            product_id: Product ID
            **kwargs: Fields to update (name, price, category_id, description, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        valid_fields = ["sku", "name", "price", "category_id", "description", 
                        "cost", "weight", "dimensions"]
        
        # Filter valid fields
        update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not update_data:
            logging.warning("No valid update fields provided")
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build query dynamically
            placeholders = ", ".join([f"{field} = %s" for field in update_data.keys()])
            values = list(update_data.values())
            values.append(product_id)  # For the WHERE clause
            
            query = f"""
            UPDATE products
            SET {placeholders}
            WHERE product_id = %s
            """
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                logging.warning(f"No product found with ID {product_id}")
                conn.rollback()
                return False
            
            conn.commit()
            logging.info(f"Updated product ID {product_id}")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error updating product: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product
        
        Args:
            product_id: Product ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if product has inventory
            cursor.execute("""
            SELECT SUM(quantity) FROM inventory WHERE product_id = %s
            """, (product_id,))
            
            inventory_count = cursor.fetchone()[0] or 0
            if inventory_count > 0:
                logging.warning(f"Cannot delete product ID {product_id} with existing inventory")
                return False
            
            # Delete the product
            cursor.execute("""
            DELETE FROM products WHERE product_id = %s
            """, (product_id,))
            
            if cursor.rowcount == 0:
                logging.warning(f"No product found with ID {product_id}")
                conn.rollback()
                return False
            
            conn.commit()
            logging.info(f"Deleted product ID {product_id}")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error deleting product: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def add_warehouse(self, name: str, location: Optional[str] = None,
                    manager: Optional[str] = None, phone: Optional[str] = None,
                    email: Optional[str] = None) -> Optional[int]:
        """
        Add a new warehouse
        
        Args:
            name: Warehouse name
            location: Warehouse location
            manager: Warehouse manager name
            phone: Contact phone
            email: Contact email
            
        Returns:
            int: Warehouse ID if successful, None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO warehouses (name, location, manager, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING warehouse_id
            """, (name, location, manager, phone, email))
            
            warehouse_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"Added new warehouse: {name} (ID: {warehouse_id})")
            return warehouse_id
        except psycopg2.Error as e:
            logging.error(f"Error adding warehouse: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_warehouses(self) -> List[Dict]:
        """
        Retrieve all warehouses
        
        Returns:
            List[Dict]: List of warehouses
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cursor.execute("""
            SELECT warehouse_id, name, location, manager, phone, email, created_at, updated_at
            FROM warehouses
            ORDER BY name
            """)
            
            warehouses = [dict(row) for row in cursor.fetchall()]
            return warehouses
        except psycopg2.Error as e:
            logging.error(f"Error retrieving warehouses: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def update_inventory(self, product_id: int, warehouse_id: int, 
                       quantity_change: int, transaction_type: str,
                       reference_id: Optional[str] = None, 
                       notes: Optional[str] = None,
                       created_by: Optional[str] = None) -> Optional[int]:
        """
        Update inventory levels using the process_inventory_transaction function
        
        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID
            quantity_change: Change in quantity (positive for increase, negative for decrease)
            transaction_type: Type of transaction (receive, ship, adjustment_add, adjustment_subtract)
            reference_id: Reference ID (e.g., order number, PO number)
            notes: Transaction notes
            created_by: User who created the transaction
            
        Returns:
            int: Transaction ID if successful, None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validate transaction type
            valid_types = ['receive', 'ship', 'adjustment_add', 'adjustment_subtract']
            if transaction_type not in valid_types:
                logging.error(f"Invalid transaction type: {transaction_type}")
                return None
            
            # For ship or adjustment_subtract, ensure quantity_change is negative
            if transaction_type in ['ship', 'adjustment_subtract']:
                quantity_change = -abs(quantity_change)
            else:
                quantity_change = abs(quantity_change)
            
            # Call the stored function
            cursor.execute("""
            SELECT process_inventory_transaction(%s, %s, %s, %s, %s, %s, %s)
            """, (product_id, warehouse_id, quantity_change, transaction_type, 
                  reference_id, notes, created_by))
            
            transaction_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"Processed inventory transaction: {transaction_type} {quantity_change} units of product {product_id}")
            return transaction_id
        except psycopg2.Error as e:
            logging.error(f"Error updating inventory: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_inventory_levels(self, product_id: Optional[int] = None, 
                           warehouse_id: Optional[int] = None) -> List[Dict]:
        """
        Get current inventory levels, optionally filtered by product or warehouse
        
        Args:
            product_id: Filter by product ID
            warehouse_id: Filter by warehouse ID
            
        Returns:
            List[Dict]: List of inventory records
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            query = """
            SELECT i.inventory_id, i.product_id, p.name as product_name, p.sku,
                   i.warehouse_id, w.name as warehouse_name, i.quantity,
                   i.min_stock_level, i.max_stock_level, i.last_stock_check
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN warehouses w ON i.warehouse_id = w.warehouse_id
            """
            
            params = []
            conditions = []
            
            if product_id:
                conditions.append("i.product_id = %s")
                params.append(product_id)
            
            if warehouse_id:
                conditions.append("i.warehouse_id = %s")
                params.append(warehouse_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.name, w.name"
            
            cursor.execute(query, params)
            
            inventory = [dict(row) for row in cursor.fetchall()]
            return inventory
        except psycopg2.Error as e:
            logging.error(f"Error retrieving inventory levels: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_inventory_transactions(self, product_id: Optional[int] = None,
                                 warehouse_id: Optional[int] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 transaction_type: Optional[str] = None,
                                 limit: int = 100) -> List[Dict]:
        """
        Get inventory transaction history with optional filters
        
        Args:
            product_id: Filter by product ID
            warehouse_id: Filter by warehouse ID
            start_date: Filter by start date
            end_date: Filter by end date
            transaction_type: Filter by transaction type
            limit: Maximum number of records to return
            
        Returns:
            List[Dict]: List of transaction records
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            query = """
            SELECT t.transaction_id, t.product_id, p.name as product_name, p.sku,
                   t.warehouse_id, w.name as warehouse_name, t.quantity,
                   t.transaction_type, t.reference_id, t.notes, t.transaction_date,
                   t.created_by
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            """
            
            params = []
            conditions = []
            
            if product_id:
                conditions.append("t.product_id = %s")
                params.append(product_id)
            
            if warehouse_id:
                conditions.append("t.warehouse_id = %s")
                params.append(warehouse_id)
            
            if start_date:
                conditions.append("t.transaction_date >= %s")
                params.append(start_date)
            
            if end_date:
                conditions.append("t.transaction_date <= %s")
                params.append(end_date)
            
            if transaction_type:
                conditions.append("t.transaction_type = %s")
                params.append(transaction_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY t.transaction_date DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            
            transactions = [dict(row) for row in cursor.fetchall()]
            return transactions
        except psycopg2.Error as e:
            logging.error(f"Error retrieving inventory transactions: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_low_stock_products(self, warehouse_id: Optional[int] = None) -> List[Dict]:
        """
        Get products with stock levels below their minimum threshold
        
        Args:
            warehouse_id: Optional warehouse ID to filter by
            
        Returns:
            List[Dict]: List of products with low stock
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            query = """
            SELECT i.inventory_id, i.product_id, p.name as product_name, p.sku,
                   i.warehouse_id, w.name as warehouse_name, i.quantity,
                   i.min_stock_level, (i.min_stock_level - i.quantity) as shortage
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN warehouses w ON i.warehouse_id = w.warehouse_id
            WHERE i.quantity < i.min_stock_level
            """
            
            params = []
            
            if warehouse_id:
                query += " AND i.warehouse_id = %s"
                params.append(warehouse_id)
            
            query += " ORDER BY shortage DESC"
            
            cursor.execute(query, params)
            
            low_stock = [dict(row) for row in cursor.fetchall()]
            return low_stock
        except psycopg2.Error as e:
            logging.error(f"Error retrieving low stock products: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)


def main():
    """Example usage of the InventorySystem class"""
    # Initialize the inventory system
    inventory_system = InventorySystem()
    
    if not inventory_system.connect():
        sys.exit(1)
    
    # Initialize schema
    inventory_system.initialize_schema()
    
    # Add product categories
    electronics_id = inventory_system.add_category(
        name="Electronics",
        description="Electronic devices and accessories"
    )
    
    furniture_id = inventory_system.add_category(
        name="Furniture",
        description="Office and home furniture"
    )
    
    # Add warehouses
    east_warehouse_id = inventory_system.add_warehouse(
        name="East Warehouse",
        location="123 East St, New York, NY",
        manager="John Smith",
        phone="555-123-4567",
        email="john.smith@example.com"
    )
    
    west_warehouse_id = inventory_system.add_warehouse(
        name="West Warehouse",
        location="456 West Ave, San Francisco, CA",
        manager="Jane Doe",
        phone="555-987-6543",
        email="jane.doe@example.com"
    )
    
    # Add products
    laptop_id = inventory_system.add_product(
        sku="LAPTOP-PRO-15",
        name="Professional Laptop 15\"",
        price=Decimal("1299.99"),
        category_id=electronics_id,
        description="High-performance laptop for professionals",
        cost=Decimal("950.00"),
        weight=Decimal("2.5"),
        dimensions="15x10x1 inches"
    )
    
    desk_id = inventory_system.add_product(
        sku="DESK-OAK-L",
        name="Large Oak Desk",
        price=Decimal("399.99"),
        category_id=furniture_id,
        description="Spacious oak desk for home office",
        cost=Decimal("250.00"),
        weight=Decimal("45.0"),
        dimensions="60x30x29 inches"
    )
    
    # Add inventory transactions
    # Receive laptops at East Warehouse
    inventory_system.update_inventory(
        product_id=laptop_id,
        warehouse_id=east_warehouse_id,
        quantity_change=20,
        transaction_type="receive",
        reference_id="PO-12345",
        notes="Initial stock",
        created_by="system"
    )
    
    # Receive desks at West Warehouse
    inventory_system.update_inventory(
        product_id=desk_id,
        warehouse_id=west_warehouse_id,
        quantity_change=15,
        transaction_type="receive",
        reference_id="PO-12346",
        notes="Initial stock",
        created_by="system"
    )
    
    # Ship some laptops from East Warehouse
    inventory_system.update_inventory(
        product_id=laptop_id,
        warehouse_id=east_warehouse_id,
        quantity_change=5,
        transaction_type="ship",
        reference_id="ORD-5678",
        notes="Customer order",
        created_by="system"
    )
    
    # Get inventory levels
    inventory_levels = inventory_system.get_inventory_levels()
    print("\nCurrent Inventory Levels:")
    for item in inventory_levels:
        print(f"{item['product_name']} at {item['warehouse_name']}: {item['quantity']} units")
    
    # Get transaction history for laptops
    laptop_transactions = inventory_system.get_inventory_transactions(product_id=laptop_id)
    print("\nLaptop Transaction History:")
    for tx in laptop_transactions:
        print(f"{tx['transaction_date']}: {tx['transaction_type']} {abs(tx['quantity'])} units - {tx['notes']}")
    
    # Update product information
    inventory_system.update_product(
        laptop_id,
        price=Decimal("1199.99"),
        description="High-performance laptop for professionals with extended battery life"
    )
    
    # Get updated product information
    laptop = inventory_system.get_product(product_id=laptop_id)
    print(f"\nUpdated Laptop Information:")
    print(f"Name: {laptop['name']}")
    print(f"Price: ${laptop['price']}")
    print(f"Description: {laptop['description']}")
    
    # Clean up
    inventory_system.close()


if __name__ == "__main__":
    main()
