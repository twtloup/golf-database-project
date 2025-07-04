#!/usr/bin/env python3
"""
Test Kaggle API connection and search for golf datasets
"""

import os
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

def test_kaggle_connection():
    """Test if Kaggle API credentials are working"""
    print("🔍 Testing Kaggle API Connection...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize and authenticate Kaggle API
        api = KaggleApi()
        api.authenticate()
        print("✅ Kaggle API authentication successful!")
        
        # Test by searching for golf-related datasets
        print("\n🏌️ Searching for golf datasets...")
        datasets = api.dataset_list(search='golf pga', max_size=10)
        
        print(f"📊 Found {len(datasets)} golf-related datasets:")
        for i, dataset in enumerate(datasets, 1):
            print(f"  {i}. {dataset.ref}")
            print(f"     Title: {dataset.title}")
            print(f"     Size: {dataset.size}")
            print(f"     Downloads: {dataset.downloadCount}")
            print(f"     Last Updated: {dataset.lastUpdated}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Kaggle API error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure kaggle.json is in your project directory")
        print("2. Check your KAGGLE_USERNAME and KAGGLE_KEY in .env file")
        print("3. Verify your Kaggle account has API access enabled")
        return False

def recommend_datasets():
    """Recommend specific golf datasets for our project"""
    recommended = [
        {
            'ref': 'bradklassen/pga-tour-20102018-data',
            'description': 'Comprehensive PGA Tour data 2010-2018 with detailed statistics',
            'why': 'Great for historical tournament results and player performance'
        },
        {
            'ref': 'jmpark746/pga-tour-data-2010-2018', 
            'description': 'Alternative PGA Tour dataset with different structure',
            'why': 'Good for cross-validation and additional data points'
        },
        {
            'ref': 'dansbecker/golf-scoring',
            'description': 'Golf scoring data focused on stroke analysis',
            'why': 'Useful for detailed round-by-round analysis'
        }
    ]
    
    print("🎯 Recommended Golf Datasets:")
    print("=" * 50)
    
    for dataset in recommended:
        print(f"📋 {dataset['ref']}")
        print(f"   Description: {dataset['description']}")
        print(f"   Why useful: {dataset['why']}")
        print()

if __name__ == "__main__":
    print("KAGGLE API CONNECTION TEST")
    print("=" * 40)
    
    if test_kaggle_connection():
        print("\n" + "=" * 40)
        recommend_datasets()
        print("\nNext step: Run the data download script!")
    else:
        print("\n❌ Fix Kaggle API setup before proceeding")