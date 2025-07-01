#!/usr/bin/env python3
"""
Golf Database SQLite Setup Script
Run this to initialize your SQLite database and verify everything works
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path so we can import our modules
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

try:
    from models.database import DatabaseManager, db_manager
    from models.models import Base, Player, Course, Tournament, TournamentEntry, Round
    print("✅ Successfully imported database modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def setup_database():
    """Initialize SQLite database and create all tables"""
    print("🏌️ Golf Database SQLite Setup")
    print("=" * 40)
    
    # Check if we're using SQLite (should be automatic fallback)
    print(f"📍 Database URL: {db_manager.database_url}")
    
    if 'sqlite' not in db_manager.database_url:
        print("⚠️  Warning: Not using SQLite. Make sure your .env file doesn't have DATABASE_URL set,")
        print("   or set it to: sqlite:///golf_database.db")
    
    try:
        # Create all tables
        print("\n📊 Creating database tables...")
        db_manager.create_tables()
        
        # Test the connection by creating a session
        print("🔗 Testing database connection...")
        session = db_manager.get_session()
        
        # Verify tables were created by checking if we can query them
        player_count = session.query(Player).count()
        course_count = session.query(Course).count()
        tournament_count = session.query(Tournament).count()
        
        print(f"✅ Database connection successful!")
        print(f"📊 Tables created:")
        print(f"   - Players: {player_count} records")
        print(f"   - Courses: {course_count} records") 
        print(f"   - Tournaments: {tournament_count} records")
        
        session.close()
        
        # Show database file location
        if 'sqlite' in db_manager.database_url:
            db_file = db_manager.database_url.replace('sqlite:///', '')
            if not db_file.startswith('/'):
                db_file = project_root / db_file
            print(f"🗃️  SQLite database file: {db_file}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def add_sample_data():
    """Add some sample data to test the database"""
    print("\n📝 Adding sample data...")
    
    try:
        session = db_manager.get_session()
        
        # Add a sample course
        sample_course = Course(
            course_name="Augusta National Golf Club",
            location="Augusta, Georgia",
            country="USA",
            par=72,
            yardage=7475,
            course_rating=76.2,
            slope_rating=137,
            architect="Alister MacKenzie, Bobby Jones",
            established_year=1933,
            greens_type="Bentgrass"
        )
        session.add(sample_course)
        session.commit()
        
        # Add a sample tournament
        from datetime import date
        sample_tournament = Tournament(
            tournament_name="Masters Tournament",
            course_id=sample_course.course_id,
            start_date=date(2024, 4, 11),
            end_date=date(2024, 4, 14),
            prize_money_usd=18000000,
            field_size=88,
            cut_line=50,
            winning_score=-11
        )
        session.add(sample_tournament)
        session.commit()
        
        # Add a sample player
        sample_player = Player(
            first_name="Tiger",
            last_name="Woods",
            nationality="USA",
            birth_date=date(1975, 12, 30),
            turned_professional_date=date(1996, 8, 27),
            height_cm=185,
            world_ranking=1,
            career_earnings=120000000.00
        )
        session.add(sample_player)
        session.commit()
        
        print("✅ Sample data added successfully!")
        print(f"   - Course: {sample_course.course_name}")
        print(f"   - Tournament: {sample_tournament.tournament_name}")
        print(f"   - Player: {sample_player.full_name}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")
        session.rollback()
        session.close()
        return False

def verify_installation():
    """Verify all required packages are installed"""
    print("🔍 Verifying installation...")
    
    # Map package names to their import names
    package_imports = {
        'sqlalchemy': 'sqlalchemy',
        'flask': 'flask',
        'pandas': 'pandas',
        'python-dotenv': 'dotenv'  # This is the key fix!
    }
    
    missing_packages = []
    
    for package, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages installed")
    return True

def main():
    """Main setup function"""
    print("🏌️ Golf Database Setup")
    print("=" * 50)
    
    # Step 1: Verify installation
    if not verify_installation():
        return False
    
    # Step 2: Setup database
    if not setup_database():
        return False
    
    # Step 3: Add sample data
    add_sample_data()
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Run your Flask API: python src/api/app.py")
    print("2. Visit http://localhost:5000 to test")
    print("3. Load your Kaggle golf data")
    
    return True

if __name__ == "__main__":
    main()