#!/usr/bin/env python3
"""
Check what position columns are available in tournament_results table
"""

import sqlite3
from pathlib import Path

def check_position_data():
    """Check the structure and content of position data"""
    
    db_path = Path("golf_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔍 POSITION DATA ANALYSIS")
        print("=" * 50)
        
        # 1. Check table structure
        print("\n1️⃣ TOURNAMENT_RESULTS TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(tournament_results)")
        columns = cursor.fetchall()
        
        position_columns = []
        for col in columns:
            col_name = col[1]
            print(f"  • {col_name} ({col[2]})")
            if 'position' in col_name.lower() or 'pos' in col_name.lower():
                position_columns.append(col_name)
        
        print(f"\n📍 Position-related columns found: {position_columns}")
        
        # 2. Check sample data from 2017 Masters (ID 227)
        print(f"\n2️⃣ SAMPLE DATA FROM 2017 MASTERS (tournament_id = 227):")
        
        # Build query to check all position columns
        position_cols_str = ", ".join(position_columns) if position_columns else "NULL as no_position_cols"
        
        query = f"""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                {position_cols_str},
                tr.total_strokes,
                tr.made_cut
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            WHERE tr.tournament_id = 227
            ORDER BY tr.total_strokes
            LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Print column headers
        headers = ["Player"] + position_columns + ["Total Strokes", "Made Cut"]
        print("  " + " | ".join(f"{h:15}" for h in headers))
        print("  " + "-" * (len(headers) * 17))
        
        for row in results:
            formatted_row = []
            for i, val in enumerate(row):
                if val is None:
                    formatted_row.append("None")
                else:
                    formatted_row.append(str(val))
            print("  " + " | ".join(f"{val:15}" for val in formatted_row))
        
        # 3. Check if we can find actual position data
        print(f"\n3️⃣ CHECKING FOR NON-NULL POSITION DATA:")
        
        for pos_col in position_columns:
            cursor.execute(f"""
                SELECT COUNT(*) as total, 
                       COUNT({pos_col}) as non_null,
                       MIN({pos_col}) as min_val,
                       MAX({pos_col}) as max_val
                FROM tournament_results 
                WHERE tournament_id = 227
            """)
            
            total, non_null, min_val, max_val = cursor.fetchone()
            print(f"  • {pos_col}: {non_null}/{total} non-null values (range: {min_val} to {max_val})")
        
        # 4. Try to find the actual winner
        print(f"\n4️⃣ TRYING TO FIND THE 2017 MASTERS WINNER:")
        
        # Try different approaches to find winner
        approaches = [
            ("Lowest total strokes", "ORDER BY tr.total_strokes ASC"),
            ("Made cut = 1, lowest strokes", "WHERE tr.made_cut = 1 ORDER BY tr.total_strokes ASC"),
        ]
        
        if position_columns:
            for pos_col in position_columns:
                approaches.append((f"Minimum {pos_col}", f"ORDER BY {pos_col} ASC"))
        
        for approach_name, order_clause in approaches:
            try:
                query = f"""
                    SELECT 
                        p.first_name || ' ' || p.last_name as player_name,
                        tr.total_strokes,
                        tr.made_cut
                    FROM tournament_results tr
                    JOIN players p ON tr.player_id = p.player_id
                    WHERE tr.tournament_id = 227
                    {order_clause}
                    LIMIT 3
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                print(f"\n  {approach_name}:")
                for i, (player, strokes, made_cut) in enumerate(results, 1):
                    print(f"    {i}. {player} - {strokes} strokes (made cut: {made_cut})")
                    
            except Exception as e:
                print(f"    {approach_name}: Error - {e}")
        
        # 5. Quick reality check - who actually won the 2017 Masters?
        print(f"\n5️⃣ REALITY CHECK:")
        print("The 2017 Masters was won by Sergio Garcia in a playoff")
        print("Let's see if Sergio Garcia is in our data...")
        
        cursor.execute("""
            SELECT 
                p.first_name || ' ' || p.last_name as player_name,
                tr.total_strokes,
                tr.made_cut
            FROM tournament_results tr
            JOIN players p ON tr.player_id = p.player_id
            WHERE tr.tournament_id = 227
            AND (p.first_name LIKE '%Sergio%' OR p.last_name LIKE '%Garcia%')
        """)
        
        sergio_results = cursor.fetchall()
        if sergio_results:
            for player, strokes, made_cut in sergio_results:
                print(f"  • Found: {player} - {strokes} strokes (made cut: {made_cut})")
        else:
            print("  • Sergio Garcia not found in 2017 Masters data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_position_data()