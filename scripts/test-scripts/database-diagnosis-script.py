#!/usr/bin/env python3
"""
Quick diagnostic script to see what's actually in your golf database
"""

import sqlite3
from pathlib import Path

def diagnose_database():
    """Check what's actually in the database for Masters tournaments"""
    
    db_path = Path("golf_database.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return
    
    print("🔍 GOLF DATABASE DIAGNOSTIC")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check what tournaments contain "Masters"
        print("\n1️⃣ TOURNAMENTS CONTAINING 'MASTERS':")
        cursor.execute("""
            SELECT tournament_id, tournament_name, tournament_date, season
            FROM tournaments_enhanced 
            WHERE tournament_name LIKE '%master%' OR tournament_name LIKE '%Master%'
            ORDER BY tournament_date
        """)
        
        masters_tournaments = cursor.fetchall()
        print(f"Found {len(masters_tournaments)} Masters tournaments:")
        for tid, name, date, season in masters_tournaments:
            print(f"  • ID {tid}: {name} on {date} (season {season})")
        
        # 2. Check what years we have data for
        print(f"\n2️⃣ TOURNAMENT DATE RANGES:")
        cursor.execute("""
            SELECT MIN(tournament_date), MAX(tournament_date), COUNT(*)
            FROM tournaments_enhanced 
            WHERE tournament_date IS NOT NULL
        """)
        min_date, max_date, count = cursor.fetchone()
        print(f"  Date range: {min_date} to {max_date}")
        print(f"  Total tournaments with dates: {count}")
        
        # 3. Check specific year 2017
        print(f"\n3️⃣ TOURNAMENTS IN 2017:")
        cursor.execute("""
            SELECT tournament_name, tournament_date, season
            FROM tournaments_enhanced 
            WHERE tournament_date LIKE '%2017%' OR season = 2017
            ORDER BY tournament_date
            LIMIT 10
        """)
        
        tournaments_2017 = cursor.fetchall()
        print(f"Found {len(tournaments_2017)} tournaments in 2017:")
        for name, date, season in tournaments_2017:
            print(f"  • {name} on {date} (season {season})")
        
        # 4. Check tournament results for Masters
        if masters_tournaments:
            masters_id = masters_tournaments[0][0]  # Get first Masters tournament ID
            print(f"\n4️⃣ SAMPLE RESULTS FOR MASTERS (ID {masters_id}):")
            cursor.execute("""
                SELECT 
                    p.first_name || ' ' || p.last_name as player_name,
                    tr.final_position,
                    tr.total_strokes,
                    t.tournament_date
                FROM tournament_results tr
                JOIN players p ON tr.player_id = p.player_id
                JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
                WHERE tr.tournament_id = ?
                ORDER BY tr.position_numeric
                LIMIT 5
            """, (masters_id,))
            
            results = cursor.fetchall()
            for player, pos, strokes, date in results:
                print(f"  • {player}: Position {pos}, {strokes} strokes ({date})")
        
        # 5. Check how your API search would work
        print(f"\n5️⃣ API SEARCH TEST FOR 'masters':")
        cursor.execute("""
            SELECT tournament_id, tournament_name, tournament_date, season
            FROM tournaments_enhanced 
            WHERE tournament_name LIKE '%masters%'
            LIMIT 10
        """)
        
        api_results = cursor.fetchall()
        print(f"API would return {len(api_results)} results:")
        for tid, name, date, season in api_results:
            print(f"  • {name} ({date})")
        
        # 6. Check the exact query the interface would make
        print(f"\n6️⃣ WHAT HAPPENS WHEN SEARCHING FOR 'masters' + '2017':")
        cursor.execute("""
            SELECT 
                tr.result_id,
                p.first_name || ' ' || p.last_name as player_name,
                t.tournament_name,
                t.tournament_date,
                tr.final_position,
                tr.total_strokes
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
            WHERE t.tournament_name LIKE '%masters%'
            AND (t.tournament_date LIKE '%2017%' OR t.season = 2017)
            ORDER BY tr.position_numeric
            LIMIT 10
        """)
        
        filtered_results = cursor.fetchall()
        print(f"Filtered results: {len(filtered_results)}")
        for result_id, player, tournament, date, pos, strokes in filtered_results:
            print(f"  • {player}: {pos} place, {strokes} strokes in {tournament} ({date})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_database()