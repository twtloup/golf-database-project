#!/usr/bin/env python3
"""
Download and organize golf datasets from Kaggle
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile

class GolfDataDownloader:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / 'data'
        self.kaggle_dir = self.data_dir / 'kaggle'
        self.raw_dir = self.data_dir / 'raw'
        
        # Create directories if they don't exist
        self.kaggle_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        load_dotenv()
        
    def setup_kaggle_api(self):
        """Initialize and authenticate Kaggle API"""
        try:
            api = KaggleApi()
            api.authenticate()
            print("✅ Kaggle API authenticated successfully")
            return api
        except Exception as e:
            print(f"❌ Kaggle authentication failed: {e}")
            return None
    
    def download_dataset(self, api, dataset_ref, custom_name=None):
        """Download a specific dataset from Kaggle"""
        try:
            # Create subdirectory for this dataset
            dataset_name = custom_name or dataset_ref.split('/')[-1]
            dataset_path = self.kaggle_dir / dataset_name
            dataset_path.mkdir(exist_ok=True)
            
            print(f"📥 Downloading {dataset_ref}...")
            print(f"   Saving to: {dataset_path}")
            
            # Download and unzip
            api.dataset_download_files(
                dataset_ref, 
                path=str(dataset_path), 
                unzip=True
            )
            
            # List downloaded files
            files = list(dataset_path.glob('*'))
            print(f"✅ Downloaded {len(files)} files:")
            for file in files:
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"   📄 {file.name} ({size_mb:.1f} MB)")
            
            return True, dataset_path
            
        except Exception as e:
            print(f"❌ Error downloading {dataset_ref}: {e}")
            return False, None
    
    def download_recommended_datasets(self):
        """Download our recommended golf datasets"""
        api = self.setup_kaggle_api()
        if not api:
            return False
        
        # Define datasets to download
        datasets = [
            {
                'ref': 'bradklassen/pga-tour-20102018-data',
                'name': 'pga_tour_2010_2018',
                'priority': 1,
                'description': 'Main PGA Tour dataset with comprehensive statistics'
            },
            {
                'ref': 'jmpark746/pga-tour-data-2010-2018',
                'name': 'pga_tour_alternative',
                'priority': 2,
                'description': 'Alternative PGA Tour dataset for comparison'
            },
            {
                'ref': 'robikscube/pga-tour-golf-data-20152022',
                'name': 'pga_tour_alternative',
                'priority': 3,
                'description': 'PGA Tour dataset 2015-2020 with detailed statistics'
            }
        ]
        
        print("🏌️ DOWNLOADING GOLF DATASETS")
        print("=" * 50)
        
        successful_downloads = []
        failed_downloads = []
        
        for dataset in datasets:
            print(f"\n📋 Dataset {dataset['priority']}: {dataset['description']}")
            success, path = self.download_dataset(
                api, 
                dataset['ref'], 
                dataset['name']
            )
            
            if success:
                successful_downloads.append({
                    'name': dataset['name'],
                    'path': path,
                    'ref': dataset['ref']
                })
            else:
                failed_downloads.append(dataset['ref'])
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 50)
        print(f"✅ Successful: {len(successful_downloads)}")
        print(f"❌ Failed: {len(failed_downloads)}")
        
        if successful_downloads:
            print(f"\n📁 Downloaded datasets stored in:")
            for download in successful_downloads:
                print(f"   {download['name']}: {download['path']}")
        
        if failed_downloads:
            print(f"\n⚠️  Failed downloads:")
            for ref in failed_downloads:
                print(f"   {ref}")
        
        return len(successful_downloads) > 0
    
    def create_download_report(self):
        """Create a report of downloaded data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = f"""# Golf Data Download Report
Generated: {timestamp}

## Downloaded Datasets

"""
        # Scan kaggle directory for datasets
        if self.kaggle_dir.exists():
            for dataset_dir in self.kaggle_dir.iterdir():
                if dataset_dir.is_dir():
                    files = list(dataset_dir.glob('*'))
                    csv_files = [f for f in files if f.suffix.lower() == '.csv']
                    
                    report_content += f"### {dataset_dir.name}\n"
                    report_content += f"- **Location**: `{dataset_dir}`\n"
                    report_content += f"- **Total Files**: {len(files)}\n"
                    report_content += f"- **CSV Files**: {len(csv_files)}\n"
                    
                    if csv_files:
                        report_content += "- **CSV Files**:\n"
                        for csv_file in csv_files:
                            size_mb = csv_file.stat().st_size / (1024 * 1024)
                            report_content += f"  - `{csv_file.name}` ({size_mb:.1f} MB)\n"
                    
                    report_content += "\n"
        
        report_content += """
## Next Steps

1. **Explore Data Structure**: Run `python scripts/explore_golf_data.py`
2. **Map to Database Schema**: Identify which columns map to your database tables
3. **Create ETL Pipeline**: Transform and load data into your SQLite database
4. **Validate Data**: Check data quality and relationships

## Files to Examine

Look for these types of files in your downloaded datasets:
- Player information (names, countries, rankings)
- Tournament results (scores, positions, prize money)
- Round-by-round statistics (strokes gained, fairways hit, etc.)
- Course information (par, yardage, location)

"""
        
        # Save report
        report_file = self.data_dir / 'download_report.md'
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📋 Download report saved to: {report_file}")
        return report_file

def main():
    """Main execution function"""
    print("GOLF DATA DOWNLOADER")
    print("=" * 40)
    
    downloader = GolfDataDownloader()
    
    if downloader.download_recommended_datasets():
        downloader.create_download_report()
        print("\n🎉 Data download completed successfully!")
        print("\nNext steps:")
        print("1. Review the download_report.md file")
        print("2. Run the data exploration script")
        print("3. Start building your ETL pipeline")
    else:
        print("\n❌ Data download failed. Check your Kaggle setup.")

if __name__ == "__main__":
    main()