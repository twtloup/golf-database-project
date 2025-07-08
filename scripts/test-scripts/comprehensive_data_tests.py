#!/usr/bin/env python3
"""
Comprehensive Data Validation Tests
Tests both database integrity and API consistency
"""

import sqlite3
import requests
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class GolfDataValidator:
    def __init__(self):
        self.db_path = Path("golf_database.db")
        self.api_base = "http://localhost:5000/api"
        self.test_results = {"passed": 0, "failed": 0, "tests": []}
        
        # Load original datasets for comparison
        self.tournament_csv = Path("data/kaggle/pga_tour_alternative/ASA All PGA Raw Data - Tourn Level.csv")
        self.player_csv = Path("data/kaggle/pga_tour_alternative/pgaTourData.csv")
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results["tests"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
    
    def test_database_connectivity(self):
        """Test 1: Database file exists and is accessible"""
        print("\n🔍 TEST CATEGORY: Database Connectivity")
        print("=" * 50)
        
        # Test database file exists
        exists = self.db_path.exists()
        self.log_test("Database file exists", exists, f"Path: {self.db_path}")
        
        if not exists:
            return False
        
        # Test database connection
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            self.log_test("Database connection works", True)
            return True
        except Exception as e:
            self.log_test("Database connection works", False, str(e))
            return False
    
    def test_table_structure(self):
        """Test 2: All expected tables exist with correct structure"""
        print("\n🔍 TEST CATEGORY: Table Structure")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Expected tables and their key columns
        expected_tables = {
            'players': ['player_id', 'first_name', 'last_name'],
            'courses_enhanced': ['course_id', 'course_name', 'location'],
            'tournaments_enhanced': ['tournament_id', 'tournament_name', 'tournament_date', 'course_id'],
            'tournament_results': ['result_id', 'tournament_id', 'player_id', 'total_strokes', 'sg_total'],
            'player_yearly_stats': ['stat_id', 'player_id', 'year', 'average_score']
        }
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [row[0] for row in cursor.fetchall()]
        
        for table_name, expected_columns in expected_tables.items():
            # Test table exists
            table_exists = table_name in actual_tables
            self.log_test(f"Table '{table_name}' exists", table_exists)
            
            if table_exists:
                # Test columns exist
                cursor.execute(f"PRAGMA table_info({table_name})")
                actual_columns = [col[1] for col in cursor.fetchall()]
                
                for col in expected_columns:
                    col_exists = col in actual_columns
                    self.log_test(f"Column '{table_name}.{col}' exists", col_exists)
        
        conn.close()
    
    def test_data_counts(self):
        """Test 3: Data counts match expectations from original datasets"""
        print("\n🔍 TEST CATEGORY: Data Counts")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test record counts
        expected_counts = {
            'players': (700, 800),  # Should be around 748
            'tournaments_enhanced': (300, 400),  # Should be around 333
            'tournament_results': (35000, 40000),  # Should be around 36,864
            'courses_enhanced': (200, 1200),  # Should be much fewer after deduplication
            'player_yearly_stats': (2000, 2500)  # Should be around 2,312
        }
        
        for table, (min_count, max_count) in expected_counts.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual_count = cursor.fetchone()[0]
            
            count_ok = min_count <= actual_count <= max_count
            self.log_test(
                f"Table '{table}' count in range", 
                count_ok,
                f"Expected: {min_count}-{max_count}, Actual: {actual_count:,}"
            )
        
        conn.close()
    
    def test_data_relationships(self):
        """Test 4: Foreign key relationships are valid"""
        print("\n🔍 TEST CATEGORY: Data Relationships")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test 1: All tournament results have valid players
        cursor.execute("""
            SELECT COUNT(*) FROM tournament_results tr
            LEFT JOIN players p ON tr.player_id = p.player_id
            WHERE p.player_id IS NULL
        """)
        orphaned_results = cursor.fetchone()[0]
        self.log_test(
            "All tournament results have valid players", 
            orphaned_results == 0,
            f"Orphaned results: {orphaned_results}"
        )
        
        # Test 2: All tournament results have valid tournaments
        cursor.execute("""
            SELECT COUNT(*) FROM tournament_results tr
            LEFT JOIN tournaments_enhanced t ON tr.tournament_id = t.tournament_id
            WHERE t.tournament_id IS NULL
        """)
        orphaned_tournaments = cursor.fetchone()[0]
        self.log_test(
            "All tournament results have valid tournaments", 
            orphaned_tournaments == 0,
            f"Orphaned tournament results: {orphaned_tournaments}"
        )
        
        # Test 3: All tournaments have valid courses (allowing NULLs)
        cursor.execute("""
            SELECT COUNT(*) FROM tournaments_enhanced t
            LEFT JOIN courses_enhanced c ON t.course_id = c.course_id
            WHERE t.course_id IS NOT NULL AND c.course_id IS NULL
        """)
        invalid_courses = cursor.fetchone()[0]
        self.log_test(
            "All tournaments with course_id have valid courses", 
            invalid_courses == 0,
            f"Invalid course references: {invalid_courses}"
        )
        
        # Test 4: All yearly stats have valid players
        cursor.execute("""
            SELECT COUNT(*) FROM player_yearly_stats pys
            LEFT JOIN players p ON pys.player_id = p.player_id
            WHERE p.player_id IS NULL
        """)
        orphaned_stats = cursor.fetchone()[0]
        self.log_test(
            "All yearly stats have valid players", 
            orphaned_stats == 0,
            f"Orphaned yearly stats: {orphaned_stats}"
        )
        
        conn.close()
    
    def test_data_quality(self):
        """Test 5: Data quality checks"""
        print("\n🔍 TEST CATEGORY: Data Quality")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test 1: No duplicate players
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT first_name, last_name, COUNT(*) 
                FROM players 
                GROUP BY first_name, last_name 
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_players = cursor.fetchone()[0]
        self.log_test(
            "No duplicate players", 
            duplicate_players == 0,
            f"Duplicate player combinations: {duplicate_players}"
        )
        
        # Test 2: No duplicate courses after cleanup
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT course_name, location, COUNT(*) 
                FROM courses_enhanced 
                WHERE course_name IS NOT NULL
                GROUP BY course_name, location 
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_courses = cursor.fetchone()[0]
        self.log_test(
            "No duplicate courses", 
            duplicate_courses == 0,
            f"Duplicate course combinations: {duplicate_courses}"
        )
        
        # Test 3: Reasonable date ranges
        cursor.execute("""
            SELECT MIN(tournament_date), MAX(tournament_date) 
            FROM tournaments_enhanced 
            WHERE tournament_date IS NOT NULL
        """)
        min_date, max_date = cursor.fetchone()
        date_range_ok = "2014" <= min_date <= "2023" and "2014" <= max_date <= "2023"
        self.log_test(
            "Tournament dates in reasonable range", 
            date_range_ok,
            f"Date range: {min_date} to {max_date}"
        )
        
        # Test 4: Reasonable score ranges
        cursor.execute("""
            SELECT MIN(total_strokes), MAX(total_strokes) 
            FROM tournament_results 
            WHERE total_strokes IS NOT NULL
        """)
        min_score, max_score = cursor.fetchone()
        score_range_ok = 50 <= min_score <= 100 and 200 <= max_score <= 350
        self.log_test(
            "Golf scores in reasonable range", 
            score_range_ok,
            f"Score range: {min_score} to {max_score} strokes"
        )
        
        conn.close()
    
    def test_api_connectivity(self):
        """Test 6: API is running and responding"""
        print("\n🔍 TEST CATEGORY: API Connectivity")
        print("=" * 50)
        
        # Test API health endpoint
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            api_healthy = response.status_code == 200
            self.log_test(
                "API health endpoint responds", 
                api_healthy,
                f"Status: {response.status_code}"
            )
            
            if api_healthy:
                health_data = response.json()
                db_connected = health_data.get("database_connected", False)
                self.log_test(
                    "API reports database connected", 
                    db_connected,
                    f"Status: {health_data.get('status', 'unknown')}"
                )
        
        except Exception as e:
            self.log_test("API health endpoint responds", False, str(e))
    
    def test_api_data_consistency(self):
        """Test 7: API data matches database data"""
        print("\n🔍 TEST CATEGORY: API Data Consistency")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test players endpoint
        try:
            response = requests.get(f"{self.api_base}/players", timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                api_player_count = api_data.get("total_players", 0)
                
                cursor.execute("SELECT COUNT(*) FROM players")
                db_player_count = cursor.fetchone()[0]
                
                counts_match = api_player_count == db_player_count
                self.log_test(
                    "Players API count matches database", 
                    counts_match,
                    f"API: {api_player_count}, DB: {db_player_count}"
                )
            else:
                self.log_test("Players API accessible", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_test("Players API accessible", False, str(e))
        
        # Test tournaments endpoint
        try:
            response = requests.get(f"{self.api_base}/tournaments", timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                api_tournament_count = api_data.get("total_tournaments", 0)
                
                cursor.execute("SELECT COUNT(*) FROM tournaments_enhanced")
                db_tournament_count = cursor.fetchone()[0]
                
                counts_match = api_tournament_count == db_tournament_count
                self.log_test(
                    "Tournaments API count matches database", 
                    counts_match,
                    f"API: {api_tournament_count}, DB: {db_tournament_count}"
                )
            else:
                self.log_test("Tournaments API accessible", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_test("Tournaments API accessible", False, str(e))
        
        # Test tournament results endpoint
        try:
            response = requests.get(f"{self.api_base}/tournament-results", timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                api_results_count = api_data.get("total_results", 0)
                
                cursor.execute("SELECT COUNT(*) FROM tournament_results")
                db_results_count = cursor.fetchone()[0]
                
                counts_match = api_results_count == db_results_count
                self.log_test(
                    "Tournament results API count matches database", 
                    counts_match,
                    f"API: {api_results_count}, DB: {db_results_count}"
                )
            else:
                self.log_test("Tournament results API accessible", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_test("Tournament results API accessible", False, str(e))
        
        conn.close()
    
    def test_original_data_consistency(self):
        """Test 8: Database data matches original CSV files"""
        print("\n🔍 TEST CATEGORY: Original Data Consistency")
        print("=" * 50)
        
        # Test tournament data consistency
        if self.tournament_csv.exists():
            try:
                df_original = pd.read_csv(self.tournament_csv)
                original_count = len(df_original)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tournament_results")
                db_count = cursor.fetchone()[0]
                conn.close()
                
                counts_match = original_count == db_count
                self.log_test(
                    "Tournament results count matches original CSV", 
                    counts_match,
                    f"Original CSV: {original_count:,}, Database: {db_count:,}"
                )
                
                # Test unique players in original data
                original_players = df_original['player'].nunique()
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(DISTINCT p.player_id) 
                    FROM tournament_results tr
                    JOIN players p ON tr.player_id = p.player_id
                """)
                db_players_in_results = cursor.fetchone()[0]
                conn.close()
                
                # Allow some variance due to name parsing differences
                players_reasonable = abs(original_players - db_players_in_results) <= 50
                self.log_test(
                    "Player count reasonably matches original data", 
                    players_reasonable,
                    f"Original unique: {original_players}, DB players with results: {db_players_in_results}"
                )
                
            except Exception as e:
                self.log_test("Tournament CSV comparison", False, str(e))
        else:
            self.log_test("Tournament CSV file exists", False, f"Path: {self.tournament_csv}")
        
        # Test yearly stats consistency
        if self.player_csv.exists():
            try:
                df_yearly = pd.read_csv(self.player_csv)
                original_yearly_count = len(df_yearly)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM player_yearly_stats")
                db_yearly_count = cursor.fetchone()[0]
                conn.close()
                
                yearly_counts_match = original_yearly_count == db_yearly_count
                self.log_test(
                    "Yearly stats count matches original CSV", 
                    yearly_counts_match,
                    f"Original CSV: {original_yearly_count:,}, Database: {db_yearly_count:,}"
                )
                
            except Exception as e:
                self.log_test("Yearly stats CSV comparison", False, str(e))
        else:
            self.log_test("Yearly stats CSV file exists", False, f"Path: {self.player_csv}")
    
    def test_specific_data_samples(self):
        """Test 9: Spot check specific data samples"""
        print("\n🔍 TEST CATEGORY: Data Sample Validation")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test 1: Check for famous players
        famous_players = ['Tiger', 'Jordan', 'Rory', 'Dustin', 'Brooks']
        for player_name in famous_players:
            cursor.execute("""
                SELECT COUNT(*) FROM players 
                WHERE first_name LIKE ? OR last_name LIKE ?
            """, (f"%{player_name}%", f"%{player_name}%"))
            
            count = cursor.fetchone()[0]
            found = count > 0
            self.log_test(
                f"Famous player '{player_name}' found in database", 
                found,
                f"Matches: {count}"
            )
        
        # Test 2: Check for famous tournaments
        famous_tournaments = ['Masters', 'Memorial', 'PGA Championship', 'Players', 'U.S. Open']
        for tournament_name in famous_tournaments:
            cursor.execute("""
                SELECT COUNT(*) FROM tournaments_enhanced 
                WHERE tournament_name LIKE ?
            """, (f"%{tournament_name}%",))
            
            count = cursor.fetchone()[0]
            found = count > 0
            self.log_test(
                f"Famous tournament '{tournament_name}' found in database", 
                found,
                f"Matches: {count}"
            )
        
        # Test 3: Check for reasonable strokes gained values
        cursor.execute("""
            SELECT COUNT(*) FROM tournament_results 
            WHERE sg_total IS NOT NULL 
            AND sg_total BETWEEN -5 AND 5
        """)
        reasonable_sg = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tournament_results 
            WHERE sg_total IS NOT NULL
        """)
        total_sg = cursor.fetchone()[0]
        
        sg_percentage = (reasonable_sg / total_sg * 100) if total_sg > 0 else 0
        sg_reasonable = sg_percentage > 95  # 95% should be in reasonable range
        
        self.log_test(
            "Strokes gained values are reasonable", 
            sg_reasonable,
            f"{sg_percentage:.1f}% of SG values between -5 and +5"
        )
        
        conn.close()
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🏌️ COMPREHENSIVE GOLF DATABASE VALIDATION")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        
        # Run all test categories
        if self.test_database_connectivity():
            self.test_table_structure()
            self.test_data_counts()
            self.test_data_relationships()
            self.test_data_quality()
            self.test_api_connectivity()
            self.test_api_data_consistency()
            self.test_original_data_consistency()
            self.test_specific_data_samples()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏆 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        pass_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if self.test_results["failed"] == 0:
            print(f"\n🎉 ALL TESTS PASSED! Your golf database is in excellent condition!")
        else:
            print(f"\n⚠️  Some tests failed. Review the details above to identify issues.")
        
        # Save detailed results
        report_file = Path("data/validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📋 Detailed results saved to: {report_file}")
        
        return self.test_results["failed"] == 0

if __name__ == "__main__":
    validator = GolfDataValidator()
    success = validator.run_all_tests()
    
    if success:
        print(f"\n🚀 Your golf database is ready for natural language queries!")
    else:
        print(f"\n🔧 Please address the failed tests before proceeding.")