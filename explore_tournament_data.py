#!/usr/bin/env python3
"""
Explore the new tournament-level golf data
"""

import pandas as pd
from pathlib import Path

def explore_tournament_data():
    # Path to the new tournament data
    tournament_data_path = Path("data/kaggle/pga_tour_alternative/ASA All PGA Raw Data - Tourn Level.csv")
    player_data_path = Path("data/kaggle/pga_tour_alternative/pgaTourData.csv")
    
    print("🏌️ EXPLORING TOURNAMENT-LEVEL GOLF DATA")
    print("=" * 60)
    
    if not tournament_data_path.exists():
        print(f"❌ Tournament file not found: {tournament_data_path}")
        return
    
    try:
        # Load the tournament data
        print("📊 Loading tournament-level data...")
        df_tournament = pd.read_csv(tournament_data_path)
        
        print(f"📏 Tournament Data: {len(df_tournament):,} rows × {len(df_tournament.columns)} columns")
        print(f"💾 Size: {tournament_data_path.stat().st_size / (1024*1024):.1f} MB")
        
        print(f"\n📋 TOURNAMENT DATA COLUMNS ({len(df_tournament.columns)}):")
        for i, col in enumerate(df_tournament.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n🔍 FIRST 3 ROWS OF TOURNAMENT DATA:")
        print("-" * 80)
        print(df_tournament.head(3).to_string())
        
        # Key golf data analysis
        print(f"\n🎯 TOURNAMENT DATA ANALYSIS:")
        
        # Check for key columns
        key_checks = {
            'Players': [col for col in df_tournament.columns if 'player' in col.lower()],
            'Tournaments': [col for col in df_tournament.columns if 'tournament' in col.lower() or 'event' in col.lower()],
            'Scores': [col for col in df_tournament.columns if 'score' in col.lower() or 'strokes' in col.lower()],
            'Positions': [col for col in df_tournament.columns if 'pos' in col.lower() or 'rank' in col.lower() or 'finish' in col.lower() or 'cut' in col.lower()],
            'Prize Money': [col for col in df_tournament.columns if 'money' in col.lower() or 'prize' in col.lower() or 'earning' in col.lower() or 'purse' in col.lower()],
            'Dates': [col for col in df_tournament.columns if 'date' in col.lower() or 'year' in col.lower() or 'season' in col.lower()],
            'Rounds': [col for col in df_tournament.columns if 'round' in col.lower() or 'r1' in col.lower() or 'r2' in col.lower() or 'r3' in col.lower() or 'r4' in col.lower()],
            'Courses': [col for col in df_tournament.columns if 'course' in col.lower() or 'venue' in col.lower() or 'location' in col.lower() or 'hole_par' in col.lower()],
            'Stats': [col for col in df_tournament.columns if 'sg' in col.lower()]
        }
        
        for category, cols in key_checks.items():
            if cols:
                print(f"  ✅ {category}: {cols}")
                # Show unique counts for key columns
                if cols and len(cols) > 0:
                    main_col = cols[0]
                    unique_count = df_tournament[main_col].nunique()
                    print(f"     └─ {unique_count:,} unique values in '{main_col}'")
            else:
                print(f"  ❌ {category}: No columns found")
        
        # Date range analysis
        date_cols = [col for col in df_tournament.columns if 'date' in col.lower() or 'year' in col.lower()]
        if date_cols:
            print(f"\n📅 DATE RANGE:")
            for col in date_cols:
                try:
                    if df_tournament[col].dtype in ['int64', 'float64']:
                        print(f"  {col}: {df_tournament[col].min()} - {df_tournament[col].max()}")
                    else:
                        # Try to parse dates
                        dates = pd.to_datetime(df_tournament[col], errors='coerce')
                        if not dates.isnull().all():
                            print(f"  {col}: {dates.min()} to {dates.max()}")
                except:
                    pass
        
        # Compare with player data
        if player_data_path.exists():
            df_player = pd.read_csv(player_data_path)
            print(f"\n🔄 COMPARISON WITH PLAYER DATA:")
            print(f"  Tournament data: {len(df_tournament):,} records")
            print(f"  Player data: {len(df_player):,} records")
            print(f"  → Tournament data is {len(df_tournament)/len(df_player):.1f}x larger!")
        
        # Data quality check
        print(f"\n🔧 DATA QUALITY:")
        missing_data = df_tournament.isnull().sum()
        high_missing = missing_data[missing_data > len(df_tournament) * 0.1]  # More than 10% missing
        
        if len(high_missing) > 0:
            print(f"  ⚠️  Columns with >10% missing data:")
            for col, missing_count in high_missing.items():
                pct = (missing_count / len(df_tournament)) * 100
                print(f"     {col}: {pct:.1f}% missing")
        else:
            print(f"  ✅ Data quality looks good (low missing values)")
        
        # Storage recommendations
        print(f"\n💡 NEXT STEPS RECOMMENDATIONS:")
        print(f"  1. This tournament data looks much more detailed than player data")
        print(f"  2. Consider updating your database schema to handle tournament-by-tournament results")
        print(f"  3. This data likely contains individual tournament performances vs. yearly aggregates")
        print(f"  4. You may want to create separate ETL processes for:")
        print(f"     - Tournament results (detailed, per-event)")
        print(f"     - Player yearly stats (aggregated)")
        
        return df_tournament
        
    except Exception as e:
        print(f"❌ Error reading tournament data: {e}")
        return None

def suggest_database_updates():
    """Suggest database schema updates based on the new data"""
    print(f"\n🗄️ DATABASE SCHEMA SUGGESTIONS:")
    print("=" * 50)
    print("""
Based on the tournament-level data, consider these table additions:

1. **tournament_results** table:
   - tournament_id, player_id, year
   - final_position, total_score, prize_money
   - made_cut, rounds_played
   - individual round scores (R1, R2, R3, R4)

2. **tournaments** table (enhanced):
   - tournament_name, venue, date
   - field_size, cut_line, winning_score
   - total_purse

3. **courses** table:
   - course_name, location, par, yardage
   - Link tournaments to specific courses

This will give you MUCH more detailed data for your natural language queries!

Examples of queries you could answer:
- "Show me Tiger Woods' performance at the Masters"
- "Which tournament had the lowest winning score in 2018?"
- "How did players perform in the final round at Pebble Beach?"
""")

if __name__ == "__main__":
    df = explore_tournament_data()
    if df is not None:
        suggest_database_updates()
        print(f"\n🚀 Ready to build enhanced ETL pipeline with tournament data!")
    else:
        print(f"\n❌ Could not load tournament data. Check file path.")