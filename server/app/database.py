import os
import asyncio
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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

# Create async database URL (convert postgresql:// to postgresql+asyncpg://)
# Remove query parameters that are not compatible with asyncpg
import urllib.parse

def create_async_database_url(sync_url):
    """Convert sync PostgreSQL URL to async URL compatible with asyncpg"""
    # Parse the URL
    parsed = urllib.parse.urlparse(sync_url)
    
    # Remove query parameters that asyncpg doesn't support
    # asyncpg handles SSL automatically for most cloud providers
    query_params = urllib.parse.parse_qs(parsed.query)
    
    # Keep only compatible parameters
    compatible_params = {}
    
    # Reconstruct URL without problematic parameters
    new_query = urllib.parse.urlencode(compatible_params, doseq=True)
    
    # Build new URL with asyncpg driver
    new_parsed = parsed._replace(
        scheme="postgresql+asyncpg",
        query=new_query
    )
    
    return urllib.parse.urlunparse(new_parsed)

ASYNC_DATABASE_URL = create_async_database_url(DATABASE_URL)

# Log the URLs for debugging (without credentials)
def safe_url_for_logging(url):
    """Create a safe version of URL for logging (hide credentials)"""
    parsed = urllib.parse.urlparse(url)
    safe_netloc = f"***:***@{parsed.hostname}:{parsed.port}" if parsed.port else f"***:***@{parsed.hostname}"
    safe_parsed = parsed._replace(netloc=safe_netloc)
    return urllib.parse.urlunparse(safe_parsed)

logger.info(f"Sync Database URL: {safe_url_for_logging(DATABASE_URL)}")
logger.info(f"Async Database URL: {safe_url_for_logging(ASYNC_DATABASE_URL)}")

# Create SQLAlchemy engine with robust connection handling (sync version for compatibility)
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
        "application_name": "deep_shiva_chat"
    },
    # Echo SQL queries in debug mode
    echo=False
)

# Create async SQLAlchemy engine for better performance
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    # Optimized connection pool settings for cloud databases
    pool_size=3,            # Smaller pool for cloud providers (Neon has connection limits)
    max_overflow=7,         # Conservative overflow for concurrent requests
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=900,       # Recycle connections every 15 minutes (cloud-friendly)
    pool_timeout=20,        # Shorter timeout for getting connection from pool
    # Echo SQL queries in debug mode
    echo=False,
    # Async-specific settings
    future=True,
    # Connection arguments optimized for asyncpg and cloud providers
    connect_args={
        "server_settings": {
            "application_name": "deep_shiva_chat_async"
        },
        # Optimized timeouts for cloud databases
        "command_timeout": 30
    }
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

# Create SessionLocal class with retry logic (sync version)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async session maker for better performance
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

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

# Async database session dependency
async def get_async_db():
    """
    Async database session dependency with automatic retry on connection failures.
    Provides better performance for concurrent requests with fallback to sync if needed.
    """
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        async_session = None
        try:
            async_session = AsyncSessionLocal()
            # Test the connection with a simple query
            await async_session.execute(text("SELECT 1"))
            
            logger.debug(f"Async database session created successfully (attempt {attempt + 1})")
            yield async_session
            return
            
        except (DisconnectionError, OperationalError) as e:
            logger.warning(f"Async database connection attempt {attempt + 1} failed: {str(e)}")
            
            if async_session:
                try:
                    await async_session.close()
                except Exception:
                    pass
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying async database connection in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("All async database connection attempts failed, check connection parameters")
                # Provide more specific error information
                error_msg = f"Failed to connect to async database after {max_retries} attempts. "
                error_msg += f"Last error: {str(e)}. "
                error_msg += "Check DATABASE_URL format and asyncpg compatibility."
                raise ConnectionError(error_msg)
                
        except Exception as e:
            logger.error(f"Unexpected async database error: {str(e)}")
            if async_session:
                try:
                    await async_session.close()
                except Exception:
                    pass
            
            # Provide more context for debugging
            error_msg = f"Async database error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise
            
        finally:
            if async_session:
                try:
                    await async_session.close()
                except Exception as e:
                    logger.warning(f"Error closing async database session: {str(e)}")

async def get_async_db_with_retry():
    """
    Alternative async database session getter with explicit retry logic.
    Use this for critical operations that need guaranteed database access.
    """
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            async_session = AsyncSessionLocal()
            # Test connection
            await async_session.execute(text("SELECT 1"))
            logger.debug(f"Async database connection established (attempt {attempt + 1})")
            return async_session
            
        except (DisconnectionError, OperationalError) as e:
            logger.warning(f"Async database connection attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)
            else:
                logger.error("Failed to establish async database connection after all retries")
                raise
                
        except Exception as e:
            logger.error(f"Unexpected async database error: {str(e)}")
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

async def test_async_database_connection():
    """
    Test async database connectivity and return status with performance metrics.
    """
    start_time = time.time()
    try:
        async_session = await get_async_db_with_retry()
        
        # Test query performance
        query_start = time.time()
        result = await async_session.execute(text("SELECT version()"))
        version_row = result.fetchone()
        query_time = (time.time() - query_start) * 1000
        
        await async_session.close()
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            "status": "connected",
            "version": version_row[0] if version_row else "unknown",
            "connection_time_ms": round(total_time, 2),
            "query_time_ms": round(query_time, 2),
            "performance_rating": "excellent" if total_time < 100 else "good" if total_time < 500 else "slow",
            "timestamp": time.time()
        }
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        return {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "connection_time_ms": round(total_time, 2),
            "timestamp": time.time()
        }