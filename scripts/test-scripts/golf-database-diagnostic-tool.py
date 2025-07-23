#!/usr/bin/env python3
"""
Simple Golf Database Diagnostic Tool
No external dependencies required - just uses SQLite
"""

import sqlite3
from pathlib import Path

def diagnose_masters_2017_simple():
    """Simple diagnosis of the 2017 Masters issue"""
    
    db_path = Path("golf_database.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        print(f"   Make sure you're running this from the project root directory")
        print(f"   Current working directory should contain: golf_database.db")
        return
    
    print("🏌️ SIMPLE MASTERS 2017 DIAGNOSTIC")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check database tables exist
        print("\n1️⃣ CHECKING DATABASE STRUCTURE:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['tournaments_enhanced', 'tournament_results', 'players', 'courses_enhanced']
        for table in required_tables:
            if table in tables:
                print(f"  ✅ {table} table exists")
            else:
                print(f"  ❌ {table} table MISSING")
                return
        
        # 2. Find Masters tournaments
        print("\n2️⃣ SEARCHING FOR MASTERS TOURNAMENTS:")
        cursor.execute("""
            SELECT tournament_id, tournament_name, tournament_date, season
            FROM tournaments_enhanced 
            WHERE tournament_name LIKE '%aster%'
            ORDER BY tournament_date
        """)
        
        masters_tournaments = cursor.fetchall()
        masters_2017_id = None
        
        print(f"   Found {len(masters_tournaments)} Masters tournaments:")
        for tid, name, date, season in masters_tournaments:
            year_indicator = ""
            if '2017' in str(date) or season == 2017:
                masters_2017_id = tid
                year_indicator = " 🎯 <- This is 2017!"
            print(f"   • ID {tid}: '{name}' on {date} (season {season}){year_indicator}")
        
        if not masters_2017_id:
            print("\n❌ CRITICAL ISSUE: No 2017 Masters tournament found!")
            print("   This means either:")
            print("   - The tournament data wasn't loaded properly")
            print("   - The tournament is named differently")
            print("   - The year/date data is incorrect")
            return
        
        # 3. Check all players in 2017 Masters
        print(f"\n3️⃣ CHECKING PLAYERS IN 2017 MASTERS (ID {masters_2017_id}):")
        cursor.execute("""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                tr.final_position,
                tr.position_numeric,
                tr.total_strokes,
                tr.made_cut
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            WHERE tr.tournament_id = ?
            ORDER BY tr.total_strokes ASC
        """, (masters_2017_id,))
        
        all_players = cursor.fetchall()
        print(f"   Found {len(all_players)} players in 2017 Masters")
        
        # Look for key players
        sergio_found = False
        justin_found = False
        
        print(f"\n   Top 15 by stroke count:")
        for i, (player, final_pos, pos_numeric, strokes, made_cut) in enumerate(all_players[:15], 1):
            # Handle None values safely
            cut_status = "✅" if made_cut else "❌"
            final_pos_str = str(final_pos) if final_pos is not None else "None"
            pos_numeric_str = str(pos_numeric) if pos_numeric is not None else "None"
            strokes_str = str(strokes) if strokes is not None else "None"
            
            # Check for specific players
            if player and 'sergio' in player.lower() and 'garcia' in player.lower():
                sergio_found = True
                marker = " 🏆 SERGIO GARCIA (should be winner!)"
            elif player and 'justin' in player.lower() and 'rose' in player.lower():
                justin_found = True
                marker = " 🥈 JUSTIN ROSE (runner-up)"
            else:
                marker = ""
            
            print(f"   {i:2d}. {player:<25} | Pos: {final_pos_str:<8} | Numeric: {pos_numeric_str:<8} | Strokes: {strokes_str:<8} | Cut: {cut_status}{marker}")
        
        # 4. Specific search for Sergio Garcia
        print(f"\n4️⃣ SPECIFIC SEARCH FOR SERGIO GARCIA:")
        cursor.execute("""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                tr.final_position,
                tr.position_numeric,
                tr.total_strokes,
                tr.made_cut
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            WHERE tr.tournament_id = ?
            AND (p.first_name LIKE '%sergio%' OR p.last_name LIKE '%garcia%' 
                 OR (p.first_name || ' ' || p.last_name) LIKE '%sergio garcia%')
        """, (masters_2017_id,))
        
        sergio_results = cursor.fetchall()
        if sergio_results:
            print(f"   ✅ Found Sergio Garcia in 2017 Masters!")
            for player, final_pos, pos_numeric, strokes, made_cut in sergio_results:
                print(f"   • {player}: Position '{final_pos}' (numeric: {pos_numeric}), {strokes} strokes, made cut: {made_cut}")
        else:
            print(f"   ❌ Sergio Garcia NOT FOUND in 2017 Masters data!")
            print(f"   This is a major data issue - he won the tournament!")
        
        # 5. Check what your current API query returns
        print(f"\n5️⃣ SIMULATING YOUR CURRENT API QUERY:")
        print(f"   Query: 'who won the masters in 2017?'")
        print(f"   This translates to: tournament='masters', year='2017', position='1'")
        
        # Simulate the current API logic
        cursor.execute("""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                t.tournament_name,
                tr.final_position,
                tr.position_numeric,
                tr.total_strokes,
                tr.made_cut
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
            WHERE tr.made_cut = 1
            AND t.tournament_name LIKE '%aster%'
            AND (t.tournament_date LIKE '%2017%' OR t.season = 2017)
            AND tr.position_numeric = 1
            ORDER BY tr.total_strokes ASC
        """)
        
        api_simulation = cursor.fetchall()
        print(f"\n   Current API query (position_numeric = 1) returns {len(api_simulation)} results:")
        if api_simulation:
            for player, tournament, final_pos, pos_numeric, strokes, made_cut in api_simulation:
                print(f"   • {player} in {tournament}: {strokes} strokes (pos: {final_pos})")
        else:
            print(f"   ❌ No results! This explains why your query isn't working.")
        
        # 6. Try alternative position detection methods
        print(f"\n6️⃣ TRYING ALTERNATIVE POSITION DETECTION:")
        
        # Method 1: Check final_position patterns
        patterns = ['1', 'T1', '1st', 'W', 'Win', 'Winner']
        for pattern in patterns:
            cursor.execute("""
                SELECT COUNT(*), p.first_name || ' ' || p.last_name as player_name
                FROM tournament_results tr
                JOIN players p ON tr.player_id = p.player_id
                WHERE tr.tournament_id = ? AND tr.final_position = ?
                GROUP BY player_name
            """, (masters_2017_id, pattern))
            
            results = cursor.fetchall()
            if results:
                print(f"   Pattern '{pattern}': {results[0][0]} players found")
                for count, player in results:
                    print(f"     • {player}")
        
        # Method 2: Lowest stroke count
        print(f"\n   Lowest stroke count method:")
        cursor.execute("""
            SELECT 
                MIN(tr.total_strokes) as winning_score,
                COUNT(*) as players_with_score
            FROM tournament_results tr
            WHERE tr.tournament_id = ? AND tr.made_cut = 1
        """, (masters_2017_id,))
        
        min_score, count_at_min = cursor.fetchone()
        print(f"   Winning score: {min_score} strokes ({count_at_min} players)")
        
        cursor.execute("""
            SELECT p.first_name || ' ' || p.last_name as player_name
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            WHERE tr.tournament_id = ? AND tr.total_strokes = ? AND tr.made_cut = 1
        """, (masters_2017_id, min_score))
        
        winners_by_score = cursor.fetchall()
        print(f"   Players with winning score:")
        for (player,) in winners_by_score:
            print(f"     • {player}")
        
        # 7. Data Quality Analysis
        print(f"\n7️⃣ DATA QUALITY ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(tr.final_position) as has_final_position,
                COUNT(tr.position_numeric) as has_position_numeric,
                COUNT(tr.total_strokes) as has_total_strokes,
                MIN(tr.total_strokes) as min_strokes,
                MAX(tr.total_strokes) as max_strokes
            FROM tournament_results tr
            WHERE tr.tournament_id = ?
        """, (masters_2017_id,))
        
        quality_stats = cursor.fetchone()
        total, has_final, has_numeric, has_strokes, min_strokes, max_strokes = quality_stats
        
        print(f"   • Total players: {total}")
        print(f"   • Has final_position: {has_final} ({has_final/total*100:.1f}%)")
        print(f"   • Has position_numeric: {has_numeric} ({has_numeric/total*100:.1f}%)")
        print(f"   • Has total_strokes: {has_strokes} ({has_strokes/total*100:.1f}%)")
        if min_strokes and max_strokes:
            print(f"   • Stroke range: {min_strokes} to {max_strokes}")
        
        # 8. Summary and recommendations
        print(f"\n7️⃣ DIAGNOSIS SUMMARY:")
        print(f"=" * 40)
        
        issues = []
        if not sergio_found:
            issues.append("Sergio Garcia missing from 2017 Masters data")
        if len(api_simulation) == 0:
            issues.append("position_numeric = 1 detection not working")
        if len(winners_by_score) == 0:
            issues.append("No players found with winning stroke count")
        
        if issues:
            print(f"   ❌ ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"      {i}. {issue}")
        else:
            print(f"   ✅ Basic data structure looks OK")
        
        print(f"\n   🔧 RECOMMENDED FIXES:")
        print(f"      1. Update API endpoint with improved winner detection")
        print(f"      2. Add fallback methods for position detection")
        print(f"      3. Test with updated tournament name matching")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_masters_2017_simple()