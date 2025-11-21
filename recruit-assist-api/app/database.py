"""
Database configuration and session management.

Uses SQLAlchemy ORM with PostgreSQL.
"""

from __future__ import annotations
import logging
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
logger = logging.getLogger(__name__)

# Database URL - will be set from settings at runtime
def get_database_url() -> str:
    """Get database URL from settings."""
    from app.settings import settings
    return settings.database_url


def get_debug_mode() -> bool:
    """Get debug mode from settings."""
    from app.settings import settings
    return settings.debug


# Create engine with connection pooling (lazy initialization)
engine = None


def get_engine():
    """Get or create database engine."""
    global engine
    if engine is None:
        db_url = get_database_url()
        
        # SQLite-specific configuration
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            # Don't use connection pooling for SQLite
            engine = create_engine(
                db_url,
                connect_args=connect_args,
                echo=get_debug_mode(),
            )
        else:
            # PostgreSQL configuration
            engine = create_engine(
                db_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=10,  # Connection pool size
                max_overflow=20,  # Max overflow connections
                echo=get_debug_mode(),  # Log SQL queries in debug mode
            )
    return engine


# Session factory (configured at runtime)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    # Initialize engine if needed
    eng = get_engine()
    SessionLocal.configure(bind=eng)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables."""
    logger.info("Initializing database...")
    eng = get_engine()
    Base.metadata.create_all(bind=eng)
    logger.info("Database initialized successfully")


def check_db_connection() -> bool:
    """Check if database connection is working."""
    try:
        eng = get_engine()
        with eng.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

