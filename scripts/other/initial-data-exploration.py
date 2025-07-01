import pandas as pd
import numpy as np
import os

# List all CSV files in the downloaded dataset
data_directory = data_directory = 'C:/Users/tomlo/coding-projects/golf-database-project/data/kaggle'  # Adjust path as needed
csv_files = [f for f in os.listdir(data_directory) if f.endswith('.csv')]
print("Available CSV files:")
for file in csv_files:
    print(f"- {file}")

# Function to quickly examine each CSV
def explore_csv(filename):
    print(f"\n=== {filename} ===")
    df = pd.read_csv(os.path.join(data_directory, filename))
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:")
    print(df.head(2))
    print(f"Data types:")
    print(df.dtypes)
    return df

# Examine each file
dataframes = {}
for file in csv_files:
    dataframes[file] = explore_csv(file)

# Check for missing values and data quality
def assess_data_quality(df, filename):
    print(f"\n=== Data Quality: {filename} ===")
    print(f"Missing values:")
    print(df.isnull().sum())
    print(f"\nDuplicate rows: {df.duplicated().sum()}")
    
    # Check date ranges if date columns exist
    date_columns = df.select_dtypes(include=['datetime64', 'object']).columns
    for col in date_columns:
        if 'date' in col.lower() or 'year' in col.lower():
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                print(f"\n{col} range: {dates.min()} to {dates.max()}")
            except:
                print(f"\n{col} - could not parse as dates")

# Assess each dataframe
for filename, df in dataframes.items():
    assess_data_quality(df, filename)

# Create mapping from Kaggle data to your database schema
def create_schema_mapping(dataframes):
    mapping = {
        'players': {
            'source_file': None,  # Will determine from data
            'field_mapping': {
                # 'kaggle_column': 'your_db_column'
                'player': 'full_name',
                'Player_initial_last': 'player_name'
                # Add more mappings as you discover the data structure
            }
        },
        'tournaments': {
            'source_file': None,
            'field_mapping': {
                'tournament id': 'tournament_id',
                'tournament name': 'tournament_name',
                'season': 'year',
                'course': 'course_name',
                'purse' : 'prize_money',
                'hole_par' : 'par'
            }
        },
        'tournament_entries': {
            'source_file': None,
            'field_mapping': {
                'player id': 'player_id',  # Will need lookup
                'tournament id': 'tournament_id',  # Will need lookup
                'Finish': 'final_position',
                'strokes': 'total_score',
                'n_rounds' : 'rounds_played',
                'made_cut' : 'made_cut',
                'sg_putt' : 'sg_putting',
                'sg_arg' : 'sg_arg',
                'sg_app' : 'sg_approach',
                'sg_ott' : 'sg_fromthetee',
                'sg_t2g' : 'sg_t2g', 
                'sg_total' : 'sg_total'
            }
        }
    }
    return mapping

# Analyze the structure to understand relationships
def analyze_relationships(dataframes):
    print("=== Relationship Analysis ===")
    
    for filename, df in dataframes.items():
        print(f"\n{filename}:")
        
        # Look for player identifiers
        player_columns = [col for col in df.columns if any(id in col.lower() for id in
                         ['player'])]
        if player_columns:
            print(f"  Player columns: {player_columns}")
            print(f"  Unique players: {df[player_columns[0]].nunique() if player_columns else 'N/A'}")
        
        # Look for tournament identifiers  
        tournament_columns = [col for col in df.columns if any(name in col.lower() for name in 
                              ['tournament', 'event', 'purse', 'par'])]
        if tournament_columns:
            print(f"  Tournament columns: {tournament_columns}")
            print(f"  Unique tournaments: {df[tournament_columns[0]].nunique() if tournament_columns else 'N/A'}")
        
        # Look for statistical columns
        stat_columns = [col for col in df.columns if any(stat in col.lower() for stat in 
                       ['score', 'distance', 'accuracy', 'putt', 'birdie', 'par', 'bogey', 'strokes', 'sg'])]
        if stat_columns:
            print(f"  Stat columns: {stat_columns[:5]}...")  # Show first 5

analyze_relationships(dataframes)




