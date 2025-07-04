#!/usr/bin/env python3
"""
Explore the downloaded golf datasets to understand their structure
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

class GolfDataExplorer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / 'data' / 'kaggle'
        
    def explore_csv_file(self, filepath):
        """Explore a single CSV file"""
        print(f"\n📊 EXPLORING: {filepath.name}")
        print("=" * 60)
        
        try:
            # Read the CSV
            df = pd.read_csv(filepath)
            
            # Basic info
            print(f"📏 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
            print(f"💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
            
            # Column information
            print(f"\n📋 COLUMNS ({len(df.columns)}):")
            for i, col in enumerate(df.columns, 1):
                dtype = df[col].dtype
                null_count = df[col].isnull().sum()
                null_pct = (null_count / len(df)) * 100
                print(f"  {i:2d}. {col:<25} | {dtype:<10} | {null_count:6,} nulls ({null_pct:4.1f}%)")
            
            # Sample data
            print(f"\n🔍 SAMPLE DATA (first 3 rows):")
            print("-" * 60)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 20)
            print(df.head(3).to_string())
            
            # Data types summary
            print(f"\n📊 DATA TYPES SUMMARY:")
            dtype_counts = df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                print(f"  {dtype}: {count} columns")
            
            # Look for key golf-related columns
            print(f"\n🏌️ GOLF-SPECIFIC COLUMNS DETECTED:")
            golf_keywords = ['player', 'tournament', 'score', 'round', 'par', 'stroke', 'putt', 'fairway', 'green', 'course', 'year', 'date', 'rank', 'position', 'money', 'prize']
            
            detected_cols = []
            for col in df.columns:
                for keyword in golf_keywords:
                    if keyword.lower() in col.lower():
                        detected_cols.append((col, keyword))
                        break
            
            if detected_cols:
                for col, keyword in detected_cols:
                    print(f"  🎯 {col} (matches: {keyword})")
            else:
                print("  No obvious golf keywords found in column names")
            
            # Unique values for key columns (if they exist)
            potential_key_cols = ['player', 'tournament', 'year', 'round']
            for col in df.columns:
                if any(key in col.lower() for key in potential_key_cols):
                    unique_count = df[col].nunique()
                    print(f"\n🔑 {col}: {unique_count:,} unique values")
                    if unique_count <= 20:
                        print(f"   Values: {sorted(df[col].unique())}")
                    else:
                        print(f"   Sample: {sorted(df[col].unique())[:10]}")
            
            # Date range analysis
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
            if date_cols:
                print(f"\n📅 DATE RANGE ANALYSIS:")
                for col in date_cols:
                    try:
                        if df[col].dtype == 'object':
                            # Try to parse as date
                            dates = pd.to_datetime(df[col], errors='coerce')
                            if not dates.isnull().all():
                                print(f"  {col}: {dates.min()} to {dates.max()}")
                        else:
                            print(f"  {col}: {df[col].min()} to {df[col].max()}")
                    except:
                        print(f"  {col}: Could not parse date range")
            
            return df
            
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return None
    
    def map_to_database_schema(self, df, filename):
        """Suggest how this data maps to our database schema"""
        print(f"\n🗄️ DATABASE MAPPING SUGGESTIONS for {filename}")
        print("=" * 60)
        
        # Our database tables
        tables = {
            'players': ['player_id', 'name', 'country', 'birth_date', 'turned_pro'],
            'courses': ['course_id', 'name', 'location', 'par', 'yardage'],
            'tournaments': ['tournament_id', 'name', 'start_date', 'end_date', 'course_id', 'prize_money'],
            'tournament_entries': ['entry_id', 'tournament_id', 'player_id', 'final_position', 'total_score', 'prize_money'],
            'rounds': ['round_id', 'entry_id', 'round_number', 'score', 'strokes_gained']
        }
        
        print("🎯 COLUMN MAPPING SUGGESTIONS:")
        
        for table_name, expected_cols in tables.items():
            print(f"\n📋 {table_name.upper()} table:")
            matches = []
            
            for expected_col in expected_cols:
                # Look for columns that might match
                for actual_col in df.columns:
                    if self._columns_match(expected_col, actual_col):
                        matches.append(f"  ✅ {expected_col} ← {actual_col}")
                        break
                else:
                    matches.append(f"  ❌ {expected_col} (not found)")
            
            for match in matches:
                print(match)
        
        # Additional suggestions
        print(f"\n💡 ADDITIONAL OBSERVATIONS:")
        print(f"  • Total records: {len(df):,}")
        print(f"  • Columns available: {len(df.columns)}")
        print(f"  • Consider creating lookup tables for repeated values")
        print(f"  • Check for data quality issues before loading")
    
    def _columns_match(self, expected, actual):
        """Check if two column names likely refer to the same thing"""
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        # Direct match
        if expected_lower == actual_lower:
            return True
        
        # Partial matches
        matches = {
            'player': ['player', 'name'],
            'tournament': ['tournament', 'event'],
            'score': ['score', 'total'],
            'round': ['round', 'rd'],
            'position': ['position', 'rank', 'finish'],
            'money': ['money', 'prize', 'earnings'],
            'course': ['course', 'venue'],
            'date': ['date', 'year']
        }
        
        if expected_lower in matches:
            return any(keyword in actual_lower for keyword in matches[expected_lower])
        
        return False
    
    def explore_all_datasets(self):
        """Explore all downloaded datasets"""
        print("🏌️ GOLF DATA EXPLORATION")
        print("=" * 60)
        
        if not self.data_dir.exists():
            print(f"❌ Data directory not found: {self.data_dir}")
            return
        
        csv_files = []
        for dataset_dir in self.data_dir.iterdir():
            if dataset_dir.is_dir():
                csv_files.extend(dataset_dir.glob('*.csv'))
        
        if not csv_files:
            print("❌ No CSV files found in data directory")
            return
        
        print(f"📁 Found {len(csv_files)} CSV files to explore")
        
        for csv_file in csv_files:
            df = self.explore_csv_file(csv_file)
            if df is not None:
                self.map_to_database_schema(df, csv_file.name)
                print("\n" + "=" * 60)
        
        print(f"\n🎉 Data exploration complete!")
        print(f"\nNext steps:")
        print(f"1. Review the column mappings above")
        print(f"2. Create an ETL script to transform and load this data")
        print(f"3. Update your database schema if needed")
        print(f"4. Test data quality and relationships")

def main():
    explorer = GolfDataExplorer()
    explorer.explore_all_datasets()

if __name__ == "__main__":
    main()