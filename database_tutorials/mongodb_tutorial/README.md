# MongoDB Production Example

This directory contains production-ready implementation of database operations using MongoDB and PyMongo.

## Project Structure

- `product_catalog.py` - Implementation of a product catalog system with MongoDB

## Requirements

- MongoDB 4.4+
- Python 3.8+
- PyMongo 4.0+

## Configuration

The code uses the following environment variables:

- `MONGO_URI` - MongoDB connection string (defaults to localhost)
- `MONGO_DB` - MongoDB database name (defaults to 'product_catalog')

## Features

- Document-based schema design
- Indexing for performance
- Transaction support
- Error handling and logging
- Production-ready code structure 