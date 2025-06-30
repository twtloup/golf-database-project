"""
Database connection and utility functions
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            # Fallback to SQLite for development
            self.database_url = 'sqlite:///golf_database.db'
            print("⚠️  Using SQLite fallback. Set DATABASE_URL for PostgreSQL.")
ECHO is off.
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
ECHO is off.
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created")
ECHO is off.
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

# Global database manager instance
db_manager = DatabaseManager()
