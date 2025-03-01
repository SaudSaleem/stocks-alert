from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

SQLALCHEMY_DATABASE_URL = "sqlite:///./stocks_alert.db"

# Adding timeout and pooling configurations for better concurrency handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # Increase SQLite timeout to 30 seconds
    },
    # Configure connection pooling
    pool_size=5,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 