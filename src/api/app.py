"""
Golf Database API - Main Flask Application
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add the src directory to Python path so we can import our modules
project_root = Path(__file__).parent.parent  # Go up one level from src/api to project root
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Also try adding the project root to the path
sys.path.insert(0, str(project_root))

print(f"🔍 Project root: {project_root}")
print(f"🔍 Src path: {src_path}")
print(f"🔍 Python paths: {sys.path[:3]}")

# Import database modules
db_manager = None
Player = Course = Tournament = TournamentEntry = Round = None

try:
    from models.database import db_manager
    from models.models import Player, Course, Tournament, TournamentEntry, Round
    print("✅ Successfully imported database modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure your database modules are properly set up")
    print("Continuing without database connection...")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Enable CORS for frontend integration
    CORS(app)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "Golf Database API",
            "version": "1.0.0",
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/health')
    def health_check():
        if db_manager is None:
            return jsonify({
                "status": "unhealthy",
                "database_connected": False,
                "error": "Database modules not imported"
            }), 500
            
        try:
            # Test database connection
            session = db_manager.get_session()
            player_count = session.query(Player).count()
            session.close()
            
            return jsonify({
                "status": "healthy",
                "database_connected": True,
                "player_count": player_count
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/players')
    def get_players():
        if db_manager is None or Player is None:
            return jsonify({
                "players": [],
                "error": "Database modules not available",
                "message": "Database connection not established"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Query all players from database
            players = session.query(Player).all()
            
            # Convert players to dictionary format
            players_data = []
            for player in players:
                player_dict = {
                    "player_id": player.player_id,
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "full_name": player.full_name,
                    "nationality": player.nationality,
                    "birth_date": player.birth_date.isoformat() if player.birth_date else None,
                    "turned_professional_date": player.turned_professional_date.isoformat() if player.turned_professional_date else None,
                    "height_cm": player.height_cm,
                    "world_ranking": player.world_ranking,
                    "career_earnings": float(player.career_earnings) if player.career_earnings else None
                }
                players_data.append(player_dict)
            
            session.close()
            
            return jsonify({
                "players": players_data,
                "count": len(players_data),
                "message": f"Found {len(players_data)} players"
            })
            
        except Exception as e:
            return jsonify({
                "players": [],
                "error": str(e),
                "message": "Failed to retrieve players"
            }), 500
        
    @app.route('/api/tournaments')
    def get_tournaments():
        if db_manager is None or Tournament is None or Course is None:
            return jsonify({
                "tournaments": [],
                "error": "Database modules not available",
                "message": "Database connection not established"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Query all tournaments with course information
            tournaments = session.query(Tournament).join(Course).all()
            
            # Convert tournaments to dictionary format
            tournaments_data = []
            for tournament in tournaments:
                tournament_dict = {
                    "tournament_id": tournament.tournament_id,
                    "tournament_name": tournament.tournament_name,
                    "course_name": tournament.course.course_name,
                    "location": tournament.course.location,
                    "country": tournament.course.country,
                    "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
                    "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
                    "prize_money_usd": float(tournament.prize_money_usd) if tournament.prize_money_usd else None,
                    "field_size": tournament.field_size,
                    "cut_line": tournament.cut_line,
                    "winning_score": tournament.winning_score
                }
                tournaments_data.append(tournament_dict)
            
            session.close()
            
            return jsonify({
                "tournaments": tournaments_data,
                "count": len(tournaments_data),
                "message": f"Found {len(tournaments_data)} tournaments"
            })
            
        except Exception as e:
            return jsonify({
                "tournaments": [],
                "error": str(e),
                "message": "Failed to retrieve tournaments"
            }), 500
    
    @app.route('/api/courses')
    def get_courses():
        if db_manager is None or Course is None:
            return jsonify({
                "courses": [],
                "error": "Database modules not available",
                "message": "Database connection not established"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Query all courses from database
            courses = session.query(Course).all()
            
            # Convert courses to dictionary format
            courses_data = []
            for course in courses:
                course_dict = {
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                    "location": course.location,
                    "country": course.country,
                    "par": course.par,
                    "yardage": course.yardage,
                    "course_rating": float(course.course_rating) if course.course_rating else None,
                    "slope_rating": course.slope_rating,
                    "architect": course.architect,
                    "established_year": course.established_year,
                    "greens_type": course.greens_type
                }
                courses_data.append(course_dict)
            
            session.close()
            
            return jsonify({
                "courses": courses_data,
                "count": len(courses_data),
                "message": f"Found {len(courses_data)} courses"
            })
            
        except Exception as e:
            return jsonify({
                "courses": [],
                "error": str(e),
                "message": "Failed to retrieve courses"
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🏌️ Starting Golf Database API...")
    print("📡 API will be available at: http://localhost:5000")
    
    if db_manager:
        print("🔗 Database URL:", db_manager.database_url)
    else:
        print("⚠️  Database not connected - check your models directory")
        
    app.run(debug=True, host='0.0.0.0', port=5000)