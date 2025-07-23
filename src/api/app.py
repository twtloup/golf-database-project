"""
Golf Database Website - Multi-section interface for exploring golf data
"""
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent  # Go up from src/api/ to project root
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))
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
    print("Continuing without database connection...")

def create_app():
    # Create Flask app with static folder configuration
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Static file serving route (this should work automatically, but adding explicitly)
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Main website route - will serve our homepage
    @app.route('/')
    def home():
        return render_template_string(HOMEPAGE_TEMPLATE)
    
    # Individual section routes
    @app.route('/players')
    def players_page():
        return render_template_string(PLAYERS_PAGE_TEMPLATE)
    
    @app.route('/tournaments')
    def tournaments_page():
        return render_template_string(TOURNAMENTS_PAGE_TEMPLATE)
    
    @app.route('/statistics')
    def statistics_page():
        return render_template_string(STATISTICS_PAGE_TEMPLATE)
    
    @app.route('/courses')
    def courses_page():
        return render_template_string(COURSES_PAGE_TEMPLATE)
    
    # API Routes (keeping your existing ones with improvements)
    @app.route('/api/health')
    def health_check():
        if db_manager is None:
            return jsonify({
                "status": "unhealthy",
                "database_connected": False,
                "error": "Database modules not imported"
            }), 500
            
        try:
            session = db_manager.get_session()
            player_count = session.query(Player).count()
            
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
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            
            # Get query parameters for filtering/pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '').strip()
            
            # Build query
            query = session.query(Player)
            
            if search:
                query = query.filter(
                    (Player.first_name.ilike(f'%{search}%')) |
                    (Player.last_name.ilike(f'%{search}%'))
                )
            
            # Get total count
            total_players = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            players = query.order_by(Player.last_name, Player.first_name).offset(offset).limit(per_page).all()
            
            # Convert to dict format
            players_data = []
            for player in players:
                player_dict = {
                    "player_id": player.player_id,
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "full_name": player.full_name,
                    "nationality": player.nationality,
                    "birth_date": player.birth_date.isoformat() if player.birth_date else None,
                    "world_ranking": player.world_ranking,
                    "career_earnings": float(player.career_earnings) if player.career_earnings else None
                }
                players_data.append(player_dict)
            
            session.close()
            
            return jsonify({
                "players": players_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_players,
                    "pages": (total_players + per_page - 1) // per_page
                },
                "search": search,
                "message": f"Found {len(players_data)} players"
            })
            
        except Exception as e:
            return jsonify({
                "players": [],
                "error": str(e)
            }), 500
    
    @app.route('/api/tournaments')
    def get_tournaments():
        if db_manager is None:
            return jsonify({
                "tournaments": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            from sqlalchemy import text
            
            # Get parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '').strip()
            year = request.args.get('year', type=int)
            
            # Build base query
            base_query = """
                SELECT 
                    t.tournament_id,
                    t.tournament_name,
                    t.tournament_date,
                    t.purse_millions,
                    t.season,
                    c.course_name,
                    c.location,
                    COUNT(tr.result_id) as player_count
                FROM tournaments_enhanced t
                LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
                LEFT JOIN tournament_results tr ON t.tournament_id = tr.tournament_id
                WHERE 1=1
            """
            
            params = {}
            
            if search:
                base_query += " AND t.tournament_name LIKE :search"
                params['search'] = f'%{search}%'
            
            if year:
                base_query += " AND t.season = :year"
                params['year'] = year
                
            base_query += """
                GROUP BY t.tournament_id, t.tournament_name, t.tournament_date, 
                         t.purse_millions, t.season, c.course_name, c.location
                ORDER BY t.tournament_date DESC
            """
            
            # Get total count
            count_query = base_query.replace("SELECT t.tournament_id", "SELECT COUNT(DISTINCT t.tournament_id)")
            count_query = count_query.split("GROUP BY")[0]  # Remove GROUP BY for count
            total_count = session.execute(text(count_query), params).scalar()
            
            # Apply pagination
            offset = (page - 1) * per_page
            paginated_query = base_query + f" LIMIT {per_page} OFFSET {offset}"
            
            result = session.execute(text(paginated_query), params)
            tournaments_data = []
            
            for row in result:
                tournament_dict = {
                    "tournament_id": row[0],
                    "tournament_name": row[1],
                    "tournament_date": row[2],
                    "purse_millions": float(row[3]) if row[3] else None,
                    "season": row[4],
                    "course_name": row[5],
                    "course_location": row[6],
                    "player_count": row[7]
                }
                tournaments_data.append(tournament_dict)
            
            session.close()
            
            return jsonify({
                "tournaments": tournaments_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page
                },
                "filters": {
                    "search": search,
                    "year": year
                }
            })
            
        except Exception as e:
            return jsonify({
                "tournaments": [],
                "error": str(e)
            }), 500
    
    @app.route('/api/tournament-results')
    def get_tournament_results():
        if db_manager is None:
            return jsonify({
                "results": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            from sqlalchemy import text
            
            # Get parameters
            tournament_id = request.args.get('tournament_id', type=int)
            player_id = request.args.get('player_id', type=int)
            limit = request.args.get('limit', 50, type=int)
            
            query_str = """
                SELECT 
                    tr.result_id,
                    p.first_name || ' ' || p.last_name as player_name,
                    t.tournament_name,
                    t.tournament_date,
                    c.course_name,
                    tr.position_numeric,
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
            
            if tournament_id:
                query_str += " AND tr.tournament_id = :tournament_id"
                params['tournament_id'] = tournament_id
            
            if player_id:
                query_str += " AND tr.player_id = :player_id"
                params['player_id'] = player_id
            
            query_str += " ORDER BY tr.position_numeric ASC, tr.total_strokes ASC"
            query_str += f" LIMIT {limit}"
            
            result = session.execute(text(query_str), params)
            results_data = []
            
            for row in result:
                result_dict = {
                    "result_id": row[0],
                    "player_name": row[1],
                    "tournament_name": row[2],
                    "tournament_date": row[3],
                    "course_name": row[4],
                    "position": row[5],
                    "total_strokes": row[6],
                    "made_cut": bool(row[7]) if row[7] is not None else None,
                    "strokes_gained_total": float(row[8]) if row[8] is not None else None,
                    "strokes_gained_putting": float(row[9]) if row[9] is not None else None,
                    "strokes_gained_approach": float(row[10]) if row[10] is not None else None,
                    "strokes_gained_off_tee": float(row[11]) if row[11] is not None else None
                }
                results_data.append(result_dict)
            
            session.close()
            
            return jsonify({
                "results": results_data,
                "count": len(results_data),
                "filters": {
                    "tournament_id": tournament_id,
                    "player_id": player_id
                }
            })
            
        except Exception as e:
            return jsonify({
                "results": [],
                "error": str(e)
            }), 500
    
    @app.route('/api/courses')
    def get_courses():
        if db_manager is None:
            return jsonify({
                "courses": [],
                "error": "Database modules not available"
            }), 500
            
        try:
            session = db_manager.get_session()
            from sqlalchemy import text
            
            courses_query = text("""
                SELECT 
                    c.course_id, 
                    c.course_name, 
                    c.location, 
                    c.total_par,
                    COUNT(t.tournament_id) as tournament_count
                FROM courses_enhanced c
                LEFT JOIN tournaments_enhanced t ON c.course_id = t.course_id
                GROUP BY c.course_id, c.course_name, c.location, c.total_par
                ORDER BY tournament_count DESC, c.course_name
            """)
            
            result = session.execute(courses_query)
            courses_data = []
            
            for row in result:
                course_dict = {
                    "course_id": row[0],
                    "course_name": row[1],
                    "location": row[2],
                    "total_par": row[3],
                    "tournament_count": row[4]
                }
                courses_data.append(course_dict)
            
            session.close()
            
            return jsonify({
                "courses": courses_data,
                "count": len(courses_data)
            })
            
        except Exception as e:
            return jsonify({
                "courses": [],
                "error": str(e)
            }), 500
    
    return app

# HTML Templates for different pages (keeping the same templates as before)
HOMEPAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Golf Database - Explore PGA Tour Data</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h2>🏌️ Golf Database</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link active">Home</a></li>
                <li><a href="/players" class="nav-link">Players</a></li>
                <li><a href="/tournaments" class="nav-link">Tournaments</a></li>
                <li><a href="/courses" class="nav-link">Courses</a></li>
                <li><a href="/statistics" class="nav-link">Statistics</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        <section class="hero">
            <div class="hero-content">
                <h1>Explore Professional Golf Data</h1>
                <p>Dive deep into PGA Tour statistics, player performances, and tournament results from 2014-2022</p>
                <div class="hero-stats">
                    <div class="stat-card">
                        <h3>748</h3>
                        <p>PGA Tour Players</p>
                    </div>
                    <div class="stat-card">
                        <h3>333</h3>
                        <p>Tournaments</p>
                    </div>
                    <div class="stat-card">
                        <h3>36K+</h3>
                        <p>Performance Records</p>
                    </div>
                    <div class="stat-card">
                        <h3>92</h3>
                        <p>Golf Courses</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="features">
            <div class="container">
                <h2>Explore Golf Data</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">👥</div>
                        <h3>Player Profiles</h3>
                        <p>Browse detailed profiles of 748 PGA Tour players with career statistics and performance data</p>
                        <a href="/players" class="btn btn-primary">View Players</a>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">🏆</div>
                        <h3>Tournament Results</h3>
                        <p>Explore results from 333 tournaments including majors, with detailed leaderboards and scoring</p>
                        <a href="/tournaments" class="btn btn-primary">View Tournaments</a>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">🏌️</div>
                        <h3>Golf Courses</h3>
                        <p>Discover information about the courses that host PGA Tour events and their characteristics</p>
                        <a href="/courses" class="btn btn-primary">View Courses</a>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Advanced Statistics</h3>
                        <p>Deep dive into strokes gained data, performance trends, and advanced golf analytics</p>
                        <a href="/statistics" class="btn btn-primary">View Statistics</a>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Golf Database. Data from PGA Tour 2014-2022.</p>
        </div>
    </footer>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

PLAYERS_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Players - Golf Database</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h2>🏌️ Golf Database</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Home</a></li>
                <li><a href="/players" class="nav-link active">Players</a></li>
                <li><a href="/tournaments" class="nav-link">Tournaments</a></li>
                <li><a href="/courses" class="nav-link">Courses</a></li>
                <li><a href="/statistics" class="nav-link">Statistics</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        <div class="container">
            <div class="page-header">
                <h1>PGA Tour Players</h1>
                <p>Browse and search through 748 professional golfers</p>
            </div>
            
            <div class="filters-section">
                <div class="search-box">
                    <input type="text" id="playerSearch" placeholder="Search players by name...">
                    <button id="searchBtn">Search</button>
                </div>
            </div>
            
            <div class="players-grid" id="playersGrid">
                <div class="loading">Loading players...</div>
            </div>
            
            <div class="pagination" id="pagination"></div>
        </div>
    </main>

    <script src="{{ url_for('static', filename='js/players.js') }}"></script>
</body>
</html>
'''

TOURNAMENTS_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournaments - Golf Database</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h2>🏌️ Golf Database</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Home</a></li>
                <li><a href="/players" class="nav-link">Players</a></li>
                <li><a href="/tournaments" class="nav-link active">Tournaments</a></li>
                <li><a href="/courses" class="nav-link">Courses</a></li>
                <li><a href="/statistics" class="nav-link">Statistics</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        <div class="container">
            <div class="page-header">
                <h1>PGA Tour Tournaments</h1>
                <p>Explore 333 tournaments from 2014-2022</p>
            </div>
            
            <div class="filters-section">
                <div class="filter-group">
                    <input type="text" id="tournamentSearch" placeholder="Search tournaments...">
                    <select id="yearFilter">
                        <option value="">All Years</option>
                        <option value="2022">2022</option>
                        <option value="2021">2021</option>
                        <option value="2020">2020</option>
                        <option value="2019">2019</option>
                        <option value="2018">2018</option>
                        <option value="2017">2017</option>
                        <option value="2016">2016</option>
                        <option value="2015">2015</option>
                        <option value="2014">2014</option>
                    </select>
                    <button id="applyFilters">Apply Filters</button>
                </div>
            </div>
            
            <div class="tournaments-list" id="tournamentsList">
                <div class="loading">Loading tournaments...</div>
            </div>
            
            <div class="pagination" id="pagination"></div>
        </div>
    </main>

    <script src="{{ url_for('static', filename='js/tournaments.js') }}"></script>
</body>
</html>
'''

COURSES_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courses - Golf Database</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h2>🏌️ Golf Database</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Home</a></li>
                <li><a href="/players" class="nav-link">Players</a></li>
                <li><a href="/tournaments" class="nav-link">Tournaments</a></li>
                <li><a href="/courses" class="nav-link active">Courses</a></li>
                <li><a href="/statistics" class="nav-link">Statistics</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        <div class="container">
            <div class="page-header">
                <h1>Golf Courses</h1>
                <p>Discover the courses that host PGA Tour events</p>
            </div>
            
            <div class="courses-grid" id="coursesGrid">
                <div class="loading">Loading courses...</div>
            </div>
        </div>
    </main>

    <script src="{{ url_for('static', filename='js/courses.js') }}"></script>
</body>
</html>
'''

STATISTICS_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Statistics - Golf Database</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h2>🏌️ Golf Database</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Home</a></li>
                <li><a href="/players" class="nav-link">Players</a></li>
                <li><a href="/tournaments" class="nav-link">Tournaments</a></li>
                <li><a href="/courses" class="nav-link">Courses</a></li>
                <li><a href="/statistics" class="nav-link active">Statistics</a></li>
            </ul>
        </div>
    </nav>

    <main class="main-content">
        <div class="container">
            <div class="page-header">
                <h1>Golf Statistics</h1>
                <p>Advanced analytics and performance insights</p>
            </div>
            
            <div class="stats-dashboard">
                <div class="stats-section">
                    <h2>Strokes Gained Analysis</h2>
                    <div class="chart-container" id="strokesGainedChart">
                        <div class="loading">Loading chart...</div>
                    </div>
                </div>
                
                <div class="stats-section">
                    <h2>Performance Leaders</h2>
                    <div class="leaderboards" id="leaderboards">
                        <div class="loading">Loading leaderboards...</div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script src="{{ url_for('static', filename='js/statistics.js') }}"></script>
</body>
</html>
'''

if __name__ == '__main__':
    app = create_app()
    print("🏌️ Starting Golf Database Website...")
    print("🌐 Homepage: http://localhost:5000")
    print("📄 Pages available:")
    print("   • Players: http://localhost:5000/players")
    print("   • Tournaments: http://localhost:5000/tournaments")
    print("   • Courses: http://localhost:5000/courses")
    print("   • Statistics: http://localhost:5000/statistics")
    
    if db_manager:
        print("🔗 Database connected:", db_manager.database_url)
    else:
        print("⚠️  Database not connected")
        
    app.run(debug=True, host='0.0.0.0', port=5000)