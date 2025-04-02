#!/usr/bin/env python3
"""
H2 Database Setup Script

This script demonstrates how to download, set up, and connect to an H2 database
using Python and JayDeBeApi (a bridge to JDBC for Python).

Author: AI Assistant
License: MIT
"""

import os
import subprocess
import sys
import jaydebeapi
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_h2():
    """
    Download the H2 database JAR file if not already present
    """
    h2_version = "2.2.224"
    h2_jar_filename = f"h2-{h2_version}.jar"
    h2_url = f"https://repo1.maven.org/maven2/com/h2database/h2/{h2_version}/{h2_jar_filename}"
    
    # Create a directory for the H2 JAR file
    os.makedirs("lib", exist_ok=True)
    
    if not os.path.exists(f"lib/{h2_jar_filename}"):
        logger.info(f"Downloading H2 database version {h2_version}...")
        try:
            # Use curl to download the file
            subprocess.run(["curl", "-L", h2_url, "-o", f"lib/{h2_jar_filename}"], check=True)
            logger.info(f"Successfully downloaded H2 database to lib/{h2_jar_filename}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download H2 database: {e}")
            sys.exit(1)
    else:
        logger.info(f"H2 database JAR already exists at lib/{h2_jar_filename}")
    
    return f"lib/{h2_jar_filename}"

def start_h2_server(jar_path):
    """
    Start the H2 database server
    
    Args:
        jar_path (str): Path to the H2 JAR file
    """
    logger.info("Starting H2 database server...")
    try:
        # Start H2 in server mode
        subprocess.Popen([
            "java", "-cp", jar_path, "org.h2.tools.Server",
            "-tcp", "-web", "-ifNotExists"
        ])
        logger.info("H2 server started successfully")
        logger.info("Web console available at http://localhost:8082")
    except Exception as e:
        logger.error(f"Failed to start H2 server: {e}")
        sys.exit(1)

def connect_to_h2(jar_path):
    """
    Connect to H2 database using JayDeBeApi
    
    Args:
        jar_path (str): Path to the H2 JAR file
        
    Returns:
        connection: JayDeBeApi connection object
    """
    try:
        # Connection parameters
        jdbc_driver = "org.h2.Driver"
        jdbc_url = "jdbc:h2:~/test"  # Creates an embedded DB in user's home directory
        user = "sa"  # Default username
        password = ""  # Default empty password
        
        # Connect to the database
        connection = jaydebeapi.connect(
            jdbc_driver,
            jdbc_url,
            [user, password],
            jar_path
        )
        
        logger.info("Successfully connected to H2 database")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to H2 database: {e}")
        sys.exit(1)

def main():
    """
    Main function to demonstrate H2 database setup
    """
    logger.info("H2 Database Setup Script")
    
    # Download H2 if needed
    jar_path = download_h2()
    
    # Start H2 server
    start_h2_server(jar_path)
    
    # Connect to H2
    connection = connect_to_h2(jar_path)
    
    # Test the connection
    cursor = connection.cursor()
    cursor.execute("SELECT 'Hello, H2 Database!' AS greeting")
    result = cursor.fetchone()
    logger.info(f"Test query result: {result[0]}")
    
    # Clean up
    cursor.close()
    connection.close()
    
    logger.info("H2 database setup and test completed successfully")
    logger.info("The H2 server is still running in the background.")
    logger.info("Access the web console at http://localhost:8082")
    logger.info("Use JDBC URL 'jdbc:h2:~/test' to connect to your database")

if __name__ == "__main__":
    main() 