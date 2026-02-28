from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This creates a local file named 'contacts.db'
DATABASE_URL = "sqlite:///./contacts.db"

engine = create_engine(
    DATABASE_URL, 
    # check_same_thread is only needed for SQLite
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()