import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Get database URL from environment, fallback to SQLite
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///golf_database.db')
        
        # Create engine
        if 'sqlite' in self.database_url:
            # SQLite specific settings
            self.engine = create_engine(
                self.database_url, 
                echo=False,  # Set to True for SQL debugging
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL or other database
            self.engine = create_engine(self.database_url, echo=False)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        from .models import Base
        Base.metadata.drop_all(bind=self.engine)

# Global database manager instance
db_manager = DatabaseManager()