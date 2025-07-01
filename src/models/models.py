from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.types import Numeric  # Use Numeric instead of Decimal for SQLAlchemy 2.x
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    nationality = Column(String(50))
    birth_date = Column(Date)
    turned_professional_date = Column(Date)
    height_cm = Column(Integer)
    world_ranking = Column(Integer)
    career_earnings = Column(Numeric(12, 2))  # Using Numeric instead of Decimal
    
    # Relationships
    tournament_entries = relationship("TournamentEntry", back_populates="player")
    rounds = relationship("Round", back_populates="player")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Player(player_id={self.player_id}, name='{self.full_name}', nationality='{self.nationality}')>"

class Course(Base):
    __tablename__ = 'courses'
    
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)
    location = Column(String(100))
    country = Column(String(50))
    par = Column(Integer)
    yardage = Column(Integer)
    course_rating = Column(Float)
    slope_rating = Column(Integer)
    architect = Column(String(100))
    established_year = Column(Integer)
    greens_type = Column(String(50))
    
    # Relationships
    tournaments = relationship("Tournament", back_populates="course")
    
    def __repr__(self):
        return f"<Course(course_id={self.course_id}, name='{self.course_name}', location='{self.location}')>"

class Tournament(Base):
    __tablename__ = 'tournaments'
    
    tournament_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    prize_money_usd = Column(Numeric(12, 2))  # Using Numeric instead of Decimal
    field_size = Column(Integer)
    cut_line = Column(Integer)
    winning_score = Column(Integer)
    
    # Relationships
    course = relationship("Course", back_populates="tournaments")
    tournament_entries = relationship("TournamentEntry", back_populates="tournament")
    rounds = relationship("Round", back_populates="tournament")
    
    def __repr__(self):
        return f"<Tournament(tournament_id={self.tournament_id}, name='{self.tournament_name}', start_date='{self.start_date}')>"

class TournamentEntry(Base):
    __tablename__ = 'tournament_entries'
    
    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), nullable=False)
    entry_date = Column(Date)
    entry_status = Column(String(20))  # 'confirmed', 'withdrawn', 'missed_cut'
    final_position = Column(Integer)
    total_score = Column(Integer)
    prize_money_won = Column(Numeric(10, 2))  # Using Numeric instead of Decimal
    made_cut = Column(Boolean)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_entries")
    player = relationship("Player", back_populates="tournament_entries")
    
    def __repr__(self):
        return f"<TournamentEntry(entry_id={self.entry_id}, tournament_id={self.tournament_id}, player_id={self.player_id})>"

class Round(Base):
    __tablename__ = 'rounds'
    
    round_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), nullable=False)
    round_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    score = Column(Integer)  # Total strokes for the round
    par_score = Column(Integer)  # Score relative to par (e.g., -2, +1)
    round_date = Column(Date)
    tee_time = Column(DateTime)
    completed = Column(Boolean, default=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="rounds")
    player = relationship("Player", back_populates="rounds")
    
    def __repr__(self):
        return f"<Round(round_id={self.round_id}, tournament_id={self.tournament_id}, player_id={self.player_id}, round={self.round_number})>"