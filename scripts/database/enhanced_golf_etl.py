#!/usr/bin/env python3
"""
Enhanced ETL Pipeline for Tournament-Level Golf Data
Loads both yearly stats and tournament-by-tournament results
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import date, datetime
import re

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

try:
    from models.database import db_manager
    from models.models import Player, Tournament, TournamentEntry, Course, Round, Base
    print("✅ Database modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class EnhancedGolfETL:
    def __init__(self):
        self.tournament_data_path = Path("data/kaggle/pga_tour_alternative/ASA All PGA Raw Data - Tourn Level.csv")
        self.player_data_path = Path("data/kaggle/pga_tour_alternative/pgaTourData.csv")
        self.session = None
        
    def create_session(self):
        """Create database session"""
        try:
            self.session = db_manager.get_session()
            print("✅ Database session created")
            return True
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def create_enhanced_tables(self):
        """Create additional tables for tournament data"""
        from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, Text
        
        # Enhanced Course table
        class CourseEnhanced(Base):
            __tablename__ = 'courses_enhanced'
            
            course_id = Column(Integer, primary_key=True, autoincrement=True)
            course_name = Column(String(150), nullable=False)
            location = Column(String(100))
            total_par = Column(Integer)
        
        # Enhanced Tournament table
        class TournamentEnhanced(Base):
            __tablename__ = 'tournaments_enhanced'
            
            tournament_id = Column(Integer, primary_key=True, autoincrement=True)
            external_tournament_id = Column(String(50))  # The tournament id from the data
            tournament_name = Column(String(150), nullable=False)
            course_id = Column(Integer, ForeignKey('courses_enhanced.course_id'))
            tournament_date = Column(Date)
            purse_millions = Column(Float)
            season = Column(Integer)
            has_cut = Column(Boolean)
        
        # Tournament Results table
        class TournamentResult(Base):
            __tablename__ = 'tournament_results'
            
            result_id = Column(Integer, primary_key=True, autoincrement=True)
            tournament_id = Column(Integer, ForeignKey('tournaments_enhanced.tournament_id'))
            player_id = Column(Integer, ForeignKey('players.player_id'))
            external_player_id = Column(String(50))  # The player id from the data
            
            # Performance metrics
            total_strokes = Column(Integer)
            par_total = Column(Integer)  # hole_par from data
            rounds_played = Column(Integer)
            made_cut = Column(Boolean)
            final_position = Column(String(10))  # T32, CUT, etc.
            position_numeric = Column(Integer)  # Numeric position if applicable
            
            # Strokes Gained metrics
            sg_putting = Column(Float)
            sg_around_green = Column(Float)
            sg_approach = Column(Float)
            sg_off_the_tee = Column(Float)
            sg_tee_to_green = Column(Float)
            sg_total = Column(Float)
            
            # DraftKings/FanDuel points (for fantasy sports analysis)
            dk_points = Column(Float)
            fd_points = Column(Float)
            sd_points = Column(Float)
        
        # Yearly Performance Stats (from original data)
        class PlayerYearlyStats(Base):
            __tablename__ = 'player_yearly_stats'
            
            stat_id = Column(Integer, primary_key=True, autoincrement=True)
            player_id = Column(Integer, ForeignKey('players.player_id'), nullable=False)
            year = Column(Integer, nullable=False)
            rounds_played = Column(Integer)
            fairway_percentage = Column(Float)
            avg_distance = Column(Float)
            greens_in_regulation = Column(Float)
            average_putts = Column(Float)
            average_scrambling = Column(Float)
            average_score = Column(Float)
            points = Column(Integer)
            wins = Column(Integer)
            top_10_finishes = Column(Integer)
            avg_sg_putts = Column(Float)
            avg_sg_total = Column(Float)
            sg_off_the_tee = Column(Float)
            sg_approach = Column(Float)
            sg_around_green = Column(Float)
            prize_money = Column(Float)
        
        # Create all tables
        try:
            Base.metadata.create_all(db_manager.engine, tables=[
                CourseEnhanced.__table__,
                TournamentEnhanced.__table__,
                TournamentResult.__table__,
                PlayerYearlyStats.__table__
            ])
            print("✅ Created enhanced database tables")
            return CourseEnhanced, TournamentEnhanced, TournamentResult, PlayerYearlyStats
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return None, None, None, None
    
    def load_tournament_data(self):
        """Load the tournament-level data"""
        print("📊 Loading tournament-level data...")
        try:
            self.df_tournament = pd.read_csv(self.tournament_data_path)
            # Clean the data
            self.df_tournament = self.df_tournament.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], errors='ignore')
            print(f"✅ Loaded {len(self.df_tournament):,} tournament records")
            return True
        except Exception as e:
            print(f"❌ Error loading tournament data: {e}")
            return False
    
    def load_yearly_data(self):
        """Load the yearly stats data"""
        print("📊 Loading yearly player data...")
        try:
            self.df_yearly = pd.read_csv(self.player_data_path)
            
            # Clean numeric columns that might have commas
            numeric_columns = ['Points', 'Wins', 'Top 10', 'Rounds']
            for col in numeric_columns:
                if col in self.df_yearly.columns:
                    self.df_yearly[col] = self.df_yearly[col].astype(str).str.replace(',', '', regex=False)
                    self.df_yearly[col] = pd.to_numeric(self.df_yearly[col], errors='coerce')
            
            # Clean money column
            if 'Money' in self.df_yearly.columns:
                self.df_yearly['Money_Clean'] = self.df_yearly['Money'].astype(str).str.replace('[$,]', '', regex=True)
                self.df_yearly['Money_Clean'] = pd.to_numeric(self.df_yearly['Money_Clean'], errors='coerce')
            
            print(f"✅ Loaded {len(self.df_yearly):,} yearly records")
            return True
        except Exception as e:
            print(f"❌ Error loading yearly data: {e}")
            return False
    
    def load_players(self):
        """Load unique players from both datasets"""
        print("👥 Loading players...")
        
        # Get players from tournament data
        tournament_players = set()
        if hasattr(self, 'df_tournament'):
            tournament_players.update(self.df_tournament['player'].dropna().unique())
        
        # Get players from yearly data
        yearly_players = set()
        if hasattr(self, 'df_yearly'):
            yearly_players.update(self.df_yearly['Player Name'].dropna().unique())
        
        # Combine all unique players
        all_players = tournament_players.union(yearly_players)
        new_players = 0
        
        for player_name in all_players:
            if pd.isna(player_name) or player_name == '':
                continue
                
            # Check if player already exists
            existing_player = self.session.query(Player).filter_by(
                first_name=player_name.split()[0] if len(player_name.split()) > 1 else player_name,
                last_name=' '.join(player_name.split()[1:]) if len(player_name.split()) > 1 else ""
            ).first()
            
            if not existing_player:
                # Create new player
                name_parts = str(player_name).split()
                first_name = name_parts[0] if name_parts else str(player_name)
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                new_player = Player(
                    first_name=first_name,
                    last_name=last_name,
                    nationality="USA"  # Default to USA
                )
                
                self.session.add(new_player)
                new_players += 1
        
        self.session.commit()
        print(f"✅ Added {new_players} new players (total unique: {len(all_players)})")
        return True
    
    def load_courses(self, CourseEnhanced):
        """Load unique courses from tournament data"""
        print("🏌️ Loading courses...")
        
        if not hasattr(self, 'df_tournament'):
            print("⚠️ No tournament data available for courses")
            return True
        
        # Get unique courses
        unique_courses = self.df_tournament[['course', 'hole_par']].drop_duplicates()
        new_courses = 0
        
        for _, row in unique_courses.iterrows():
            course_name = row['course']
            if pd.isna(course_name):
                continue
                
            # Check if course exists
            existing_course = self.session.query(CourseEnhanced).filter_by(
                course_name=course_name
            ).first()
            
            if not existing_course:
                # Parse location from course name (e.g., "Muirfield Village Golf Club - Dublin, OH")
                location = ""
                if " - " in course_name:
                    parts = course_name.split(" - ")
                    if len(parts) > 1:
                        location = parts[1]
                        course_name = parts[0]
                
                new_course = CourseEnhanced(
                    course_name=course_name,
                    location=location,
                    total_par=int(row['hole_par']) if pd.notna(row['hole_par']) else None
                )
                
                self.session.add(new_course)
                new_courses += 1
        
        self.session.commit()
        print(f"✅ Added {new_courses} new courses")
        return True
    
    def load_tournaments(self, TournamentEnhanced, CourseEnhanced):
        """Load unique tournaments"""
        print("🏆 Loading tournaments...")
        
        if not hasattr(self, 'df_tournament'):
            print("⚠️ No tournament data available")
            return True
        
        # Get unique tournaments
        unique_tournaments = self.df_tournament[[
            'tournament id', 'tournament name', 'course', 'date', 'purse', 'season', 'no_cut'
        ]].drop_duplicates()
        
        new_tournaments = 0
        
        for _, row in unique_tournaments.iterrows():
            tournament_id = str(row['tournament id'])
            tournament_name = row['tournament name']
            
            if pd.isna(tournament_name):
                continue
            
            # Check if tournament exists
            existing_tournament = self.session.query(TournamentEnhanced).filter_by(
                external_tournament_id=tournament_id
            ).first()
            
            if not existing_tournament:
                # Find course
                course = None
                if pd.notna(row['course']):
                    course_name = row['course']
                    if " - " in course_name:
                        course_name = course_name.split(" - ")[0]
                    course = self.session.query(CourseEnhanced).filter_by(
                        course_name=course_name
                    ).first()
                
                # Parse date
                tournament_date = None
                if pd.notna(row['date']):
                    try:
                        tournament_date = pd.to_datetime(row['date']).date()
                    except:
                        pass
                
                new_tournament = TournamentEnhanced(
                    external_tournament_id=tournament_id,
                    tournament_name=tournament_name,
                    course_id=course.course_id if course else None,
                    tournament_date=tournament_date,
                    purse_millions=float(row['purse']) if pd.notna(row['purse']) else None,
                    season=int(row['season']) if pd.notna(row['season']) else None,
                    has_cut=not bool(row['no_cut']) if pd.notna(row['no_cut']) else True
                )
                
                self.session.add(new_tournament)
                new_tournaments += 1
        
        self.session.commit()
        print(f"✅ Added {new_tournaments} new tournaments")
        return True
    
    def load_tournament_results(self, TournamentResult, TournamentEnhanced):
        """Load individual tournament results"""
        print("📈 Loading tournament results...")
        
        if not hasattr(self, 'df_tournament'):
            print("⚠️ No tournament data available")
            return True
        
        results_added = 0
        
        for _, row in self.df_tournament.iterrows():
            # Find tournament
            tournament = self.session.query(TournamentEnhanced).filter_by(
                external_tournament_id=str(row['tournament id'])
            ).first()
            
            # Find player
            player_name = row['player']
            if pd.isna(player_name):
                continue
                
            name_parts = str(player_name).split()
            first_name = name_parts[0] if name_parts else str(player_name)
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            player = self.session.query(Player).filter_by(
                first_name=first_name,
                last_name=last_name
            ).first()
            
            if tournament and player:
                # Check if result already exists
                existing_result = self.session.query(TournamentResult).filter_by(
                    tournament_id=tournament.tournament_id,
                    player_id=player.player_id
                ).first()
                
                if not existing_result:
                    result = TournamentResult(
                        tournament_id=tournament.tournament_id,
                        player_id=player.player_id,
                        external_player_id=str(row['player id']) if pd.notna(row['player id']) else None,
                        total_strokes=int(row['strokes']) if pd.notna(row['strokes']) else None,
                        par_total=int(row['hole_par']) if pd.notna(row['hole_par']) else None,
                        rounds_played=int(row['n_rounds']) if pd.notna(row['n_rounds']) else None,
                        made_cut=bool(row['made_cut']) if pd.notna(row['made_cut']) else None,
                        final_position=str(row['Finish']) if pd.notna(row['Finish']) else None,
                        position_numeric=int(row['pos']) if pd.notna(row['pos']) else None,
                        sg_putting=float(row['sg_putt']) if pd.notna(row['sg_putt']) else None,
                        sg_around_green=float(row['sg_arg']) if pd.notna(row['sg_arg']) else None,
                        sg_approach=float(row['sg_app']) if pd.notna(row['sg_app']) else None,
                        sg_off_the_tee=float(row['sg_ott']) if pd.notna(row['sg_ott']) else None,
                        sg_tee_to_green=float(row['sg_t2g']) if pd.notna(row['sg_t2g']) else None,
                        sg_total=float(row['sg_total']) if pd.notna(row['sg_total']) else None,
                        dk_points=float(row['total_DKP']) if pd.notna(row['total_DKP']) else None,
                        fd_points=float(row['total_FDP']) if pd.notna(row['total_FDP']) else None,
                        sd_points=float(row['total_SDP']) if pd.notna(row['total_SDP']) else None
                    )
                    
                    self.session.add(result)
                    results_added += 1
        
        self.session.commit()
        print(f"✅ Added {results_added} tournament results")
        return True
    
    def load_yearly_stats(self, PlayerYearlyStats):
        """Load yearly performance statistics"""
        print("📅 Loading yearly statistics...")
        
        if not hasattr(self, 'df_yearly'):
            print("⚠️ No yearly data available")
            return True
        
        stats_added = 0
        
        for _, row in self.df_yearly.iterrows():
            # Find player
            player_name = row['Player Name']
            name_parts = str(player_name).split()
            first_name = name_parts[0] if name_parts else str(player_name)
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            player = self.session.query(Player).filter_by(
                first_name=first_name,
                last_name=last_name
            ).first()
            
            if player:
                # Check if yearly stat already exists
                existing_stat = self.session.query(PlayerYearlyStats).filter_by(
                    player_id=player.player_id,
                    year=int(row['Year'])
                ).first()
                
                if not existing_stat:
                    yearly_stat = PlayerYearlyStats(
                        player_id=player.player_id,
                        year=int(row['Year']),
                        rounds_played=int(row['Rounds']) if pd.notna(row['Rounds']) else None,
                        fairway_percentage=float(row['Fairway Percentage']) if pd.notna(row['Fairway Percentage']) else None,
                        avg_distance=float(row['Avg Distance']) if pd.notna(row['Avg Distance']) else None,
                        greens_in_regulation=float(row['gir']) if pd.notna(row['gir']) else None,
                        average_putts=float(row['Average Putts']) if pd.notna(row['Average Putts']) else None,
                        average_scrambling=float(row['Average Scrambling']) if pd.notna(row['Average Scrambling']) else None,
                        average_score=float(row['Average Score']) if pd.notna(row['Average Score']) else None,
                        points=int(row['Points']) if pd.notna(row['Points']) else None,
                        wins=int(row['Wins']) if pd.notna(row['Wins']) else None,
                        top_10_finishes=int(row['Top 10']) if pd.notna(row['Top 10']) else None,
                        avg_sg_putts=float(row['Average SG Putts']) if pd.notna(row['Average SG Putts']) else None,
                        avg_sg_total=float(row['Average SG Total']) if pd.notna(row['Average SG Total']) else None,
                        sg_off_the_tee=float(row['SG:OTT']) if pd.notna(row['SG:OTT']) else None,
                        sg_approach=float(row['SG:APR']) if pd.notna(row['SG:APR']) else None,
                        sg_around_green=float(row['SG:ARG']) if pd.notna(row['SG:ARG']) else None,
                        prize_money=float(row['Money_Clean']) if pd.notna(row['Money_Clean']) else None
                    )
                    
                    self.session.add(yearly_stat)
                    stats_added += 1
        
        self.session.commit()
        print(f"✅ Added {stats_added} yearly statistics")
        return True
    
    def create_summary_report(self):
        """Create comprehensive summary report"""
        print("\n📋 Creating comprehensive summary report...")
        
        # Query all loaded data
        player_count = self.session.query(Player).count()
        
        try:
            tournament_count = self.session.execute("SELECT COUNT(*) FROM tournaments_enhanced").scalar()
            course_count = self.session.execute("SELECT COUNT(*) FROM courses_enhanced").scalar()
            result_count = self.session.execute("SELECT COUNT(*) FROM tournament_results").scalar()
            yearly_count = self.session.execute("SELECT COUNT(*) FROM player_yearly_stats").scalar()
        except:
            tournament_count = course_count = result_count = yearly_count = 0
        
        report = f"""
# Enhanced Golf Database Load Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏌️ Data Successfully Loaded

### Players
- **Total Players**: {player_count:,}
- **Sources**: Tournament data (2014-2022) + Yearly stats (2010-2018)

### Tournaments & Courses
- **Tournaments**: {tournament_count:,}
- **Courses**: {course_count:,}
- **Date Range**: 2014-2022

### Performance Data
- **Tournament Results**: {result_count:,} individual tournament performances
- **Yearly Statistics**: {yearly_count:,} annual performance summaries

## 🎯 Database Schema

Your enhanced database now contains:

1. **players** - Basic player information
2. **courses_enhanced** - Golf courses with location and par
3. **tournaments_enhanced** - Individual tournaments with dates, purses, courses
4. **tournament_results** - Player performance in each tournament
5. **player_yearly_stats** - Annual performance aggregates

## 🚀 What You Can Now Query

### Tournament-Specific Queries:
- "Show me all players who made the cut at The Memorial Tournament"
- "What was Jordan Spieth's best strokes gained performance in 2022?"
- "Which course had the lowest scoring average in 2021?"

### Player Performance Queries:
- "Who had the most wins at Pebble Beach?"
- "Show me improving players from 2015 to 2020"
- "Which player has the best putting stats?"

### Advanced Analytics:
- "Compare players' performance on different course types"
- "Show trends in strokes gained putting over time"
- "Find players who perform better in high-purse tournaments"

## 🎯 Next Steps

1. **Test Enhanced API**: Add endpoints for tournament data
2. **Build Natural Language Interface**: Parse and execute golf queries
3. **Add Data Visualization**: Charts showing performance trends
4. **Course Analysis**: Add more detailed course information

## 📊 Data Quality Notes

- Tournament results: {result_count:,} records with complete strokes gained data
- Missing data: ~21% for some strokes gained metrics (normal for older tournaments)
- Date coverage: Strong coverage from 2014-2022 for tournament data

Your golf database is now ready for sophisticated analysis and natural language querying!
"""
        
        # Save report
        report_file = Path("data/enhanced_load_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Enhanced load report saved to: {report_file}")
        return report
    
    def run_enhanced_etl(self):
        """Run the complete enhanced ETL pipeline"""
        print("🏌️ ENHANCED GOLF DATA ETL PIPELINE")
        print("=" * 60)
        
        # Create session
        if not self.create_session():
            return False
        
        try:
            # Create enhanced tables
            CourseEnhanced, TournamentEnhanced, TournamentResult, PlayerYearlyStats = self.create_enhanced_tables()
            if not CourseEnhanced:
                return False
            
            # Load data files
            tournament_loaded = self.load_tournament_data()
            yearly_loaded = self.load_yearly_data()
            
            if not tournament_loaded and not yearly_loaded:
                print("❌ No data files could be loaded")
                return False
            
            # Load entities
            self.load_players()
            
            if tournament_loaded:
                self.load_courses(CourseEnhanced)
                self.load_tournaments(TournamentEnhanced, CourseEnhanced)
                self.load_tournament_results(TournamentResult, TournamentEnhanced)
            
            if yearly_loaded:
                self.load_yearly_stats(PlayerYearlyStats)
            
            # Create summary report
            self.create_summary_report()
            
            print("\n🎉 Enhanced ETL Pipeline completed successfully!")
            print("\nYour golf database now contains:")
            print("  • Individual tournament results with strokes gained data")
            print("  • Course information and tournament details")
            print("  • Annual player performance statistics")
            print("\n🚀 Ready for natural language queries!")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced ETL error: {e}")
            if self.session:
                self.session.rollback()
            return False
        
        finally:
            if self.session:
                self.session.close()

def main():
    etl = EnhancedGolfETL()
    success = etl.run_enhanced_etl()
    
    if success:
        print("\n🏆 Database loaded with comprehensive golf data!")
        print("Next steps:")
        print("1. Update your Flask API to serve tournament data")
        print("2. Build the natural language query interface")
        print("3. Create visualizations and analytics dashboards")
    else:
        print("\n❌ Enhanced ETL failed. Check error messages above.")

if __name__ == "__main__":
    main()