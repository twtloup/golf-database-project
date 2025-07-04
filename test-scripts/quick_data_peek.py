#!/usr/bin/env python3
"""
Quick peek at the golf data structure
"""

import pandas as pd
from pathlib import Path

def quick_peek():
    # Find the CSV file
    data_path = Path("data/kaggle/pga_tour_alternative/pgaTourData.csv")
    
    if not data_path.exists():
        print(f"❌ File not found: {data_path}")
        return
    
    print("🏌️ QUICK GOLF DATA PEEK")
    print("=" * 50)
    
    try:
        # Read the CSV
        df = pd.read_csv(data_path)
        
        print(f"📊 Dataset: {len(df):,} rows × {len(df.columns)} columns")
        print(f"\n📋 COLUMNS:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n🔍 FIRST 5 ROWS:")
        print("-" * 50)
        print(df.head().to_string())
        
        print(f"\n📈 BASIC STATS:")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"Numeric columns: {len(numeric_cols)}")
            print(df[numeric_cols].describe())
        
        # Check for key golf data
        print(f"\n🎯 KEY GOLF DATA DETECTED:")
        if 'Player' in df.columns:
            print(f"  Players: {df['Player'].nunique():,} unique players")
        if 'Tournament' in df.columns:
            print(f"  Tournaments: {df['Tournament'].nunique():,} unique tournaments")
        if 'Year' in df.columns:
            print(f"  Years: {df['Year'].min()} - {df['Year'].max()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_peek()