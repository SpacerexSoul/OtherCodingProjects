#!/usr/bin/env python3
"""
Data Science Integration with Databases

This module demonstrates how to extract data from databases and perform
data science operations using pandas, NumPy, and scikit-learn.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_sample_database(db_path):
    """
    Create a sample database with customer and order data for analysis
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    logger.info(f"Creating sample database at {db_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        age INTEGER,
        gender TEXT,
        location TEXT,
        income REAL,
        signup_date TEXT,
        last_login TEXT
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total_amount REAL,
        status TEXT,
        payment_method TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')
    
    # Insert sample customer data
    sample_customers = []
    locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
                'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    genders = ['Male', 'Female', 'Non-binary']
    
    # Generate random signup dates between 1-3 years ago
    today = datetime.now()
    start_date = today - timedelta(days=365*3)
    
    for i in range(1, 201):  # 200 customers
        name = f"Customer {i}"
        email = f"customer{i}@example.com"
        age = random.randint(18, 75)
        gender = random.choice(genders)
        location = random.choice(locations)
        income = round(random.uniform(30000, 150000), 2)
        
        # Random signup date
        days_ago = random.randint(0, (today - start_date).days)
        signup_date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Random last login (after signup)
        last_login_days = random.randint(0, days_ago)
        last_login = (today - timedelta(days=last_login_days)).strftime('%Y-%m-%d')
        
        sample_customers.append((
            i, name, email, age, gender, location, income, signup_date, last_login
        ))
    
    cursor.executemany('''
    INSERT OR REPLACE INTO customers 
    (customer_id, name, email, age, gender, location, income, signup_date, last_login)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_customers)
    
    # Insert sample order data
    sample_orders = []
    statuses = ['completed', 'shipped', 'processing', 'cancelled']
    payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'crypto']
    
    order_id = 1
    for customer_id in range(1, 201):
        # Each customer has 0-15 orders
        num_orders = random.randint(0, 15)
        
        for _ in range(num_orders):
            # Order date after signup
            customer_signup = next(date for id, _, _, _, _, _, _, date, _ in sample_customers if id == customer_id)
            signup_date_obj = datetime.strptime(customer_signup, '%Y-%m-%d')
            
            days_after_signup = random.randint(1, (today - signup_date_obj).days)
            order_date = (signup_date_obj + timedelta(days=days_after_signup)).strftime('%Y-%m-%d')
            
            total_amount = round(random.uniform(10, 500), 2)
            status = random.choice(statuses)
            payment_method = random.choice(payment_methods)
            
            sample_orders.append((
                order_id, customer_id, order_date, total_amount, status, payment_method
            ))
            order_id += 1
    
    cursor.executemany('''
    INSERT OR REPLACE INTO orders 
    (order_id, customer_id, order_date, total_amount, status, payment_method)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_orders)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    logger.info(f"Sample database created with {len(sample_customers)} customers and {len(sample_orders)} orders")
    return True

def extract_data_from_db(db_path):
    """
    Extract data from the database using pandas
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        DataFrame: Pandas DataFrame with customer and order data
    """
    logger.info(f"Extracting data from {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Query to join customers and orders tables
    query = """
    SELECT c.customer_id, c.name, c.age, c.gender, c.location, c.income,
           c.signup_date, c.last_login,
           COUNT(o.order_id) AS order_count,
           SUM(o.total_amount) AS total_spent,
           AVG(o.total_amount) AS avg_order_value,
           MAX(o.order_date) AS last_order_date,
           julianday('now') - julianday(MAX(o.order_date)) AS days_since_last_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
    """
    
    # Load data into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    logger.info(f"Extracted data for {len(df)} customers")
    return df

def data_cleaning_and_preprocessing(df):
    """
    Clean and preprocess the data
    
    Args:
        df (DataFrame): Raw data from the database
        
    Returns:
        DataFrame: Cleaned and preprocessed data
    """
    logger.info("Cleaning and preprocessing data")
    
    # Handle missing values
    df['total_spent'].fillna(0, inplace=True)
    df['avg_order_value'].fillna(0, inplace=True)
    df['order_count'].fillna(0, inplace=True)
    df['days_since_last_order'].fillna(df['days_since_last_order'].max(), inplace=True)
    
    # Calculate customer tenure in days
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['last_login'] = pd.to_datetime(df['last_login'])
    df['tenure_days'] = (datetime.now() - df['signup_date']).dt.days
    
    # Create binary features
    df['is_active'] = (datetime.now() - df['last_login']).dt.days <= 30
    df['is_high_value'] = df['total_spent'] > df['total_spent'].median()
    
    # Create categorical features
    df['age_group'] = pd.cut(
        df['age'], 
        bins=[0, 25, 35, 45, 55, 65, 100],
        labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    )
    
    # Log transform skewed features
    df['income_log'] = np.log1p(df['income'])
    df['total_spent_log'] = np.log1p(df['total_spent'])
    
    logger.info("Data cleaning and preprocessing completed")
    return df

def feature_engineering(df):
    """
    Create new features from existing data
    
    Args:
        df (DataFrame): Preprocessed data
        
    Returns:
        DataFrame: Data with engineered features
    """
    logger.info("Performing feature engineering")
    
    # Calculate spending frequency (orders per month)
    df['months_active'] = df['tenure_days'] / 30.44  # Average days in a month
    df['orders_per_month'] = df['order_count'] / df['months_active']
    
    # Calculate average spending per month
    df['spending_per_month'] = df['total_spent'] / df['months_active']
    
    # Create RFM scores
    # Recency score (lower days_since_last_order is better)
    df['recency_score'] = 5 - pd.qcut(
        df['days_since_last_order'], 
        q=5, 
        labels=False, 
        duplicates='drop'
    )
    
    # Frequency score (higher orders_per_month is better)
    df['frequency_score'] = 1 + pd.qcut(
        df['orders_per_month'].clip(lower=0), 
        q=5, 
        labels=False, 
        duplicates='drop'
    )
    
    # Monetary score (higher spending_per_month is better)
    df['monetary_score'] = 1 + pd.qcut(
        df['spending_per_month'].clip(lower=0), 
        q=5, 
        labels=False, 
        duplicates='drop'
    )
    
    # Combined RFM score
    df['rfm_score'] = df['recency_score'] + df['frequency_score'] + df['monetary_score']
    
    # Create customer segments
    df['customer_segment'] = pd.qcut(
        df['rfm_score'], 
        q=4, 
        labels=['Low Value', 'Medium Value', 'High Value', 'Top Value']
    )
    
    logger.info("Feature engineering completed")
    return df

def build_predictive_model(df):
    """
    Build a machine learning model to predict high-value customers
    
    Args:
        df (DataFrame): Data with engineered features
        
    Returns:
        tuple: (model, feature_importance)
    """
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import accuracy_score, classification_report
        
        logger.info("Building predictive model")
        
        # Select features and target
        features = ['age', 'income', 'tenure_days', 'order_count', 
                   'total_spent', 'avg_order_value', 'days_since_last_order']
        X = df[features]
        y = df['is_high_value']  # Binary target: high value customer or not
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Create a pipeline with preprocessing and model
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Make predictions
        y_pred = pipeline.predict(X_test)
        
        # Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model Accuracy: {accuracy:.2f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': features,
            'Importance': pipeline.named_steps['classifier'].feature_importances_
        }).sort_values('Importance', ascending=False)
        
        return pipeline, feature_importance
    
    except ImportError:
        logger.warning("Scikit-learn not available. Skipping model building.")
        return None, None

if __name__ == "__main__":
    # Example usage
    db_path = "customer_orders.db"
    create_sample_database(db_path)
    df = extract_data_from_db(db_path)
    df = data_cleaning_and_preprocessing(df)
    df = feature_engineering(df)
    model, importance = build_predictive_model(df) 