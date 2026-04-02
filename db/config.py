from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

# Get database configuration from environment variables
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")  # Default to 5432 if not set
DB_NAME = os.getenv("POSTGRES_DB")

# Only create engine if all required database variables are present
# This allows tests to run without a real database connection
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # For test environments without DB config, use in-memory SQLite
    # This prevents import errors but won't be used since tests use FakeSession
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)