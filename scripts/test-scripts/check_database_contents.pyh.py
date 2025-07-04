#!/usr/bin/env python3
"""
Check what's actually in our database tables
"""

import sys
from pathlib import Path

# Add the src directory to Python path - fix for proper path resolution
project_root = Path(__file__).parent
src_path = project_root / 'src'

# Try multiple path configurations
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

print(f"🔍 Project root: {project_root}")
print(f"🔍 Src path: {src_path}")
print(f"🔍 Src path exists: {src_path.exists()}")

try:
    from models.database import db_manager
    print("✅ Database connection successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # Try alternative import approach
    try:
        import os
        os.chdir(project_root)
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        from models.database import db_manager
        print("✅ Database connection successful (alternative path)")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        print("Please run this script from the project root directory")
        sys.exit(1)

def check_table_contents():
    """Check contents of all tables"""
    print("🔍 CHECKING DATABASE CONTENTS")
    print("=" * 50)
    
    session = db_manager.get_session()
    
    try:
        from sqlalchemy import text
        
        # Check each table
        tables_to_check = [
            'players',
            'courses_enhanced', 
            'tournaments_enhanced',
            'tournament_results',
            'player_yearly_stats'
        ]
        
        for table in tables_to_check:
            try:
                # Get count
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                count = session.execute(count_query).scalar()
                
                print(f"\n📋 {table.upper()}: {count:,} records")
                
                # Get sample data
                if count > 0:
                    sample_query = text(f"SELECT * FROM {table} LIMIT 3")
                    result = session.execute(sample_query)
                    
                    # Get column names
                    columns = result.keys()
                    print(f"   Columns: {list(columns)}")
                    
                    # Show sample data
                    rows = result.fetchall()
                    for i, row in enumerate(rows, 1):
                        print(f"   Sample {i}: {dict(row._mapping)}")
                        
                else:
                    print("   ⚠️ No data in this table")
                    
            except Exception as e:
                print(f"   ❌ Error checking {table}: {e}")
        
        # Check specific tournament relationships
        print(f"\n🔗 CHECKING RELATIONSHIPS:")
        
        # Check if tournaments have courses
        tournament_course_query = text("""
            SELECT 
                t.tournament_name, 
                c.course_name,
                t.tournament_date,
                t.course_id
            FROM tournaments_enhanced t
            LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
            LIMIT 5
        """)
        
        print(f"\n   Tournament-Course relationships:")
        result = session.execute(tournament_course_query)
        for row in result:
            print(f"   - {row[0]} at {row[1]} (course_id: {row[3]}) on {row[2]}")
        
        # Check if tournament results have players and tournaments
        result_relationships_query = text("""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                t.tournament_name,
                tr.final_position,
                tr.total_strokes
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
            LIMIT 5
        """)
        
        print(f"\n   Tournament Result relationships:")
        result = session.execute(result_relationships_query)
        for row in result:
            print(f"   - {row[0]} in {row[1]}: Position {row[2]}, Strokes {row[3]}")
            
    except Exception as e:
        print(f"❌ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()

if __name__ == "__main__":
    check_table_contents()