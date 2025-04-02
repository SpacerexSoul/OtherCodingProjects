# H2 Database Tutorial

H2 is a lightweight, open-source Java SQL database that can run in embedded mode or server mode.

## Prerequisites

- Java JDK installed (version 8 or higher)
- Python 3.6 or higher
- JayDeBeApi Python package (`pip install jaydebeapi`)

## Contents

This directory contains the following files:

- `h2_setup.py` - Instructions and code for setting up H2 database
- `h2_operations.py` - Example of CRUD operations with H2 database

## Getting Started

1. Download H2 database from the official website (https://h2database.com/html/main.html)
2. Start H2 database console: `java -jar h2*.jar`
3. Run the sample scripts in this directory

## Key Concepts

- **Connection**: Using JayDeBeApi as a bridge to connect to JDBC databases
- **CRUD Operations**: Basic Create, Read, Update, Delete operations
- **Performance Tips**: Creating indexes and optimizing H2 database

## Further Reading

- [H2 Database Documentation](https://h2database.com/html/main.html)
- [JayDeBeApi Documentation](https://pypi.org/project/JayDeBeApi/) 