#!/usr/bin/env python3
"""
Database initialization script for Deep-Shiva project.
This script creates tables and optionally seeds data.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.database import engine, SessionLocal
from app.models import Base

def create_tables():
    """Create all database tables using SQLAlchemy models."""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def run_sql_file(filename):
    """Execute SQL commands from a file."""
    print(f"Executing {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        db = SessionLocal()
        try:
            for statement in statements:
                if statement:
                    db.execute(text(statement))
            db.commit()
            print(f"✓ {filename} executed successfully!")
            return True
        except Exception as e:
            db.rollback()
            print(f"✗ Error executing {filename}: {e}")
            return False
        finally:
            db.close()
            
    except FileNotFoundError:
        print(f"✗ File {filename} not found!")
        return False
    except Exception as e:
        print(f"✗ Error reading {filename}: {e}")
        return False

def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Database connection successful!")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Main initialization function."""
    load_dotenv()
    
    print("=== Deep-Shiva Database Initialization ===\n")
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("✗ DATABASE_URL environment variable not set!")
        print("Please check your .env file.")
        sys.exit(1)
    
    print(f"Database URL: {os.getenv('DATABASE_URL')[:50]}...")
    
    # Test connection
    if not test_connection():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    # Ask user if they want to seed data
    seed_data = input("\nDo you want to seed the database with sample data? (y/N): ").lower().strip()
    
    if seed_data in ['y', 'yes']:
        if run_sql_file('seed_data.sql'):
            print("\n✓ Database initialized and seeded successfully!")
        else:
            print("\n✗ Database initialized but seeding failed!")
            sys.exit(1)
    else:
        print("\n✓ Database initialized successfully (no seed data)!")
    
    print("\nYou can now start the FastAPI server with: python run.py")

if __name__ == "__main__":
    main()