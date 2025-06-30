"""
Data loading and ETL utilities
"""
import pandas as pd
import os
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv

load_dotenv()

class DataLoader:
    def __init__(self):
        self.data_dir = './data'
        self.kaggle_dir = './data/kaggle'
ECHO is off.
    def setup_kaggle(self):
        """Setup Kaggle API credentials"""
        api = KaggleApi()
        api.authenticate()
        return api
ECHO is off.
    def download_golf_datasets(self):
        """Download popular golf datasets from Kaggle"""
        api = self.setup_kaggle()
ECHO is off.
        datasets = [
            'bradklassen/pga-tour-20102018-data',
            'jmpark746/pga-tour-data-2010-2018'
        ]
ECHO is off.
        for dataset in datasets:
            try:
                print(f"📥 Downloading {dataset}...")
                api.dataset_download_files(dataset, path=self.kaggle_dir, unzip=True)
                print(f"✅ Downloaded {dataset}")
            except Exception as e:
                print(f"❌ Error downloading {dataset}: {e}")
ECHO is off.
    def load_csv_data(self, filename):
        """Load CSV data with error handling"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            df = pd.read_csv(filepath)
            print(f"✅ Loaded {filename}: {len^(df^)} rows")
            return df
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return None
