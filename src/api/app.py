"""
Golf Database API - Main Flask Application
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

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
        return jsonify({"status": "healthy"})
    
    @app.route('/api/players')
    def get_players():
        # Placeholder for player data endpoint
        return jsonify({
            "players": [],
            "message": "Players endpoint - connect to database"
        })
        
    @app.route('/api/tournaments')
    def get_tournaments():
        # Placeholder for tournament data endpoint
        return jsonify({
            "tournaments": [],
            "message": "Tournaments endpoint - connect to database"
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🏌️ Starting Golf Database API...")
    print("📡 API will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)