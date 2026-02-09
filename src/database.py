"""
Database connection and session management
"""

from models import Base
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from aws_lambda_powertools import Logger
from config import config

logger = Logger(child=True)

# Pool connection settings for better performance in Lambda environment
# Reaproveita conexões anteriores para reduzir latência
engine = create_engine(
    config.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL debugging
    connect_args={"options": "-c client_encoding=utf8"},  # Ensure UTF-8 encoding
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Session:
    """
    Para usar:
        with get_db() as db:
            user = db.query(Usuario).first()
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
        db.commit()
        logger.debug("Database session committed")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def init_db():
    """Initialize database (create tables)"""

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
