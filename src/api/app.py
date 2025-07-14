"""
Golf Database API - Updated to serve enhanced tournament and course data with Natural Language Interface
"""
from flask import Flask, jsonify, request, render_template_string
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


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Golf Database - Natural Language Query</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .query-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        .query-input-container {
            position: relative;
            margin-bottom: 20px;
        }

        .query-input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            outline: none;
            transition: border-color 0.3s;
        }

        .query-input:focus {
            border-color: #2a5298;
        }

        .query-button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .query-button:hover {
            transform: translateY(-2px);
        }

        .query-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .examples {
            margin-top: 20px;
        }

        .examples h3 {
            color: #2a5298;
            margin-bottom: 15px;
        }

        .example-queries {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .example-query {
            background: #f5f5f5;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 0.9em;
        }

        .example-query:hover {
            background: #e0e0e0;
        }

        .results-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            min-height: 200px;
        }

        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }

        .error {
            background: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .query-interpretation {
            background: #f0f8ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #2a5298;
        }

        .query-interpretation h4 {
            color: #2a5298;
            margin-bottom: 10px;
        }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .results-table th,
        .results-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .results-table th {
            background: #f5f5f5;
            font-weight: 600;
            color: #2a5298;
        }

        .results-table tr:hover {
            background: #f9f9f9;
        }

        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .download-section {
            margin-top: 20px;
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .download-button {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.9em;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 0 5px;
        }

        .download-button:hover {
            transform: translateY(-1px);
        }

        .download-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .query-section,
            .results-section {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏌️ Golf Database Query</h1>
            <p>Ask questions about PGA Tour players, tournaments, and performance data</p>
        </div>

        <div class="query-section">
            <div class="query-input-container">
                <input type="text" id="queryInput" class="query-input" 
                       placeholder="Ask something like: 'Who won the Masters Tournament in 2017?' or 'Show me Tiger Woods tournament results'"
                       maxlength="500">
            </div>
            <button id="queryButton" class="query-button">🔍 Search</button>

            <div class="examples">
                <h3>Try these example queries:</h3>
                <div class="example-queries">
                    <div class="example-query">Who won the Masters Tournament in 2017?</div>
                    <div class="example-query">Show me Tiger Woods tournament results</div>
                    <div class="example-query">Which players have the best putting stats?</div>
                    <div class="example-query">What tournaments were played at Pebble Beach?</div>
                    <div class="example-query">Show me Jordan Spieth 2015 season</div>
                    <div class="example-query">Which course has the lowest scoring average?</div>
                    <div class="example-query">Show me all major championship winners</div>
                </div>
            </div>
        </div>

        <div class="results-section">
            <div id="resultsContainer">
                <div class="no-results">
                    <h3>Welcome to the Golf Database!</h3>
                    <p>Enter a natural language query above to search through:</p>
                    <ul style="text-align: left; display: inline-block; margin-top: 15px;">
                        <li>748 PGA Tour players (2014-2022)</li>
                        <li>333 tournaments with detailed results</li>
                        <li>92 unique golf courses</li>
                        <li>36,864 individual performance records</li>
                        <li>Comprehensive strokes gained data</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        class GolfQueryInterface {
            constructor() {
                this.apiBase = '/api';
                this.queryInput = document.getElementById('queryInput');
                this.queryButton = document.getElementById('queryButton');
                this.resultsContainer = document.getElementById('resultsContainer');
                this.currentResults = null; // Store current results for download
                
                this.initializeEventListeners();
            }

            initializeEventListeners() {
                this.queryButton.addEventListener('click', () => this.handleQuery());
                this.queryInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.handleQuery();
                });

                document.querySelectorAll('.example-query').forEach(example => {
                    example.addEventListener('click', () => {
                        this.queryInput.value = example.textContent;
                        this.handleQuery();
                    });
                });
            }

            async handleQuery() {
                const query = this.queryInput.value.trim();
                if (!query) return;

                this.showLoading();
                this.queryButton.disabled = true;

                try {
                    const result = await this.processQuery(query);
                    this.displayResults(result);
                } catch (error) {
                    this.showError(error.message);
                } finally {
                    this.queryButton.disabled = false;
                }
            }

            async processQuery(query) {
                const parsedQuery = this.parseNaturalLanguage(query);
                const results = await this.executeQuery(parsedQuery);
                
                return {
                    interpretation: parsedQuery,
                    data: results,
                    originalQuery: query
                };
            }

            parseNaturalLanguage(query) {
                const lowerQuery = query.toLowerCase();
                
                // Tournament winner patterns
                if (lowerQuery.includes('who won') || lowerQuery.includes('winner') || lowerQuery.includes('champion')) {
                    return this.parseTournamentWinner(query);
                }
                
                // Player performance patterns
                if (lowerQuery.includes('show me') && (lowerQuery.includes('stats') || lowerQuery.includes('performance') || lowerQuery.includes('results'))) {
                    return this.parsePlayerPerformance(query);
                }
                
                // Best/worst performance patterns
                if (lowerQuery.includes('best') || lowerQuery.includes('worst') || lowerQuery.includes('top')) {
                    return this.parseBestWorstQuery(query);
                }
                
                // Course-related queries
                if (lowerQuery.includes('course') || lowerQuery.includes('pebble') || lowerQuery.includes('augusta') || lowerQuery.includes('torrey')) {
                    return this.parseCourseQuery(query);
                }
                
                // Tournament queries
                if (lowerQuery.includes('tournament') || lowerQuery.includes('masters') || lowerQuery.includes('open')) {
                    return this.parseTournamentQuery(query);
                }
                
                // Default to search
                return {
                    type: 'search',
                    query: query,
                    description: `Searching for "${query}" across all data`
                };
            }

            parseTournamentWinner(query) {
                const lowerQuery = query.toLowerCase();
                let tournamentMatch = null;
                
                // Simple string matching instead of complex regex
                if (lowerQuery.includes('masters')) {
                    tournamentMatch = 'masters';
                } else if (lowerQuery.includes('memorial')) {
                    tournamentMatch = 'memorial';
                } else if (lowerQuery.includes('u.s. open') || lowerQuery.includes('us open')) {
                    tournamentMatch = 'u.s. open';
                } else if (lowerQuery.includes('pga championship')) {
                    tournamentMatch = 'pga championship';
                } else if (lowerQuery.includes('open championship') || lowerQuery.includes('british open')) {
                    tournamentMatch = 'open championship';
                } else if (lowerQuery.includes('players championship') || lowerQuery.includes('players')) {
                    tournamentMatch = 'players';
                } else if (lowerQuery.includes('arnold palmer')) {
                    tournamentMatch = 'arnold palmer';
                }
                
                // Simple year extraction
                const yearMatch = query.match(/\\b(19|20)\\d{2}\\b/);
                
                return {
                    type: 'tournament_winner',
                    tournament: tournamentMatch,
                    year: yearMatch ? yearMatch[0] : null,
                    description: `Finding tournament winner${tournamentMatch ? ` for ${tournamentMatch}` : ''}${yearMatch ? ` in ${yearMatch[0]}` : ''}`
                };
            }

            parsePlayerPerformance(query) {
                const lowerQuery = query.toLowerCase();
                let playerMatch = null;
                
                // Simple player name matching
                if (lowerQuery.includes('tiger woods')) {
                    playerMatch = 'tiger woods';
                } else if (lowerQuery.includes('jordan spieth')) {
                    playerMatch = 'jordan spieth';
                } else if (lowerQuery.includes('rory mcilroy')) {
                    playerMatch = 'rory mcilroy';
                } else if (lowerQuery.includes('sergio garcia')) {
                    playerMatch = 'sergio garcia';
                } else if (lowerQuery.includes('dustin johnson')) {
                    playerMatch = 'dustin johnson';
                } else if (lowerQuery.includes('phil mickelson')) {
                    playerMatch = 'phil mickelson';
                }
                
                const yearMatch = query.match(/\\b(19|20)\\d{2}\\b/);
                
                return {
                    type: 'player_performance',
                    player: playerMatch,
                    year: yearMatch ? yearMatch[0] : null,
                    description: `Getting performance data${playerMatch ? ` for ${playerMatch}` : ''}${yearMatch ? ` in ${yearMatch[0]}` : ''}`
                };
            }

            parseBestWorstQuery(query) {
                const statType = query.match(/(putting|driving|approach|scrambling|scoring)/i);
                
                return {
                    type: 'best_worst',
                    statType: statType ? statType[1] : 'overall',
                    metric: query.includes('best') ? 'best' : 'worst',
                    description: `Finding ${query.includes('best') ? 'best' : 'worst'} ${statType ? statType[1] : 'overall'} performance`
                };
            }

            parseCourseQuery(query) {
                const courseMatch = query.match(/(pebble beach|augusta|torrey pines|riviera|tpc sawgrass)/i);
                
                return {
                    type: 'course',
                    course: courseMatch ? courseMatch[1] : null,
                    description: `Getting course information${courseMatch ? ` for ${courseMatch[1]}` : ''}`
                };
            }

            parseTournamentQuery(query) {
                const tournamentMatch = query.match(/(memorial|masters|open|championship|pga)/i);
                
                return {
                    type: 'tournament',
                    tournament: tournamentMatch ? tournamentMatch[1] : null,
                    description: `Getting tournament information${tournamentMatch ? ` for ${tournamentMatch[1]}` : ''}`
                };
            }

            async executeQuery(parsedQuery) {
                switch (parsedQuery.type) {
                    case 'tournament_winner':
                        return await this.getTournamentWinner(parsedQuery);
                    case 'player_performance':
                        return await this.getPlayerPerformance(parsedQuery);
                    case 'best_worst':
                        return await this.getBestWorstPerformance(parsedQuery);
                    case 'course':
                        return await this.getCourseInfo(parsedQuery);
                    case 'tournament':
                        return await this.getTournamentInfo(parsedQuery);
                    default:
                        return await this.searchAll(parsedQuery.query);
                }
            }

            async getTournamentWinner(parsedQuery) {
                let url = `${this.apiBase}/tournament-results`;
                const params = new URLSearchParams();
                
                if (parsedQuery.tournament) {
                    params.append('tournament', parsedQuery.tournament);
                }
                if (parsedQuery.year) {
                    params.append('year', parsedQuery.year);
                }
                params.append('position', '1');
                
                if (params.toString()) {
                    url += `?${params.toString()}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                return data.results || [];
            }

            async getPlayerPerformance(parsedQuery) {
                let url = `${this.apiBase}/tournament-results`;
                const params = new URLSearchParams();
                
                if (parsedQuery.player) {
                    params.append('player', parsedQuery.player);
                }
                if (parsedQuery.year) {
                    params.append('year', parsedQuery.year);
                }
                
                if (params.toString()) {
                    url += `?${params.toString()}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                return data.results || [];
            }

            async getBestWorstPerformance(parsedQuery) {
                const response = await fetch(`${this.apiBase}/tournament-results?limit=20`);
                const data = await response.json();
                
                let sortedData = data.results || [];
                
                if (parsedQuery.statType === 'putting') {
                    sortedData = sortedData.filter(r => r.strokes_gained_putting !== null)
                        .sort((a, b) => parsedQuery.metric === 'best' ? b.strokes_gained_putting - a.strokes_gained_putting : a.strokes_gained_putting - b.strokes_gained_putting);
                } else if (parsedQuery.statType === 'driving') {
                    sortedData = sortedData.filter(r => r.strokes_gained_off_tee !== null)
                        .sort((a, b) => parsedQuery.metric === 'best' ? b.strokes_gained_off_tee - a.strokes_gained_off_tee : a.strokes_gained_off_tee - b.strokes_gained_off_tee);
                } else {
                    sortedData = sortedData.filter(r => r.total_strokes !== null)
                        .sort((a, b) => parsedQuery.metric === 'best' ? a.total_strokes - b.total_strokes : b.total_strokes - a.total_strokes);
                }
                
                return sortedData.slice(0, 10);
            }

            async getCourseInfo(parsedQuery) {
                let url = `${this.apiBase}/courses`;
                if (parsedQuery.course) {
                    url += `?name=${encodeURIComponent(parsedQuery.course)}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                return data.courses || [];
            }

            async getTournamentInfo(parsedQuery) {
                let url = `${this.apiBase}/tournaments`;
                if (parsedQuery.tournament) {
                    url += `?name=${encodeURIComponent(parsedQuery.tournament)}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                return data.tournaments || [];
            }

            async searchAll(query) {
                const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                return data.results || [];
            }

            showLoading() {
                this.resultsContainer.innerHTML = `
                    <div class="loading">
                        <h3>🔍 Searching...</h3>
                        <p>Processing your query...</p>
                    </div>
                `;
            }

            showError(message) {
                this.resultsContainer.innerHTML = `
                    <div class="error">
                        <h3>❌ Error</h3>
                        <p>${message}</p>
                    </div>
                `;
            }

            displayResults(result) {
                const { interpretation, data, originalQuery } = result;
                
                // Store current results for download
                this.currentResults = data;
                
                let html = `
                    <div class="query-interpretation">
                        <h4>Query Interpretation:</h4>
                        <p>${interpretation.description}</p>
                    </div>
                `;

                if (!data || data.length === 0) {
                    this.currentResults = null;
                    html += `
                        <div class="no-results">
                            <h3>No results found</h3>
                            <p>Try rephrasing your query or check the example queries above.</p>
                        </div>
                    `;
                } else {
                    html += this.formatResults(data, interpretation.type);
                    
                    // Add download section
                    html += `
                        <div class="download-section">
                            <h4>📊 Download Results</h4>
                            <button class="download-button" onclick="window.golfInterface.downloadCSV()">📊 Download CSV</button>
                            <button class="download-button" onclick="window.golfInterface.downloadJSON()">📄 Download JSON</button>
                            <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                                ${data.length} result${data.length !== 1 ? 's' : ''} • Query: "${originalQuery}"
                            </p>
                        </div>
                    `;
                }

                this.resultsContainer.innerHTML = html;
            }

            formatResults(data, queryType) {
                if (queryType === 'tournament_winner') {
                    return this.formatTournamentWinners(data);
                } else if (queryType === 'player_performance') {
                    return this.formatPlayerResults(data);
                } else {
                    return this.formatGenericResults(data);
                }
            }

            formatTournamentWinners(data) {
                const columns = ['player_name', 'tournament_name', 'tournament_date', 'season', 'total_strokes', 'course_name'];
                const headers = ['Winner', 'Tournament', 'Date', 'Season', 'Winning Score', 'Course'];
                return this.createTable(data, columns, headers);
            }

            formatPlayerResults(data) {
                const columns = ['player_name', 'tournament_name', 'tournament_date', 'total_strokes', 'position_numeric', 'made_cut'];
                const headers = ['Player', 'Tournament', 'Date', 'Score', 'Position', 'Made Cut'];
                return this.createTable(data, columns, headers);
            }

            formatGenericResults(data) {
                const columns = this.getDisplayColumns(data[0]);
                const headers = columns.map(col => 
                    col.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())
                );
                return this.createTable(data, columns, headers);
            }

            getDisplayColumns(sampleRow) {
                if (!sampleRow) return [];
                
                const allKeys = Object.keys(sampleRow);
                const priorityKeys = ['player_name', 'tournament_name', 'tournament_date', 'course_name', 'total_strokes', 'position_numeric'];
                
                let displayKeys = [];
                
                priorityKeys.forEach(key => {
                    if (allKeys.includes(key)) {
                        displayKeys.push(key);
                    }
                });
                
                allKeys.forEach(key => {
                    if (!displayKeys.includes(key) && displayKeys.length < 8) {
                        displayKeys.push(key);
                    }
                });
                
                return displayKeys;
            }

            createTable(data, columns, headers) {
                let html = `
                    <div class="success">
                        <strong>Found ${data.length} result${data.length !== 1 ? 's' : ''}</strong>
                    </div>
                    <table class="results-table">
                        <thead>
                            <tr>
                                ${headers.map(header => `<th>${header}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.forEach(row => {
                    html += '<tr>';
                    columns.forEach(col => {
                        let value = row[col];
                        if (value === null || value === undefined) {
                            value = '-';
                        } else if (typeof value === 'number') {
                            value = value.toLocaleString();
                        }
                        html += `<td>${value}</td>`;
                    });
                    html += '</tr>';
                });

                html += '</tbody></table>';
                return html;
            }

            downloadCSV() {
                if (!this.currentResults || this.currentResults.length === 0) {
                    alert('No data to download');
                    return;
                }

                const csvData = this.convertToCSV(this.currentResults);
                const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `golf_query_results_${new Date().toISOString().slice(0,10)}.csv`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

            downloadJSON() {
                if (!this.currentResults || this.currentResults.length === 0) {
                    alert('No data to download');
                    return;
                }

                const jsonData = JSON.stringify(this.currentResults, null, 2);
                const blob = new Blob([jsonData], { type: 'application/json;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `golf_query_results_${new Date().toISOString().slice(0,10)}.json`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

            convertToCSV(data) {
                if (!data || data.length === 0) return '';
                
                const allKeys = [...new Set(data.flatMap(Object.keys))];
                const header = allKeys.join(',');
                
                const rows = data.map(row => {
                    return allKeys.map(key => {
                        let value = row[key];
                        
                        if (value === null || value === undefined) {
                            value = '';
                        }
                        
                        value = String(value);
                        if (value.includes(',') || value.includes('"') || value.includes('\\n')) {
                            value = '"' + value.replace(/"/g, '""') + '"';
                        }
                        
                        return value;
                    }).join(',');
                });
                
                return [header, ...rows].join('\\n');
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            window.golfInterface = new GolfQueryInterface();
        });
    </script>
</body>
</html>
'''

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # NEW: Route to serve the HTML interface
    @app.route('/')
    def home():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/interface')
    def interface():
        """Alternative route to the interface"""
        return render_template_string(HTML_TEMPLATE)
    
    # Your existing API routes (keeping them exactly as they are)
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
        """Get tournament results data with proper filtering"""
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
            year = request.args.get('year')
            position = request.args.get('position')  # NEW: for winner filtering
            
            # Build query with proper winner logic
            query_str = """
                SELECT 
                    tr.result_id,
                    p.first_name || ' ' || p.last_name as player_name,
                    t.tournament_name,
                    t.tournament_date,
                    t.season,
                    c.course_name,
                    tr.position_numeric,
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
                WHERE tr.made_cut = 1
            """
            
            params = {}
            
            # Player name filtering
            if player_name:
                query_str += " AND (p.first_name LIKE :player_search OR p.last_name LIKE :player_search OR (p.first_name || ' ' || p.last_name) LIKE :player_search)"
                params['player_search'] = f"%{player_name}%"
            
            # Tournament name filtering
            if tournament_name:
                query_str += " AND t.tournament_name LIKE :tournament_search"
                params['tournament_search'] = f"%{tournament_name}%"
            
            # Year filtering (improved to handle both date and season)
            if year:
                query_str += " AND (t.tournament_date LIKE :year_search OR t.season = :year_numeric)"
                params['year_search'] = f"%{year}%"
                params['year_numeric'] = int(year)
            
            # Winner filtering (position = 1)
            if position == '1':
                # For each tournament, find the player with lowest strokes who made the cut
                query_str = """
                    WITH tournament_winners AS (
                        SELECT 
                            tr.tournament_id,
                            MIN(tr.total_strokes) as winning_score
                        FROM tournament_results tr
                        WHERE tr.made_cut = 1 AND tr.total_strokes IS NOT NULL
                        GROUP BY tr.tournament_id
                    ),
                    winner_details AS (
                        SELECT 
                            tr.result_id,
                            p.first_name || ' ' || p.last_name as player_name,
                            t.tournament_name,
                            t.tournament_date,
                            t.season,
                            c.course_name,
                            tr.position_numeric,
                            tr.final_position,
                            tr.total_strokes,
                            tr.made_cut,
                            tr.sg_total,
                            tr.sg_putting,
                            tr.sg_approach,
                            tr.sg_off_the_tee,
                            ROW_NUMBER() OVER (PARTITION BY tr.tournament_id ORDER BY tr.total_strokes ASC) as rank_in_tournament
                        FROM tournament_results tr
                        JOIN players p ON tr.player_id = p.player_id
                        JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
                        LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
                        JOIN tournament_winners tw ON tr.tournament_id = tw.tournament_id AND tr.total_strokes = tw.winning_score
                        WHERE tr.made_cut = 1
                """
                
                # Add filters to the CTE query
                if player_name:
                    query_str += " AND (p.first_name LIKE :player_search OR p.last_name LIKE :player_search OR (p.first_name || ' ' || p.last_name) LIKE :player_search)"
                
                if tournament_name:
                    query_str += " AND t.tournament_name LIKE :tournament_search"
                
                if year:
                    query_str += " AND (t.tournament_date LIKE :year_search OR t.season = :year_numeric)"
                
                query_str += """
                    )
                    SELECT * FROM winner_details 
                    WHERE rank_in_tournament = 1
                    ORDER BY tournament_date DESC
                """
            
            else:
                # Regular ordering for non-winner queries
                query_str += " ORDER BY t.tournament_date DESC, tr.total_strokes ASC"
            
            query_str += f" LIMIT {limit}"
            
            result = session.execute(text(query_str), params)
            results_data = []
            
            for row in result:
                result_dict = {
                    "result_id": row[0],
                    "player_name": row[1],
                    "tournament_name": row[2],
                    "tournament_date": row[3] if row[3] else None,
                    "season": row[4],
                    "course_name": row[5],
                    "position_numeric": row[6],
                    "final_position": row[7],
                    "total_strokes": row[8],
                    "made_cut": bool(row[9]) if row[9] is not None else None,
                    "strokes_gained_total": float(row[10]) if row[10] is not None else None,
                    "strokes_gained_putting": float(row[11]) if row[11] is not None else None,
                    "strokes_gained_approach": float(row[12]) if row[12] is not None else None,
                    "strokes_gained_off_tee": float(row[13]) if row[13] is not None else None
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
                    "year": year,
                    "position": position,
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
    print("🏌️ Starting Enhanced Golf Database API with Natural Language Interface...")
    print("📡 API will be available at: http://localhost:5000")
    print("🌐 Natural Language Interface at: http://localhost:5000")
    print("🎯 API endpoints:")
    print("   • /api/courses - Real course data")
    print("   • /api/tournaments - Real tournament data") 
    print("   • /api/tournament-results - Individual results")
    print("   • /api/search?q=search_term - Search everything")
    
    if db_manager:
        print("🔗 Database URL:", db_manager.database_url)
    else:
        print("⚠️  Database not connected - check your models directory")
        
    app.run(debug=True, host='0.0.0.0', port=5000)