#!/usr/bin/env python3
"""
PGA Tour Data Exploration Script
Analyzes Kaggle dataset structure and prepares for database integration
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class PGADataExplorer:
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)
        self.dataframes = {}
        self.schema_mapping = {}
        
    def load_all_data(self):
        """Load all CSV files from the data directory"""
        print("🏌️ Loading PGA Tour Data...")
        
        csv_files = list(self.data_directory.glob("*.csv"))
        if not csv_files:
            print(f"❌ No CSV files found in {self.data_directory}")
            return False
            
        print(f"📁 Found {len(csv_files)} CSV files:")
        
        for file_path in csv_files:
            try:
                df = pd.read_csv(file_path)
                filename = file_path.name
                self.dataframes[filename] = df
                print(f"  ✅ {filename}: {df.shape[0]:,} rows, {df.shape[1]} columns")
            except Exception as e:
                print(f"  ❌ Error loading {file_path.name}: {e}")
                
        return len(self.dataframes) > 0
    
    def explore_structure(self):
        """Explore the structure of each dataframe"""
        print("\n" + "="*60)
        print("📊 DATA STRUCTURE ANALYSIS")
        print("="*60)
        
        for filename, df in self.dataframes.items():
            print(f"\n🗂️  {filename.upper()}")
            print("-" * 40)
            print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Column analysis
            print(f"\nColumns ({len(df.columns)}):")
            for i, col in enumerate(df.columns, 1):
                dtype = str(df[col].dtype)
                non_null = df[col].count()
                null_pct = (1 - non_null/len(df)) * 100
                unique_vals = df[col].nunique()
                
                print(f"  {i:2d}. {col:<25} | {dtype:<12} | {non_null:>6}/{len(df):<6} | "
                      f"{null_pct:5.1f}% null | {unique_vals:>6} unique")
            
            # Sample data
            print(f"\nSample data (first 3 rows):")
            print(df.head(3).to_string())
            
    def identify_key_entities(self):
        """Identify players, tournaments, and statistical columns"""
        print("\n" + "="*60)
        print("🔍 ENTITY IDENTIFICATION")
        print("="*60)
        
        entities = {
            'players': [],
            'tournaments': [],
            'statistics': [],
            'scores': [],
            'dates': []
        }
        
        for filename, df in self.dataframes.items():
            print(f"\n📋 {filename}:")
            
            # Player identification
            player_cols = [col for col in df.columns if any(term in col.lower() for term in 
                          ['player', 'golfer'])]
            if player_cols:
                entities['players'].extend([(filename, col) for col in player_cols])
                unique_players = df[player_cols[0]].nunique() if player_cols else 0
                print(f"  👤 Player columns: {player_cols} ({unique_players:,} unique players)")
            
            # Tournament identification  
            tournament_cols = [col for col in df.columns if any(term in col.lower() for term in 
                              ['tournament', 'event', 'purse', 'par', 'course'])]
            if tournament_cols:
                entities['tournaments'].extend([(filename, col) for col in tournament_cols])
                print(f"  🏆 Tournament columns: {tournament_cols}")
            
            # Statistical columns
            stat_keywords = ['distance', 'accuracy', 'putt', 'green', 'fairway', 'birdie', 
                           'eagle', 'par', 'bogey', 'average', 'percentage', 'pct', 'sg', 'sg_total']
            stat_cols = [col for col in df.columns if any(term in col.lower() for term in stat_keywords)]
            if stat_cols:
                entities['statistics'].extend([(filename, col) for col in stat_cols])
                print(f"  📈 Statistical columns ({len(stat_cols)}): {stat_cols[:5]}{'...' if len(stat_cols) > 5 else ''}")
            
            # Score columns
            score_cols = [col for col in df.columns if any(term in col.lower() for term in 
                         ['score', 'round', 'position', 'rank', 'finish', 'pos', 'cut', 'strokes'])]
            if score_cols:
                entities['scores'].extend([(filename, col) for col in score_cols])
                print(f"  🎯 Score columns: {score_cols}")
            
            # Date columns
            date_cols = [col for col in df.columns if any(term in col.lower() for term in 
                        ['date', 'year', 'season', 'time'])]
            if date_cols:
                entities['dates'].extend([(filename, col) for col in date_cols])
                print(f"  📅 Date columns: {date_cols}")
        
        self.entities = entities
        return entities
    
    def analyze_data_quality(self):
        """Analyze data quality issues"""
        print("\n" + "="*60)
        print("🔧 DATA QUALITY ANALYSIS")
        print("="*60)
        
        quality_report = {}
        
        for filename, df in self.dataframes.items():
            print(f"\n🔍 {filename}:")
            
            report = {}
            
            # Missing values
            missing = df.isnull().sum()
            missing_pct = (missing / len(df) * 100).round(2)
            high_missing = missing_pct[missing_pct > 10]
            
            if len(high_missing) > 0:
                print(f"  ⚠️  High missing values:")
                for col, pct in high_missing.items():
                    print(f"     {col}: {pct}% ({missing[col]:,} rows)")
            else:
                print(f"  ✅ Missing values: {missing.sum():,} total ({(missing.sum()/len(df)/len(df.columns)*100):.1f}%)")
            
            # Duplicates
            duplicates = df.duplicated().sum()
            print(f"  {'⚠️ ' if duplicates > 0 else '✅'} Duplicate rows: {duplicates:,}")
            
            # Date range analysis
            for col in df.columns:
                if any(term in col.lower() for term in ['date', 'year', 'season']):
                    try:
                        if 'year' in col.lower():
                            years = df[col].dropna().astype(int)
                            print(f"  📅 {col}: {years.min()} - {years.max()} ({years.nunique()} years)")
                        elif 'season' in col.lower():
                            seasons = df[col].dropna().astype(int)
                            print(f"  📅 {col}: {seasons.min()} - {seasons.max()} ({seasons.nunique()} seasons)")
                        else:
                            dates = pd.to_datetime(df[col], errors='coerce').dropna()
                            if len(dates) > 0:
                                print(f"  📅 {col}: {dates.min().date()} - {dates.max().date()}")
                    except:
                        pass
            
            quality_report[filename] = {
                'missing_values': missing.sum(),
                'duplicates': duplicates,
                'total_rows': len(df)
            }
        
        return quality_report
    
    def suggest_schema_mapping(self):
        """Suggest mapping from Kaggle data to database schema"""
        print("\n" + "="*60)
        print("🗺️  SCHEMA MAPPING SUGGESTIONS")
        print("="*60)
        
        mapping_suggestions = {
            'players': {
                'source_files': [],
                'field_mapping': {},
                'notes': []
            },
            'tournaments': {
                'source_files': [],
                'field_mapping': {},
                'notes': []
            },
            'tournament_entries': {
                'source_files': [],
                'field_mapping': {},
                'notes': []
            },
            'round_statistics': {
                'source_files': [],
                'field_mapping': {},
                'notes': []
            }
        }
        
        # Analyze each file for mapping potential
        for filename, df in self.dataframes.items():
            print(f"\n📋 {filename} → Database Tables:")
            
            cols = [col.lower() for col in df.columns]
            
            # Players table mapping
            if any(term in ' '.join(cols) for term in ['player', 'golfer']):
                mapping_suggestions['players']['source_files'].append(filename)
                player_cols = [col for col in df.columns if 'player' in col.lower() or 'golfer' in col.lower()]
                print(f"  👤 PLAYERS table: {player_cols}")
            
            # Tournaments table mapping
            if any(term in ' '.join(cols) for term in ['tournament', 'event', 'purse', 'par', 'course']):
                mapping_suggestions['tournaments']['source_files'].append(filename)
                tournament_cols = [col for col in df.columns if any(term in col.lower() for term in 
                                  ['tournament', 'event', 'purse', 'par', 'course'])]
                print(f"  🏆 TOURNAMENTS table: {tournament_cols}")
            
            # Tournament entries (results)
            if any(term in ' '.join(cols) for term in ['score', 'round', 'position', 'rank', 'finish', 'pos', 'cut', 'strokes']):
                mapping_suggestions['tournament_entries']['source_files'].append(filename)
                entry_cols = [col for col in df.columns if any(term in col.lower() for term in 
                             ['score', 'round', 'position', 'rank', 'finish', 'pos', 'cut', 'strokes'])]
                print(f"  🎯 TOURNAMENT_ENTRIES table: {entry_cols}")
            
            # Round statistics
            stat_terms = ['distance', 'accuracy', 'putt', 'green', 'fairway', 'birdie', 
                           'eagle', 'bogey', 'average', 'percentage', 'pct', 'sg', 'sg_total']
            if any(term in ' '.join(cols) for term in stat_terms):
                mapping_suggestions['round_statistics']['source_files'].append(filename)
                stat_cols = [col for col in df.columns if any(term in col.lower() for term in stat_terms)]
                print(f"  📊 ROUND_STATISTICS table: {stat_cols}")
        
        self.mapping_suggestions = mapping_suggestions
        return mapping_suggestions
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# PGA Tour Data Exploration Report
Generated: {timestamp}

## Dataset Overview
- **Total files**: {len(self.dataframes)}
- **Total records**: {sum(len(df) for df in self.dataframes.values()):,}
- **Data directory**: {self.data_directory}

## Files Summary
"""
        for filename, df in self.dataframes.items():
            report += f"- **{filename}**: {len(df):,} rows × {len(df.columns)} columns\n"
        
        report += "\n## Key Findings\n"
        
        # Player analysis
        player_files = [f for f, cols in self.entities['players']]
        if player_files:
            total_players = max([self.dataframes[f][col].nunique() 
                               for f, col in self.entities['players']])
            report += f"- **Players**: ~{total_players:,} unique players identified\n"
        
        # Tournament analysis  
        tournament_files = [f for f, cols in self.entities['tournaments']]
        if tournament_files:
            report += f"- **Tournaments**: Data spans multiple tournaments and years\n"
        
        # Statistical depth
        stat_files = set([f for f, cols in self.entities['statistics']])
        report += f"- **Statistics**: {len(stat_files)} files contain detailed performance statistics\n"
        
        report += "\n## Recommended Next Steps\n"
        report += "1. Create data transformation scripts based on identified structure\n"
        report += "2. Set up PostgreSQL database with the designed schema\n"
        report += "3. Build ETL pipeline to load historical data\n"
        report += "4. Validate data integrity and relationships\n"
        report += "5. Create initial Flask API endpoints\n"
        
        return report
    
    def run_full_exploration(self):
        """Run complete data exploration pipeline"""
        print("PGA TOUR DATA EXPLORATION")
        print("="*60)
        
        if not self.load_all_data():
            return False
        
        self.explore_structure()
        self.identify_key_entities()
        self.analyze_data_quality()
        self.suggest_schema_mapping()
        
        # Generate summary
        summary = self.generate_summary_report()
        print("\n" + "="*60)
        print("📋 EXPLORATION COMPLETE")
        print("="*60)
        print(summary)
        
        # Save summary to file
        summary_file = self.data_directory / "exploration_report.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"\n💾 Full report saved to: {summary_file}")
        
        return True

def main():
    """Main execution function"""
    # Update this path to your downloaded Kaggle data directory
    data_directory = "./data/kaggle"  # Adjust as needed
    
    explorer = PGADataExplorer(data_directory)
    
    if explorer.run_full_exploration():
        print("\n🎉 Data exploration completed successfully!")
        print("\nNext steps:")
        print("1. Review the exploration_report.md file")
        print("2. Run the data transformation scripts (coming next)")
        print("3. Set up PostgreSQL database")
    else:
        print("\n❌ Data exploration failed. Check your data directory path.")

if __name__ == "__main__":
    main()