#!/usr/bin/env python3
"""
Test what the API should return for players
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from models.database import db_manager
from models.models import Player

def test_api_logic():
    """Test the same logic your API should be using"""
    print("🧪 Testing API database logic...")
    
    session = db_manager.get_session()
    
    try:
        # This is what your API endpoint should be doing
        players = session.query(Player).all()
        print(f"📊 Found {len(players)} players")
        
        # Convert to dict format (like API should return)
        players_data = []
        for player in players:
            player_dict = {
                'player_id': player.player_id,
                'first_name': player.first_name,
                'last_name': player.last_name,
                'full_name': player.full_name,
                'nationality': player.nationality,
                'birth_date': str(player.birth_date) if player.birth_date else None,
                'world_ranking': player.world_ranking,
                'career_earnings': float(player.career_earnings) if player.career_earnings else None
            }
            players_data.append(player_dict)
            print(f"✅ Player: {player_dict}")
        
        # This is what your API should return
        response = {
            "message": "Players retrieved successfully",
            "players": players_data,
            "count": len(players_data)
        }
        
        print(f"\n📡 API should return:")
        import json
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"❌ Error in API logic: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_api_logic()