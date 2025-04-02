#!/usr/bin/env python3
"""
MongoDB Product Catalog Implementation

A production-ready implementation of a product catalog system using MongoDB.
Features document-based schema, indexing, transactions, and validation.
"""

import os
import sys
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any

import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure, OperationFailure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("mongodb.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class ProductCatalog:
    """MongoDB-based product catalog implementation"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.environ.get("MONGO_DB", "product_catalog")
        self.client = None
        self.db = None
    
    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            
            # Ping the server to check connection
            self.client.admin.command('ping')
            
            # Get database
            self.db = self.client[self.db_name]
            logging.info(f"Connected to MongoDB: {self.mongo_uri}")
            return True
        except ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def initialize_collections(self) -> bool:
        """Create collections with validation schemas and indexes"""
        try:
            # Create products collection with schema validation
            try:
                self.db.create_collection("products", validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["name", "sku", "price", "category"],
                        "properties": {
                            "name": {
                                "bsonType": "string",
                                "description": "Product name (required)"
                            },
                            "sku": {
                                "bsonType": "string",
                                "description": "Stock keeping unit (required, unique)"
                            },
                            "description": {
                                "bsonType": "string",
                                "description": "Product description"
                            },
                            "price": {
                                "bsonType": "number",
                                "minimum": 0,
                                "description": "Product price (required, non-negative)"
                            },
                            "category": {
                                "bsonType": "string",
                                "description": "Product category (required)"
                            },
                            "tags": {
                                "bsonType": "array",
                                "items": {
                                    "bsonType": "string"
                                }
                            },
                            "inventory": {
                                "bsonType": "object",
                                "required": ["quantity"],
                                "properties": {
                                    "quantity": {
                                        "bsonType": "int",
                                        "minimum": 0,
                                        "description": "Current stock quantity"
                                    },
                                    "warehouse": {
                                        "bsonType": "string",
                                        "description": "Warehouse location"
                                    }
                                }
                            },
                            "created_at": {
                                "bsonType": "date",
                                "description": "Creation timestamp"
                            },
                            "updated_at": {
                                "bsonType": "date",
                                "description": "Last update timestamp"
                            }
                        }
                    }
                })
                logging.info("Created 'products' collection with schema validation")
            except OperationFailure:
                # Collection might already exist
                logging.info("Products collection already exists")
            
            # Create categories collection
            try:
                self.db.create_collection("categories", validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["name", "slug"],
                        "properties": {
                            "name": {
                                "bsonType": "string",
                                "description": "Category name (required)"
                            },
                            "slug": {
                                "bsonType": "string",
                                "description": "URL-friendly identifier (required, unique)"
                            },
                            "description": {
                                "bsonType": "string",
                                "description": "Category description"
                            },
                            "parent_id": {
                                "bsonType": ["objectId", "null"],
                                "description": "Parent category ID for hierarchical structure"
                            }
                        }
                    }
                })
                logging.info("Created 'categories' collection with schema validation")
            except OperationFailure:
                logging.info("Categories collection already exists")
            
            # Create indexes
            # Products indexes
            products = self.db.products
            products.create_indexes([
                IndexModel([("sku", ASCENDING)], unique=True),
                IndexModel([("name", ASCENDING)]),
                IndexModel([("category", ASCENDING), ("price", ASCENDING)]),
                IndexModel([("tags", ASCENDING)]),
                IndexModel([("inventory.quantity", ASCENDING)])
            ])
            
            # Categories indexes
            categories = self.db.categories
            categories.create_indexes([
                IndexModel([("slug", ASCENDING)], unique=True),
                IndexModel([("parent_id", ASCENDING)])
            ])
            
            logging.info("Created indexes for products and categories collections")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize collections: {e}")
            return False
    
    def add_product(self, product_data: Dict[str, Any]) -> Optional[str]:
        """
        Add a new product to the catalog
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            str: Product ID if successful, None if failed
        """
        # Add timestamps
        now = datetime.utcnow()
        product_data["created_at"] = now
        product_data["updated_at"] = now
        
        # Ensure inventory object exists
        if "inventory" not in product_data:
            product_data["inventory"] = {"quantity": 0}
        
        try:
            result = self.db.products.insert_one(product_data)
            product_id = str(result.inserted_id)
            logging.info(f"Added new product: {product_data['name']} (ID: {product_id})")
            return product_id
        except DuplicateKeyError:
            logging.error(f"Product with SKU '{product_data.get('sku')}' already exists")
            return None
        except Exception as e:
            logging.error(f"Error adding product: {e}")
            return None
    
    def get_product(self, product_id: Optional[str] = None, sku: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve a product by ID or SKU
        
        Args:
            product_id: Product ID (ObjectId as string)
            sku: Product SKU
            
        Returns:
            Dict: Product data or None if not found
        """
        try:
            if product_id:
                query = {"_id": ObjectId(product_id)}
            elif sku:
                query = {"sku": sku}
            else:
                logging.error("Either product_id or sku must be provided")
                return None
            
            product = self.db.products.find_one(query)
            
            if not product:
                return None
            
            # Convert ObjectId to string for easier handling
            product["_id"] = str(product["_id"])
            return product
        except Exception as e:
            logging.error(f"Error retrieving product: {e}")
            return None
    
    def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update product information
        
        Args:
            product_id: Product ID
            update_data: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logging.warning(f"No product found with ID {product_id}")
                return False
            
            logging.info(f"Updated product ID {product_id}")
            return True
        except Exception as e:
            logging.error(f"Error updating product: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the catalog
        
        Args:
            product_id: Product ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.db.products.delete_one({"_id": ObjectId(product_id)})
            
            if result.deleted_count == 0:
                logging.warning(f"No product found with ID {product_id}")
                return False
            
            logging.info(f"Deleted product ID {product_id}")
            return True
        except Exception as e:
            logging.error(f"Error deleting product: {e}")
            return False
    
    def update_inventory(self, product_id: str, quantity_change: int, 
                         warehouse: Optional[str] = None) -> bool:
        """
        Update product inventory
        
        Args:
            product_id: Product ID
            quantity_change: Change in quantity (positive for increase, negative for decrease)
            warehouse: Optional warehouse location
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Start a session for transaction
            with self.client.start_session() as session:
                with session.start_transaction():
                    # Get current product to check inventory
                    product = self.db.products.find_one(
                        {"_id": ObjectId(product_id)},
                        session=session
                    )
                    
                    if not product:
                        logging.warning(f"No product found with ID {product_id}")
                        return False
                    
                    current_quantity = product.get("inventory", {}).get("quantity", 0)
                    new_quantity = current_quantity + quantity_change
                    
                    if new_quantity < 0:
                        logging.warning(f"Cannot reduce inventory below zero (current: {current_quantity}, change: {quantity_change})")
                        return False
                    
                    # Prepare update
                    update = {
                        "inventory.quantity": new_quantity,
                        "updated_at": datetime.utcnow()
                    }
                    
                    if warehouse:
                        update["inventory.warehouse"] = warehouse
                    
                    # Update the inventory
                    self.db.products.update_one(
                        {"_id": ObjectId(product_id)},
                        {"$set": update},
                        session=session
                    )
                    
                    logging.info(f"Updated inventory for product {product_id}: {current_quantity} -> {new_quantity}")
                    
            return True
        except Exception as e:
            logging.error(f"Error updating inventory: {e}")
            return False
    
    def search_products(self, 
                      query: Optional[str] = None,
                      category: Optional[str] = None,
                      min_price: Optional[float] = None,
                      max_price: Optional[float] = None,
                      tags: Optional[List[str]] = None,
                      in_stock: Optional[bool] = None,
                      sort_by: str = "name",
                      sort_order: int = 1,  # 1 for ascending, -1 for descending
                      skip: int = 0,
                      limit: int = 20) -> List[Dict]:
        """
        Search for products with various filters
        
        Returns:
            List[Dict]: List of products matching the criteria
        """
        try:
            # Build query filter
            filter_query = {}
            
            if query:
                filter_query["$or"] = [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"sku": {"$regex": query, "$options": "i"}}
                ]
            
            if category:
                filter_query["category"] = category
            
            price_query = {}
            if min_price is not None:
                price_query["$gte"] = min_price
            if max_price is not None:
                price_query["$lte"] = max_price
            if price_query:
                filter_query["price"] = price_query
            
            if tags:
                filter_query["tags"] = {"$all": tags}
            
            if in_stock is not None:
                if in_stock:
                    filter_query["inventory.quantity"] = {"$gt": 0}
                else:
                    filter_query["inventory.quantity"] = 0
            
            # Define sort options
            sort_options = {
                "name": ("name", sort_order),
                "price": ("price", sort_order),
                "date": ("created_at", sort_order)
            }
            
            sort_field, sort_direction = sort_options.get(sort_by, sort_options["name"])
            
            # Execute the query
            cursor = self.db.products.find(
                filter_query
            ).sort(sort_field, sort_direction).skip(skip).limit(limit)
            
            # Convert ObjectId to string
            results = []
            for product in cursor:
                product["_id"] = str(product["_id"])
                results.append(product)
            
            return results
        except Exception as e:
            logging.error(f"Error searching products: {e}")
            return []
    
    def add_category(self, name: str, slug: str, description: Optional[str] = None, 
                   parent_id: Optional[str] = None) -> Optional[str]:
        """
        Add a new product category
        
        Args:
            name: Category name
            slug: URL-friendly identifier
            description: Category description
            parent_id: Parent category ID for hierarchical structure
            
        Returns:
            str: Category ID if successful, None if failed
        """
        try:
            category_data = {
                "name": name,
                "slug": slug,
                "description": description
            }
            
            if parent_id:
                category_data["parent_id"] = ObjectId(parent_id)
            else:
                category_data["parent_id"] = None
            
            result = self.db.categories.insert_one(category_data)
            category_id = str(result.inserted_id)
            logging.info(f"Added new category: {name} (ID: {category_id})")
            return category_id
        except DuplicateKeyError:
            logging.error(f"Category with slug '{slug}' already exists")
            return None
        except Exception as e:
            logging.error(f"Error adding category: {e}")
            return None
    
    def get_category_tree(self) -> List[Dict]:
        """
        Retrieve the full category hierarchy
        
        Returns:
            List[Dict]: List of top-level categories with nested children
        """
        try:
            # First, get all categories
            all_categories = list(self.db.categories.find())
            
            # Convert ObjectId to string
            for category in all_categories:
                category["_id"] = str(category["_id"])
                if category["parent_id"]:
                    category["parent_id"] = str(category["parent_id"])
            
            # Create a lookup dictionary
            category_lookup = {str(cat["_id"]): cat for cat in all_categories}
            
            # Organize into a tree structure
            root_categories = []
            
            for category in all_categories:
                # Add children array to each category
                category["children"] = []
                
                # If it's a root category (no parent), add to root list
                if not category["parent_id"]:
                    root_categories.append(category)
                else:
                    # Add this category as a child of its parent
                    parent = category_lookup.get(category["parent_id"])
                    if parent:
                        parent["children"].append(category)
            
            return root_categories
        except Exception as e:
            logging.error(f"Error retrieving category tree: {e}")
            return []
    
    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed")


def main():
    """Example usage of the ProductCatalog class"""
    catalog = ProductCatalog()
    
    if not catalog.connect():
        sys.exit(1)
    
    # Initialize collections and indexes
    catalog.initialize_collections()
    
    # Add categories
    electronics_id = catalog.add_category(
        name="Electronics",
        slug="electronics",
        description="Electronic devices and accessories"
    )
    
    phones_id = catalog.add_category(
        name="Smartphones",
        slug="smartphones",
        description="Mobile phones and accessories",
        parent_id=electronics_id
    )
    
    # Add products
    smartphone = {
        "name": "Premium Smartphone X1",
        "sku": "PHONE-X1-2023",
        "description": "High-end smartphone with advanced camera and fast processor",
        "price": 799.99,
        "category": "Smartphones",
        "tags": ["electronics", "smartphone", "camera", "5G"],
        "inventory": {
            "quantity": 25,
            "warehouse": "East"
        }
    }
    
    phone_id = catalog.add_product(smartphone)
    
    # Add another product
    tablet = {
        "name": "Pro Tablet T5",
        "sku": "TABLET-T5-2023",
        "description": "Professional tablet with stylus support and high-resolution display",
        "price": 649.99,
        "category": "Electronics",
        "tags": ["electronics", "tablet", "stylus"],
        "inventory": {
            "quantity": 15,
            "warehouse": "West"
        }
    }
    
    tablet_id = catalog.add_product(tablet)
    
    # Update product
    catalog.update_product(phone_id, {
        "price": 849.99,
        "description": "High-end smartphone with advanced camera system and ultrafast processor"
    })
    
    # Update inventory
    catalog.update_inventory(phone_id, -5)  # Decrease by 5
    catalog.update_inventory(tablet_id, 10)  # Increase by 10
    
    # Search for products
    results = catalog.search_products(
        query="pro",
        min_price=600,
        in_stock=True,
        sort_by="price",
        sort_order=-1  # descending
    )
    
    print(f"Found {len(results)} matching products:")
    for product in results:
        print(f"{product['name']} - ${product['price']} - {product['inventory']['quantity']} in stock")
    
    # Get category tree
    categories = catalog.get_category_tree()
    
    print("\nCategory tree:")
    for category in categories:
        print(f"- {category['name']}")
        for child in category.get("children", []):
            print(f"  - {child['name']}")
    
    # Cleanup
    catalog.close()

if __name__ == "__main__":
    main() 