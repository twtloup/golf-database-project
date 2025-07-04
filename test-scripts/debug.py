#!/usr/bin/env python3
"""
Simple debug script to test imports and basic functionality
"""

print("🔍 Starting debug script...")

import os
import sys
from pathlib import Path

print(f"📍 Current working directory: {os.getcwd()}")
print(f"📍 Script location: {__file__}")

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
print(f"📍 Project root: {project_root}")
print(f"📍 Src path: {src_path}")
print(f"📍 Src path exists: {src_path.exists()}")

sys.path.insert(0, str(src_path))

print("🔄 Attempting imports...")

try:
    print("  - Importing database module...")
    from models.database import DatabaseManager, db_manager
    print("  ✅ Database module imported successfully")
    
    print("  - Importing models...")
    from models.models import Base, Player, Course, Tournament
    print("  ✅ Models imported successfully")
    
    print("🔗 Testing database connection...")
    print(f"  - Database URL: {db_manager.database_url}")
    
    # Try to create a session
    session = db_manager.get_session()
    print("  ✅ Session created successfully")
    session.close()
    print("  ✅ Session closed successfully")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"❌ Error type: {type(e).__name__}")
    import traceback
    print("📍 Full traceback:")
    traceback.print_exc()

print("🏁 Debug script completed")