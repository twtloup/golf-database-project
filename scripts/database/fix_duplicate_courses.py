#!/usr/bin/env python3
"""
Fix duplicate course records in the database
"""

import sqlite3
from pathlib import Path

def analyze_course_duplicates():
    """Analyze and fix course duplicates"""
    
    db_path = Path("golf_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 ANALYZING COURSE DUPLICATES")
    print("=" * 50)
    
    # Find duplicate courses
    print("\n📊 COURSE DUPLICATES:")
    cursor.execute("""
        SELECT course_name, location, COUNT(*) as duplicate_count, 
               GROUP_CONCAT(course_id) as course_ids
        FROM courses_enhanced 
        GROUP BY course_name, location 
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC
    """)
    
    duplicates = cursor.fetchall()
    total_duplicates = 0
    
    for row in duplicates:
        course_name, location, count, course_ids = row
        total_duplicates += count - 1  # All but one are duplicates
        print(f"   • {course_name} ({location}): {count} copies - IDs: {course_ids}")
    
    print(f"\n📈 SUMMARY:")
    print(f"   • Unique courses with duplicates: {len(duplicates)}")
    print(f"   • Total duplicate records: {total_duplicates}")
    
    # Show tournament relationships that would be affected
    print(f"\n🏆 TOURNAMENTS AFFECTED BY DUPLICATES:")
    cursor.execute("""
        SELECT t.tournament_name, t.course_id, c.course_name, c.location
        FROM tournaments_enhanced t
        JOIN courses_enhanced c ON t.course_id = c.course_id
        WHERE c.course_name IN (
            SELECT course_name 
            FROM courses_enhanced 
            GROUP BY course_name, location 
            HAVING COUNT(*) > 1
        )
        ORDER BY c.course_name, t.tournament_date
    """)
    
    affected_tournaments = cursor.fetchall()
    for tournament_name, course_id, course_name, location in affected_tournaments[:10]:  # Show first 10
        print(f"   • {tournament_name} → Course ID {course_id} ({course_name})")
    
    if len(affected_tournaments) > 10:
        print(f"   ... and {len(affected_tournaments) - 10} more tournaments")
    
    conn.close()
    return duplicates

def fix_course_duplicates():
    """Fix course duplicates by merging them"""
    
    db_path = Path("golf_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔧 FIXING COURSE DUPLICATES")
    print("=" * 50)
    
    try:
        # Get all duplicate course groups
        cursor.execute("""
            SELECT course_name, location, MIN(course_id) as keep_id, 
                   GROUP_CONCAT(course_id) as all_ids
            FROM courses_enhanced 
            GROUP BY course_name, location 
            HAVING COUNT(*) > 1
        """)
        
        duplicate_groups = cursor.fetchall()
        fixed_count = 0
        
        for course_name, location, keep_id, all_ids in duplicate_groups:
            # Convert comma-separated IDs to list
            all_id_list = [int(id.strip()) for id in all_ids.split(',')]
            duplicate_ids = [id for id in all_id_list if id != keep_id]
            
            print(f"\n   Fixing: {course_name} ({location})")
            print(f"   Keeping course_id: {keep_id}")
            print(f"   Removing course_ids: {duplicate_ids}")
            
            # Update all tournaments pointing to duplicate course IDs
            for duplicate_id in duplicate_ids:
                cursor.execute("""
                    UPDATE tournaments_enhanced 
                    SET course_id = ? 
                    WHERE course_id = ?
                """, (keep_id, duplicate_id))
                
                updated_tournaments = cursor.rowcount
                print(f"     → Updated {updated_tournaments} tournaments from course_id {duplicate_id} to {keep_id}")
            
            # Delete duplicate course records
            cursor.execute("""
                DELETE FROM courses_enhanced 
                WHERE course_id IN ({})
            """.format(','.join(map(str, duplicate_ids))))
            
            deleted_courses = cursor.rowcount
            print(f"     → Deleted {deleted_courses} duplicate course records")
            fixed_count += deleted_courses
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ DUPLICATE FIXING COMPLETE!")
        print(f"   • Fixed {len(duplicate_groups)} course groups")
        print(f"   • Removed {fixed_count} duplicate course records")
        
        # Verify results
        cursor.execute("SELECT COUNT(*) FROM courses_enhanced")
        total_courses = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM courses_enhanced 
            GROUP BY course_name, location 
            HAVING COUNT(*) > 1
        """)
        remaining_duplicates = len(cursor.fetchall())
        
        print(f"   • Total courses remaining: {total_courses}")
        print(f"   • Remaining duplicates: {remaining_duplicates}")
        
    except Exception as e:
        print(f"❌ Error fixing duplicates: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def verify_fix():
    """Verify the fix worked"""
    
    db_path = Path("golf_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🔍 VERIFICATION")
    print("=" * 30)
    
    # Check Memorial courses specifically
    cursor.execute("""
        SELECT course_id, course_name, location 
        FROM courses_enhanced 
        WHERE course_name LIKE '%Memorial%'
        ORDER BY course_name
    """)
    
    memorial_courses = cursor.fetchall()
    print(f"\nMemorial courses after fix:")
    for course_id, course_name, location in memorial_courses:
        print(f"   • ID {course_id}: {course_name} ({location})")
    
    # Check tournament relationships
    cursor.execute("""
        SELECT COUNT(DISTINCT t.tournament_id) 
        FROM tournaments_enhanced t
        JOIN courses_enhanced c ON t.course_id = c.course_id
        WHERE c.course_name LIKE '%Memorial%'
    """)
    
    memorial_tournaments = cursor.fetchone()[0]
    print(f"\nTournaments at Memorial courses: {memorial_tournaments}")
    
    conn.close()

if __name__ == "__main__":
    # Step 1: Analyze the problem
    duplicates = analyze_course_duplicates()
    
    if duplicates:
        # Step 2: Ask for confirmation
        print(f"\n⚠️  Found course duplicates that need fixing.")
        response = input("Do you want to fix these duplicates? (y/n): ").lower().strip()
        
        if response == 'y':
            # Step 3: Fix the duplicates
            fix_course_duplicates()
            
            # Step 4: Verify the fix
            verify_fix()
            
            print(f"\n🎉 Course duplicates fixed!")
            print(f"Now test your API again: http://localhost:5000/api/search?q=Memorial")
        else:
            print("Fix cancelled.")
    else:
        print("✅ No course duplicates found!")