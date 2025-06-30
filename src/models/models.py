"""
SQLAlchemy models for Golf Database
"""
from sqlalchemy import create_engine, Column, Integer, String, Date, Decimal, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
ECHO is off.
    player_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    nationality = Column(String(3))
    birth_date = Column(Date)
    turned_professional_date = Column(Date)
    height_cm = Column(Integer)
    world_ranking = Column(Integer)
    career_earnings = Column(Decimal(12,2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
ECHO is off.
    # Relationships
    tournament_entries = relationship("TournamentEntry", back_populates="player")
ECHO is off.
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
ECHO is off.
    def __repr__(self):
        return f"^<Player^({self.full_name}^)^>"

class Course(Base):
    __tablename__ = 'courses'
ECHO is off.
    course_id = Column(Integer, primary_key=True)
    course_name = Column(String(100), nullable=False)
    location = Column(String(100))
    country = Column(String(3))
    par = Column(Integer)
    yardage = Column(Integer)
    course_rating = Column(Decimal(4,1))
    slope_rating = Column(Integer)
    architect = Column(String(100))
    established_year = Column(Integer)
    greens_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
ECHO is off.
    def __repr__(self):
        return f"^<Course^({self.course_name}^)^>"

class Tournament(Base):
    __tablename__ = 'tournaments'
ECHO is off.
    tournament_id = Column(Integer, primary_key=True)
    tournament_name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    prize_money_usd = Column(Integer)
    field_size = Column(Integer)
    cut_line = Column(Integer)
    winning_score = Column(Integer)
    weather_conditions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
ECHO is off.
    # Relationships
    course = relationship("Course")
    entries = relationship("TournamentEntry", back_populates="tournament")
ECHO is off.
    def __repr__(self):
        return f"^<Tournament^({self.tournament_name}^)^>"

class TournamentEntry(Base):
    __tablename__ = 'tournament_entries'
ECHO is off.
    entry_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    final_position = Column(Integer)
    total_score = Column(Integer)
    prize_money = Column(Decimal(10,2))
    made_cut = Column(Boolean, default=False)
    rounds_played = Column(Integer)
ECHO is off.
    # Relationships
    tournament = relationship("Tournament", back_populates="entries")
    player = relationship("Player", back_populates="tournament_entries")
    rounds = relationship("Round")

class Round(Base):
    __tablename__ = 'rounds'
ECHO is off.
    round_id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('tournament_entries.entry_id'))
    round_number = Column(Integer, nullable=False)
    score = Column(Integer)
    strokes_gained_total = Column(Decimal(5,2))
    fairways_hit = Column(Integer)
    greens_in_regulation = Column(Integer)
    putts = Column(Integer)
    date_played = Column(Date)
