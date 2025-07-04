#!/usr/bin/env python3
"""
Check what's actually in the database
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from models.database import db_manager
from models.models import Player, Course, Tournament

def check_database():
    """Check what data is in the database"""
    print("🔍 Checking database contents...")
    print(f"📍 Database URL: {db_manager.database_url}")
    
    session = db_manager.get_session()
    
    try:
        # Count records
        player_count = session.query(Player).count()
        course_count = session.query(Course).count()
        tournament_count = session.query(Tournament).count()
        
        print(f"📊 Record counts:")
        print(f"   - Players: {player_count}")
        print(f"   - Courses: {course_count}")
        print(f"   - Tournaments: {tournament_count}")
        
        # Show actual data
        if player_count > 0:
            print(f"\n👥 Players in database:")
            players = session.query(Player).all()
            for player in players:
                print(f"   - {player.full_name} ({player.nationality})")
        else:
            print("\n❌ No players found in database")
            
        if course_count > 0:
            print(f"\n🏌️ Courses in database:")
            courses = session.query(Course).all()
            for course in courses:
                print(f"   - {course.course_name} ({course.location})")
        else:
            print("\n❌ No courses found in database")
            
        if tournament_count > 0:
            print(f"\n🏆 Tournaments in database:")
            tournaments = session.query(Tournament).all()
            for tournament in tournaments:
                print(f"   - {tournament.tournament_name} ({tournament.start_date})")
        else:
            print("\n❌ No tournaments found in database")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_database()