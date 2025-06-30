@echo off
REM Golf Database Project - Windows Development Environment Setup
echo 🏌️ Setting up Golf Database Development Environment
echo ==================================================

REM Create project directory structure
echo 📁 Creating project structure...
mkdir golf-database-project 2>nul
cd golf-database-project

REM Create subdirectories
mkdir data\raw 2>nul
mkdir data\processed 2>nul
mkdir data\kaggle 2>nul
mkdir src\api 2>nul
mkdir src\etl 2>nul
mkdir src\models 2>nul
mkdir src\nlp 2>nul
mkdir scripts\database 2>nul
mkdir scripts\deployment 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir docs 2>nul
mkdir logs 2>nul

echo ✅ Project structure created

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Setting up Python virtual environment...
python -m venv venv

echo 📋 To activate your virtual environment, run:
echo   venv\Scripts\activate
echo.

REM Create requirements.txt
echo 📦 Creating requirements.txt...
(
echo # Core dependencies
echo pandas^>=1.5.0
echo numpy^>=1.24.0
echo psycopg2-binary^>=2.9.0
echo sqlalchemy^>=2.0.0
echo.
echo # Web framework
echo flask^>=2.3.0
echo flask-sqlalchemy^>=3.0.0
echo flask-cors^>=4.0.0
echo.
echo # Data processing and analysis
echo matplotlib^>=3.7.0
echo seaborn^>=0.12.0
echo scikit-learn^>=1.3.0
echo.
echo # Natural Language Processing
echo spacy^>=3.6.0
echo openai^>=1.0.0
echo.
echo # API and data fetching
echo requests^>=2.31.0
echo kaggle^>=1.5.0
echo.
echo # Development tools
echo jupyter^>=1.0.0
echo python-dotenv^>=1.0.0
echo pytest^>=7.4.0
echo.
echo # Database migrations
echo alembic^>=1.11.0
echo.
echo # Data visualization ^(web^)
echo plotly^>=5.15.0
echo.
echo # Utilities
echo python-dateutil^>=2.8.0
echo tqdm^>=4.65.0
) > requirements.txt

echo ✅ Requirements file created

REM Create .env template
echo 🔐 Creating environment variables template...
(
echo # Database Configuration
echo DATABASE_URL=postgresql://username:password@localhost:5432/golf_database
echo POSTGRES_USER=golf_user
echo POSTGRES_PASSWORD=your_secure_password
echo POSTGRES_DB=golf_database
echo.
echo # API Keys
echo OPENAI_API_KEY=your_openai_api_key_here
echo KAGGLE_USERNAME=your_kaggle_username
echo KAGGLE_KEY=your_kaggle_key
echo.
echo # Flask Configuration
echo FLASK_APP=src/api/app.py
echo FLASK_ENV=development
echo SECRET_KEY=your_secret_key_here
echo.
echo # Data Sources
echo DATA_DIRECTORY=./data/kaggle
echo API_BASE_URL=https://api.yourgolfdata.com
echo.
echo # Logging
echo LOG_LEVEL=INFO
echo LOG_FILE=./logs/golf_database.log
) > .env.template

echo ✅ Environment template created - copy to .env and fill in your values

REM Create .gitignore
echo 🚫 Creating .gitignore...
(
echo # Environment variables
echo .env
echo *.env
echo.
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo venv/
echo env/
echo ENV/
echo.
echo # Data files
echo data/raw/*
echo data/processed/*
echo *.csv
echo *.json
echo *.xlsx
echo.
echo # Database
echo *.db
echo *.sqlite
echo.
echo # Jupyter Notebooks
echo .ipynb_checkpoints
echo.
echo # Logs
echo logs/
echo *.log
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # API Keys
echo kaggle.json
echo credentials.json
) > .gitignore

echo ✅ .gitignore created

REM Create main Flask application
echo 📄 Creating Flask API application...
(
echo """
echo Golf Database API - Main Flask Application
echo """
echo from flask import Flask, jsonify, request
echo from flask_cors import CORS
echo import os
echo from dotenv import load_dotenv
echo from datetime import datetime
echo.
echo # Load environment variables
echo load_dotenv^(^)
echo.
echo def create_app^(^):
echo     app = Flask^(__name__^)
echo     app.config['SECRET_KEY'] = os.getenv^('SECRET_KEY', 'dev-secret-key'^)
echo     
echo     # Enable CORS for frontend integration
echo     CORS^(app^)
echo     
echo     @app.route^('/'^)
echo     def home^(^):
echo         return jsonify^({
echo             "message": "Golf Database API",
echo             "version": "1.0.0",
echo             "status": "active",
echo             "timestamp": datetime.utcnow^(^).isoformat^(^)
echo         }^)
echo     
echo     @app.route^('/api/health'^)
echo     def health_check^(^):
echo         return jsonify^({"status": "healthy"}^)
echo     
echo     @app.route^('/api/players'^)
echo     def get_players^(^):
echo         # Placeholder for player data endpoint
echo         return jsonify^({
echo             "players": [],
echo             "message": "Players endpoint - connect to database"
echo         }^)
echo         
echo     @app.route^('/api/tournaments'^)
echo     def get_tournaments^(^):
echo         # Placeholder for tournament data endpoint
echo         return jsonify^({
echo             "tournaments": [],
echo             "message": "Tournaments endpoint - connect to database"
echo         }^)
echo     
echo     return app
echo.
echo if __name__ == '__main__':
echo     app = create_app^(^)
echo     print^("🏌️ Starting Golf Database API..."^)
echo     print^("📡 API will be available at: http://localhost:5000"^)
echo     app.run^(debug=True, host='0.0.0.0', port=5000^)
) > src\api\app.py

REM Create database models
echo 📊 Creating database models...
echo # Database models > src\models\__init__.py

(
echo """
echo SQLAlchemy models for Golf Database
echo """
echo from sqlalchemy import create_engine, Column, Integer, String, Date, Decimal, Boolean, ForeignKey, DateTime, Text
echo from sqlalchemy.ext.declarative import declarative_base
echo from sqlalchemy.orm import relationship, sessionmaker
echo from datetime import datetime
echo import os
echo.
echo Base = declarative_base^(^)
echo.
echo class Player^(Base^):
echo     __tablename__ = 'players'
echo     
echo     player_id = Column^(Integer, primary_key=True^)
echo     first_name = Column^(String^(50^), nullable=False^)
echo     last_name = Column^(String^(50^), nullable=False^)
echo     nationality = Column^(String^(3^)^)
echo     birth_date = Column^(Date^)
echo     turned_professional_date = Column^(Date^)
echo     height_cm = Column^(Integer^)
echo     world_ranking = Column^(Integer^)
echo     career_earnings = Column^(Decimal^(12,2^)^)
echo     created_at = Column^(DateTime, default=datetime.utcnow^)
echo     updated_at = Column^(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow^)
echo     
echo     # Relationships
echo     tournament_entries = relationship^("TournamentEntry", back_populates="player"^)
echo     
echo     @property
echo     def full_name^(self^):
echo         return f"{self.first_name} {self.last_name}"
echo     
echo     def __repr__^(self^):
echo         return f"^<Player^({self.full_name}^)^>"
echo.
echo class Course^(Base^):
echo     __tablename__ = 'courses'
echo     
echo     course_id = Column^(Integer, primary_key=True^)
echo     course_name = Column^(String^(100^), nullable=False^)
echo     location = Column^(String^(100^)^)
echo     country = Column^(String^(3^)^)
echo     par = Column^(Integer^)
echo     yardage = Column^(Integer^)
echo     course_rating = Column^(Decimal^(4,1^)^)
echo     slope_rating = Column^(Integer^)
echo     architect = Column^(String^(100^)^)
echo     established_year = Column^(Integer^)
echo     greens_type = Column^(String^(50^)^)
echo     created_at = Column^(DateTime, default=datetime.utcnow^)
echo     
echo     def __repr__^(self^):
echo         return f"^<Course^({self.course_name}^)^>"
echo.
echo class Tournament^(Base^):
echo     __tablename__ = 'tournaments'
echo     
echo     tournament_id = Column^(Integer, primary_key=True^)
echo     tournament_name = Column^(String^(100^), nullable=False^)
echo     course_id = Column^(Integer, ForeignKey^('courses.course_id'^)^)
echo     start_date = Column^(Date, nullable=False^)
echo     end_date = Column^(Date, nullable=False^)
echo     prize_money_usd = Column^(Integer^)
echo     field_size = Column^(Integer^)
echo     cut_line = Column^(Integer^)
echo     winning_score = Column^(Integer^)
echo     weather_conditions = Column^(Text^)
echo     created_at = Column^(DateTime, default=datetime.utcnow^)
echo     
echo     # Relationships
echo     course = relationship^("Course"^)
echo     entries = relationship^("TournamentEntry", back_populates="tournament"^)
echo     
echo     def __repr__^(self^):
echo         return f"^<Tournament^({self.tournament_name}^)^>"
echo.
echo class TournamentEntry^(Base^):
echo     __tablename__ = 'tournament_entries'
echo     
echo     entry_id = Column^(Integer, primary_key=True^)
echo     tournament_id = Column^(Integer, ForeignKey^('tournaments.tournament_id'^)^)
echo     player_id = Column^(Integer, ForeignKey^('players.player_id'^)^)
echo     final_position = Column^(Integer^)
echo     total_score = Column^(Integer^)
echo     prize_money = Column^(Decimal^(10,2^)^)
echo     made_cut = Column^(Boolean, default=False^)
echo     rounds_played = Column^(Integer^)
echo     
echo     # Relationships
echo     tournament = relationship^("Tournament", back_populates="entries"^)
echo     player = relationship^("Player", back_populates="tournament_entries"^)
echo     rounds = relationship^("Round"^)
echo.
echo class Round^(Base^):
echo     __tablename__ = 'rounds'
echo     
echo     round_id = Column^(Integer, primary_key=True^)
echo     entry_id = Column^(Integer, ForeignKey^('tournament_entries.entry_id'^)^)
echo     round_number = Column^(Integer, nullable=False^)
echo     score = Column^(Integer^)
echo     strokes_gained_total = Column^(Decimal^(5,2^)^)
echo     fairways_hit = Column^(Integer^)
echo     greens_in_regulation = Column^(Integer^)
echo     putts = Column^(Integer^)
echo     date_played = Column^(Date^)
) > src\models\models.py

REM Create database connection utility
echo 🔗 Creating database utilities...
(
echo """
echo Database connection and utility functions
echo """
echo from sqlalchemy import create_engine
echo from sqlalchemy.orm import sessionmaker
echo from src.models.models import Base
echo import os
echo from dotenv import load_dotenv
echo.
echo load_dotenv^(^)
echo.
echo class DatabaseManager:
echo     def __init__^(self^):
echo         self.database_url = os.getenv^('DATABASE_URL'^)
echo         if not self.database_url:
echo             # Fallback to SQLite for development
echo             self.database_url = 'sqlite:///golf_database.db'
echo             print^("⚠️  Using SQLite fallback. Set DATABASE_URL for PostgreSQL."^)
echo         
echo         self.engine = create_engine^(self.database_url^)
echo         self.SessionLocal = sessionmaker^(bind=self.engine^)
echo     
echo     def create_tables^(self^):
echo         """Create all database tables"""
echo         Base.metadata.create_all^(bind=self.engine^)
echo         print^("✅ Database tables created"^)
echo     
echo     def get_session^(self^):
echo         """Get database session"""
echo         return self.SessionLocal^(^)
echo.
echo # Global database manager instance
echo db_manager = DatabaseManager^(^)
) > src\models\database.py

REM Create data loading script
echo 📥 Creating data loading utilities...
(
echo """
echo Data loading and ETL utilities
echo """
echo import pandas as pd
echo import os
echo from kaggle.api.kaggle_api_extended import KaggleApi
echo from dotenv import load_dotenv
echo.
echo load_dotenv^(^)
echo.
echo class DataLoader:
echo     def __init__^(self^):
echo         self.data_dir = './data'
echo         self.kaggle_dir = './data/kaggle'
echo         
echo     def setup_kaggle^(self^):
echo         """Setup Kaggle API credentials"""
echo         api = KaggleApi^(^)
echo         api.authenticate^(^)
echo         return api
echo         
echo     def download_golf_datasets^(self^):
echo         """Download popular golf datasets from Kaggle"""
echo         api = self.setup_kaggle^(^)
echo         
echo         datasets = [
echo             'bradklassen/pga-tour-20102018-data',
echo             'jmpark746/pga-tour-data-2010-2018'
echo         ]
echo         
echo         for dataset in datasets:
echo             try:
echo                 print^(f"📥 Downloading {dataset}..."^)
echo                 api.dataset_download_files^(dataset, path=self.kaggle_dir, unzip=True^)
echo                 print^(f"✅ Downloaded {dataset}"^)
echo             except Exception as e:
echo                 print^(f"❌ Error downloading {dataset}: {e}"^)
echo                 
echo     def load_csv_data^(self, filename^):
echo         """Load CSV data with error handling"""
echo         try:
echo             filepath = os.path.join^(self.data_dir, filename^)
echo             df = pd.read_csv^(filepath^)
echo             print^(f"✅ Loaded {filename}: {len^(df^)} rows"^)
echo             return df
echo         except Exception as e:
echo             print^(f"❌ Error loading {filename}: {e}"^)
echo             return None
) > src\etl\data_loader.py

REM Create setup instructions
echo 📋 Creating setup instructions...
(
echo # Golf Database Project Setup Instructions
echo.
echo ## Quick Start
echo.
echo 1. **Activate Virtual Environment:**
echo    ```
echo    venv\Scripts\activate
echo    ```
echo.
echo 2. **Install Dependencies:**
echo    ```
echo    pip install -r requirements.txt
echo    ```
echo.
echo 3. **Setup Environment Variables:**
echo    - Copy `.env.template` to `.env`
echo    - Fill in your database credentials and API keys
echo.
echo 4. **Install PostgreSQL ^(Optional^):**
echo    - Download from https://postgresql.org/download/windows/
echo    - Or use SQLite ^(default fallback^)
echo.
echo 5. **Run the API:**
echo    ```
echo    python src\api\app.py
echo    ```
echo.
echo ## Project Structure
echo.
echo - `src/api/` - Flask web API
echo - `src/models/` - Database models
echo - `src/etl/` - Data loading and processing
echo - `data/` - Data storage ^(raw, processed, kaggle^)
echo - `tests/` - Unit and integration tests
echo.
echo ## Next Steps
echo.
echo 1. Set up your database connection
echo 2. Download golf data from Kaggle
echo 3. Load data into your database
echo 4. Build analysis notebooks in Jupyter
echo 5. Develop additional API endpoints
echo.
echo ## Useful Commands
echo.
echo ```bash
echo # Install development dependencies
echo pip install -e .
echo.
echo # Run tests
echo pytest tests/
echo.
echo # Start Jupyter
echo jupyter notebook
echo.
echo # Database migrations
echo alembic init alembic
echo alembic revision --autogenerate -m "Initial migration"
echo alembic upgrade head
echo ```
) > README.md

REM Create simple installer batch file
echo 🚀 Creating installation helper...
(
echo @echo off
echo echo 🏌️ Golf Database - Quick Install
echo echo ==============================
echo.
echo echo Activating virtual environment...
echo call venv\Scripts\activate
echo.
echo echo Installing Python packages...
echo pip install -r requirements.txt
echo.
echo echo 🎯 Installation complete!
echo echo.
echo echo Next steps:
echo echo 1. Copy .env.template to .env and configure
echo echo 2. Run: python src\api\app.py
echo echo 3. Visit: http://localhost:5000
echo.
echo pause
) > install.bat

echo ✅ All files created successfully!
echo.
echo 🎯 Next Steps:
echo 1. Run: install.bat
echo 2. Configure your .env file
echo 3. Start developing!
echo.
echo 📡 Your API will be available at: http://localhost:5000
echo.
pause