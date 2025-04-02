# PostgreSQL Inventory Management System

This directory contains a production-grade implementation of an inventory management system using PostgreSQL and Python.

## Project Structure

- `inventory_system.py` - Implementation of an inventory management system with PostgreSQL

## Requirements

- PostgreSQL 12+
- Python 3.8+
- psycopg2-binary 2.9+

## Configuration

The system requires the following environment variables:

- `POSTGRES_HOST` - PostgreSQL server hostname (defaults to localhost)
- `POSTGRES_PORT` - PostgreSQL server port (defaults to 5432)
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password

## Features

- Complete inventory tracking system with products, stock levels, warehouses, and transactions
- Transaction management and atomicity
- Advanced PostgreSQL features like stored procedures, triggers, and complex queries
- Connection pooling for performance
- Comprehensive error handling 