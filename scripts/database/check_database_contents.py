#!/usr/bin/env python3
"""
Simple database content checker using direct SQLite connection
"""

import sqlite3
from pathlib import Path

def check_database():
    """Check database contents directly"""
    
    # Database path
    db_path = Path("golf_database.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"✅ Database found: {db_path}")
    print("🔍 CHECKING DATABASE CONTENTS")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        print("\n📋 TABLES IN DATABASE:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_names = [table[0] for table in tables]
        for table in table_names:
            print(f"   • {table}")
        
        print(f"\n📊 RECORD COUNTS:")
        for table_name in table_names:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                print(f"   {table_name}: {count:,} records")
            except Exception as e:
                print(f"   {table_name}: Error - {e}")
        
        # Check specific tables we care about
        important_tables = ['tournaments_enhanced', 'tournament_results', 'courses_enhanced']
        
        for table in important_tables:
            if table in table_names:
                print(f"\n🔍 {table.upper()} SAMPLE DATA:")
                
                # Get column info
                cursor.execute(f'PRAGMA table_info("{table}")')
                columns = [col[1] for col in cursor.fetchall()]
                print(f"   Columns: {columns}")
                
                # Get sample data
                cursor.execute(f'SELECT * FROM "{table}" LIMIT 3')
                rows = cursor.fetchall()
                
                if rows:
                    for i, row in enumerate(rows, 1):
                        print(f"   Sample {i}:")
                        for col, val in zip(columns, row):
                            print(f"     {col}: {val}")
                        print()
                else:
                    print("   ⚠️ No data in this table")
        
        # Check relationships
        print(f"\n🔗 CHECKING RELATIONSHIPS:")
        
        # Check tournaments with courses
        print(f"\n   Tournaments with courses:")
        cursor.execute("""
            SELECT 
                t.tournament_name, 
                c.course_name,
                t.tournament_date,
                t.course_id
            FROM tournaments_enhanced t
            LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"   - {row[0]} at {row[1]} (course_id: {row[3]}) on {row[2]}")
        else:
            print("   ⚠️ No tournament-course relationships found")
        
        # Check tournament results with players
        print(f"\n   Tournament results with players:")
        cursor.execute("""
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
        
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"   - {row[0]} in {row[1]}: Position {row[2]}, Strokes {row[3]}")
        else:
            print("   ⚠️ No tournament result relationships found")
            
            # Let's check what's actually in tournament_results
            print(f"\n   Raw tournament_results data:")
            cursor.execute("SELECT * FROM tournament_results LIMIT 3")
            results = cursor.fetchall()
            cursor.execute("PRAGMA table_info(tournament_results)")
            tr_columns = [col[1] for col in cursor.fetchall()]
            
            if results:
                for result in results:
                    print(f"   Raw result: {dict(zip(tr_columns, result))}")
            else:
                print("   ⚠️ tournament_results table is empty")
    
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()