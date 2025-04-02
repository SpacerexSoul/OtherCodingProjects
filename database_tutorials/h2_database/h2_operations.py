#!/usr/bin/env python3
"""
H2 Database Operations

Production-ready implementation of database operations for a 
customer management system using H2 database.

Dependencies: jaydebeapi
"""

import jaydebeapi
import logging
from datetime import datetime
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("database.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class CustomerDatabase:
    """Database manager for customer data using H2 database"""
    
    def __init__(self, db_path="~/customer_db", jar_path="lib/h2-2.2.224.jar"):
        """Initialize the database connection"""
        self.jar_path = os.path.expanduser(jar_path)
        self.db_path = os.path.expanduser(db_path)
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to the H2 database"""
        try:
            # Connection parameters
            jdbc_driver = "org.h2.Driver"
            jdbc_url = f"jdbc:h2:{self.db_path}"
            user = "admin"
            password = "secure_password"  # In production, use env vars or secret manager
            
            # Connect to the database
            self.connection = jaydebeapi.connect(
                jdbc_driver,
                jdbc_url,
                [user, password],
                self.jar_path
            )
            
            self.cursor = self.connection.cursor()
            logging.info("Connected to H2 database successfully")
            return True
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            return False
    
    def initialize_schema(self):
        """Create tables and indexes if they don't exist"""
        try:
            # Create customers table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20),
                address VARCHAR(200),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create orders table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                customer_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
            """)
            
            # Create indexes for performance
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email)
            """)
            
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_customer ON orders(customer_id)
            """)
            
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date)
            """)
            
            self.connection.commit()
            logging.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Schema initialization error: {e}")
            self.connection.rollback()
            return False
    
    def add_customer(self, first_name, last_name, email, phone=None, address=None):
        """
        Add a new customer to the database
        
        Returns: customer_id if successful, None if failed
        """
        try:
            self.cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone, address))
            
            # Get the auto-generated ID
            self.cursor.execute("CALL IDENTITY()")
            customer_id = self.cursor.fetchone()[0]
            
            self.connection.commit()
            logging.info(f"Added new customer: {first_name} {last_name} (ID: {customer_id})")
            return customer_id
        except Exception as e:
            logging.error(f"Error adding customer: {e}")
            self.connection.rollback()
            return None
    
    def get_customer(self, customer_id=None, email=None):
        """
        Retrieve customer by ID or email
        
        Returns: Customer data as dictionary or None if not found
        """
        try:
            if customer_id:
                self.cursor.execute("""
                SELECT customer_id, first_name, last_name, email, phone, address, 
                       registration_date, last_updated
                FROM customers
                WHERE customer_id = ?
                """, (customer_id,))
            elif email:
                self.cursor.execute("""
                SELECT customer_id, first_name, last_name, email, phone, address, 
                       registration_date, last_updated
                FROM customers
                WHERE email = ?
                """, (email,))
            else:
                logging.error("Either customer_id or email must be provided")
                return None
            
            result = self.cursor.fetchone()
            if not result:
                return None
            
            # Convert to dictionary
            columns = ["customer_id", "first_name", "last_name", "email", 
                       "phone", "address", "registration_date", "last_updated"]
            return dict(zip(columns, result))
        except Exception as e:
            logging.error(f"Error retrieving customer: {e}")
            return None
    
    def update_customer(self, customer_id, **kwargs):
        """
        Update customer information
        
        Args:
            customer_id: ID of the customer to update
            **kwargs: Fields to update (first_name, last_name, email, phone, address)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not kwargs:
            logging.warning("No update parameters provided")
            return False
        
        # Prepare the SQL query dynamically based on provided fields
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ["first_name", "last_name", "email", "phone", "address"]:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            logging.warning("No valid update fields provided")
            return False
        
        # Add last_updated timestamp
        update_fields.append("last_updated = ?")
        values.append(datetime.now())
        
        # Add customer_id to values
        values.append(customer_id)
        
        try:
            query = f"""
            UPDATE customers
            SET {", ".join(update_fields)}
            WHERE customer_id = ?
            """
            
            self.cursor.execute(query, values)
            if self.cursor.rowcount == 0:
                logging.warning(f"No customer found with ID {customer_id}")
                self.connection.rollback()
                return False
            
            self.connection.commit()
            logging.info(f"Updated customer ID {customer_id}")
            return True
        except Exception as e:
            logging.error(f"Error updating customer: {e}")
            self.connection.rollback()
            return False
    
    def delete_customer(self, customer_id):
        """
        Delete a customer and all associated orders
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Start a transaction
            self.cursor.execute("START TRANSACTION")
            
            # Delete associated orders first (due to foreign key constraint)
            self.cursor.execute("""
            DELETE FROM orders
            WHERE customer_id = ?
            """, (customer_id,))
            orders_deleted = self.cursor.rowcount
            
            # Delete the customer
            self.cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = ?
            """, (customer_id,))
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No customer found with ID {customer_id}")
                self.connection.rollback()
                return False
            
            self.connection.commit()
            logging.info(f"Deleted customer ID {customer_id} and {orders_deleted} associated orders")
            return True
        except Exception as e:
            logging.error(f"Error deleting customer: {e}")
            self.connection.rollback()
            return False
    
    def add_order(self, customer_id, total_amount, status="pending"):
        """
        Create a new order for a customer
        
        Returns: order_id if successful, None if failed
        """
        try:
            self.cursor.execute("""
            INSERT INTO orders (customer_id, total_amount, status)
            VALUES (?, ?, ?)
            """, (customer_id, total_amount, status))
            
            # Get the auto-generated ID
            self.cursor.execute("CALL IDENTITY()")
            order_id = self.cursor.fetchone()[0]
            
            self.connection.commit()
            logging.info(f"Added new order #{order_id} for customer #{customer_id}")
            return order_id
        except Exception as e:
            logging.error(f"Error adding order: {e}")
            self.connection.rollback()
            return None
    
    def get_customer_orders(self, customer_id):
        """
        Retrieve all orders for a specific customer
        
        Returns: List of orders or empty list if none found
        """
        try:
            self.cursor.execute("""
            SELECT order_id, customer_id, order_date, total_amount, status
            FROM orders
            WHERE customer_id = ?
            ORDER BY order_date DESC
            """, (customer_id,))
            
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = ["order_id", "customer_id", "order_date", "total_amount", "status"]
            orders = [dict(zip(columns, row)) for row in results]
            
            return orders
        except Exception as e:
            logging.error(f"Error retrieving customer orders: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")


def main():
    """Example usage of the CustomerDatabase class"""
    # Initialize the database
    db = CustomerDatabase()
    
    if not db.connect():
        sys.exit(1)
    
    # Initialize schema (tables and indexes)
    db.initialize_schema()
    
    # Example: Add new customers
    customer1_id = db.add_customer(
        "John", "Doe", "john.doe@example.com", 
        phone="555-123-4567", 
        address="123 Main St, City, State 12345"
    )
    
    customer2_id = db.add_customer(
        "Jane", "Smith", "jane.smith@example.com",
        phone="555-987-6543",
        address="456 Oak Ave, Town, State 12345"
    )
    
    # Example: Retrieve customer info
    customer = db.get_customer(customer_id=customer1_id)
    if customer:
        print(f"Retrieved customer: {customer['first_name']} {customer['last_name']}")
    
    # Example: Update customer
    db.update_customer(customer1_id, phone="555-111-2222", address="789 Pine St, City, State 12345")
    
    # Example: Add orders
    order1_id = db.add_order(customer1_id, 125.99, "completed")
    order2_id = db.add_order(customer1_id, 89.99, "pending")
    order3_id = db.add_order(customer2_id, 245.50, "shipped")
    
    # Example: Retrieve customer orders
    orders = db.get_customer_orders(customer1_id)
    print(f"Customer {customer1_id} has {len(orders)} orders:")
    for order in orders:
        print(f"  Order #{order['order_id']}: ${order['total_amount']} - {order['status']}")
    
    # Cleanup
    db.close()

if __name__ == "__main__":
    main() 