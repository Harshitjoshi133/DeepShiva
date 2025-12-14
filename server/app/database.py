import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError, OperationalError
from dotenv import load_dotenv
import logging
import time

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with robust connection handling
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections every hour
    pool_timeout=30,     # Timeout for getting connection from pool
    # Connection arguments
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        "application_name": "deep_shiva_chat"
    },
    # Echo SQL queries in debug mode
    echo=False
)

# Add connection event listeners for better error handling
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection parameters on connect"""
    logger.info("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Handle connection checkout from pool"""
    logger.debug("Connection checked out from pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Handle connection checkin to pool"""
    logger.debug("Connection checked in to pool")

@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    """Handle connection invalidation"""
    logger.warning(f"Connection invalidated: {exception}")

# Create SessionLocal class with retry logic
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session with retry logic
def get_db():
    """
    Database session dependency with automatic retry on connection failures.
    Implements exponential backoff for connection retries.
    """
    max_retries = 3
    retry_delay = 1  # Start with 1 second delay
    
    for attempt in range(max_retries):
        db = None
        try:
            db = SessionLocal()
            # Test the connection
            db.execute(text("SELECT 1"))
            yield db
            return
            
        except (DisconnectionError, OperationalError) as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            
            if db:
                try:
                    db.close()
                except Exception:
                    pass
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying database connection in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                raise
                
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            if db:
                try:
                    db.close()
                except Exception:
                    pass
            raise
            
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.warning(f"Error closing database session: {str(e)}")

def get_db_with_retry():
    """
    Alternative database session getter with explicit retry logic.
    Use this for critical operations that need guaranteed database access.
    """
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test connection
            db.execute(text("SELECT 1"))
            return db
            
        except (DisconnectionError, OperationalError) as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)  # Cap at 30 seconds
            else:
                logger.error("Failed to establish database connection after all retries")
                raise
                
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            raise

def test_database_connection():
    """
    Test database connectivity and return status.
    """
    try:
        db = get_db_with_retry()
        result = db.execute(text("SELECT version()")).fetchone()
        db.close()
        return {
            "status": "connected",
            "version": result[0] if result else "unknown",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": time.time()
        }