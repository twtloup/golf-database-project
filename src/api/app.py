"""
Golf Database API - Updated to serve enhanced tournament and course data
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
            "message": "Golf Database API - Enhanced Edition",
            "version": "2.0.0",
            "status": "active",
            "timestamp": datetime.utcnow().isoformat(),
            "data_loaded": "747 players, 280 courses, 333 tournaments, 36,864 results"
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
            
            # Check both old and new tables
            player_count = session.query(Player).count()
            
            # Check enhanced tables
            try:
                from sqlalchemy import text
                tournament_count = session.execute(text("SELECT COUNT(*) FROM tournaments_enhanced")).scalar()
                course_count = session.execute(text("SELECT COUNT(*) FROM courses_enhanced")).scalar()
                result_count = session.execute(text("SELECT COUNT(*) FROM tournament_results")).scalar()
                yearly_count = session.execute(text("SELECT COUNT(*) FROM player_yearly_stats")).scalar()
            except:
                tournament_count = course_count = result_count = yearly_count = 0
            
            session.close()
            
            return jsonify({
                "status": "healthy",
                "database_connected": True,
                "data_summary": {
                    "players": player_count,
                    "tournaments": tournament_count,
                    "courses": course_count,
                    "tournament_results": result_count,
                    "yearly_stats": yearly_count
                }
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
            players = session.query(Player).limit(50).all()  # Limit to first 50 for performance
            
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
            
            total_players = session.query(Player).count()
            session.close()
            
            return jsonify({
                "players": players_data,
                "count": len(players_data),
                "total_players": total_players,
                "message": f"Showing first {len(players_data)} of {total_players} players"
            })
            
        except Exception as e:
            return jsonify({
                "players": [],
                "error": str(e),
                "message": "Failed to retrieve players"
            }), 500
    
    @app.route('/api/courses')
    def get_courses():
        """Get courses from the enhanced courses table"""
        if db_manager is None:
            return jsonify({
                "courses": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Query courses from enhanced table using proper SQLAlchemy text
            from sqlalchemy import text
            
            courses_query = text("""
                SELECT course_id, course_name, location, total_par 
                FROM courses_enhanced 
                ORDER BY course_name 
                LIMIT 50
            """)
            
            result = session.execute(courses_query)
            courses_data = []
            
            for row in result:
                course_dict = {
                    "course_id": row[0],
                    "course_name": row[1],
                    "location": row[2],
                    "total_par": row[3]
                }
                courses_data.append(course_dict)
            
            # Get total count
            total_count_query = text("SELECT COUNT(*) FROM courses_enhanced")
            total_count = session.execute(total_count_query).scalar()
            
            session.close()
            
            return jsonify({
                "courses": courses_data,
                "count": len(courses_data),
                "total_courses": total_count,
                "message": f"Showing first {len(courses_data)} of {total_count} courses from enhanced data"
            })
            
        except Exception as e:
            return jsonify({
                "courses": [],
                "error": str(e),
                "message": "Failed to retrieve courses from enhanced table"
            }), 500
    
    @app.route('/api/tournaments')
    def get_tournaments():
        """Get tournaments from the enhanced tournaments table"""
        if db_manager is None:
            return jsonify({
                "tournaments": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Query tournaments from enhanced table with proper SQLAlchemy text
            from sqlalchemy import text
            
            tournaments_query = text("""
                SELECT 
                    t.tournament_id,
                    t.tournament_name,
                    t.tournament_date,
                    t.purse_millions,
                    t.season,
                    t.has_cut,
                    c.course_name,
                    c.location
                FROM tournaments_enhanced t
                LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
                ORDER BY t.tournament_date DESC
                LIMIT 50
            """)
            
            result = session.execute(tournaments_query)
            tournaments_data = []
            
            for row in result:
                tournament_dict = {
                    "tournament_id": row[0],
                    "tournament_name": row[1],
                    "tournament_date": row[2] if row[2] else None,  # Already a string from SQLite
                    "purse_millions": float(row[3]) if row[3] else None,
                    "season": row[4],
                    "has_cut": bool(row[5]) if row[5] is not None else None,
                    "course_name": row[6],
                    "course_location": row[7]
                }
                tournaments_data.append(tournament_dict)
            
            # Get total count
            total_count_query = text("SELECT COUNT(*) FROM tournaments_enhanced")
            total_count = session.execute(total_count_query).scalar()
            
            session.close()
            
            return jsonify({
                "tournaments": tournaments_data,
                "count": len(tournaments_data),
                "total_tournaments": total_count,
                "message": f"Showing first {len(tournaments_data)} of {total_count} tournaments from enhanced data"
            })
            
        except Exception as e:
            return jsonify({
                "tournaments": [],
                "error": str(e),
                "message": "Failed to retrieve tournaments from enhanced table"
            }), 500
    
    @app.route('/api/tournament-results')
    def get_tournament_results():
        """Get tournament results data"""
        if db_manager is None:
            return jsonify({
                "results": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            from sqlalchemy import text
            
            # Get query parameters
            limit = request.args.get('limit', 50, type=int)
            player_name = request.args.get('player')
            tournament_name = request.args.get('tournament')
            
            # Build query
            query_str = """
                SELECT 
                    tr.result_id,
                    p.first_name || ' ' || p.last_name as player_name,
                    t.tournament_name,
                    t.tournament_date,
                    c.course_name,
                    tr.final_position,
                    tr.total_strokes,
                    tr.made_cut,
                    tr.sg_total,
                    tr.sg_putting,
                    tr.sg_approach,
                    tr.sg_off_the_tee
                FROM tournament_results tr
                JOIN players p ON tr.player_id = p.player_id
                JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
                LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
                WHERE 1=1
            """
            
            params = {}
            
            if player_name:
                query_str += " AND (p.first_name LIKE :player_search OR p.last_name LIKE :player_search OR (p.first_name || ' ' || p.last_name) LIKE :player_search)"
                params['player_search'] = f"%{player_name}%"
            
            if tournament_name:
                query_str += " AND t.tournament_name LIKE :tournament_search"
                params['tournament_search'] = f"%{tournament_name}%"
            
            query_str += " ORDER BY t.tournament_date DESC, tr.position_numeric ASC"
            query_str += f" LIMIT {limit}"
            
            result = session.execute(text(query_str), params)
            results_data = []
            
            for row in result:
                result_dict = {
                    "result_id": row[0],
                    "player_name": row[1],
                    "tournament_name": row[2],
                    "tournament_date": row[3] if row[3] else None,  # Already a string
                    "course_name": row[4],
                    "final_position": row[5],
                    "total_strokes": row[6],
                    "made_cut": bool(row[7]) if row[7] is not None else None,
                    "strokes_gained_total": float(row[8]) if row[8] is not None else None,
                    "strokes_gained_putting": float(row[9]) if row[9] is not None else None,
                    "strokes_gained_approach": float(row[10]) if row[10] is not None else None,
                    "strokes_gained_off_tee": float(row[11]) if row[11] is not None else None
                }
                results_data.append(result_dict)
            
            # Get total count
            total_count = session.execute(text("SELECT COUNT(*) FROM tournament_results")).scalar()
            
            session.close()
            
            return jsonify({
                "results": results_data,
                "count": len(results_data),
                "total_results": total_count,
                "filters": {
                    "player": player_name,
                    "tournament": tournament_name,
                    "limit": limit
                },
                "message": f"Showing {len(results_data)} tournament results"
            })
            
        except Exception as e:
            return jsonify({
                "results": [],
                "error": str(e),
                "message": "Failed to retrieve tournament results"
            }), 500
    
    @app.route('/api/search')
    def search_data():
        """Basic search across players, tournaments, and courses"""
        if db_manager is None:
            return jsonify({
                "results": [],
                "error": "Database not available"
            }), 500
        
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({
                "results": [],
                "message": "Please provide a search term using ?q=search_term"
            })
        
        try:
            session = db_manager.get_session()
            from sqlalchemy import text
            
            results = {
                "players": [],
                "tournaments": [],
                "courses": []
            }
            
            # Search players
            player_query = text("""
                SELECT player_id, first_name, last_name, nationality
                FROM players 
                WHERE first_name LIKE :search OR last_name LIKE :search
                LIMIT 10
            """)
            search_pattern = f"%{search_term}%"
            player_results = session.execute(player_query, {"search": search_pattern})
            
            for row in player_results:
                results["players"].append({
                    "player_id": row[0],
                    "name": f"{row[1]} {row[2]}",
                    "nationality": row[3]
                })
            
            # Search tournaments
            tournament_query = text("""
                SELECT tournament_id, tournament_name, tournament_date, season
                FROM tournaments_enhanced 
                WHERE tournament_name LIKE :search
                LIMIT 10
            """)
            tournament_results = session.execute(tournament_query, {"search": search_pattern})
            
            for row in tournament_results:
                results["tournaments"].append({
                    "tournament_id": row[0],
                    "tournament_name": row[1],
                    "tournament_date": row[2] if row[2] else None,  # Already a string, no .isoformat() needed
                    "season": row[3]
                })
            
            # Search courses
            course_query = text("""
                SELECT course_id, course_name, location
                FROM courses_enhanced 
                WHERE course_name LIKE :search1 OR location LIKE :search2
                LIMIT 10
            """)
            course_results = session.execute(course_query, {"search1": search_pattern, "search2": search_pattern})
            
            for row in course_results:
                results["courses"].append({
                    "course_id": row[0],
                    "course_name": row[1],
                    "location": row[2]
                })
            
            session.close()
            
            total_results = len(results["players"]) + len(results["tournaments"]) + len(results["courses"])
            
            return jsonify({
                "search_term": search_term,
                "results": results,
                "total_found": total_results,
                "message": f"Found {total_results} results for '{search_term}'"
            })
            
        except Exception as e:
            return jsonify({
                "results": [],
                "error": str(e),
                "message": "Search failed"
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🏌️ Starting Enhanced Golf Database API...")
    print("📡 API will be available at: http://localhost:5000")
    print("🎯 New endpoints:")
    print("   • /api/courses - Real course data")
    print("   • /api/tournaments - Real tournament data") 
    print("   • /api/tournament-results - Individual results")
    print("   • /api/search?q=search_term - Search everything")
    
    if db_manager:
        print("🔗 Database URL:", db_manager.database_url)
    else:
        print("⚠️  Database not connected - check your models directory")
        
    app.run(debug=True, host='0.0.0.0', port=5000)