from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    sofascore_id = Column(Integer, unique=True, index=True)
    name = Column(String)

    matches_home = relationship('Match', back_populates='home_team', foreign_keys='Match.home_team_id')
    matches_away = relationship('Match', back_populates='away_team', foreign_keys='Match.away_team_id')

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True, index=True)
    sofascore_id = Column(Integer, unique=True, index=True)
    event_date = Column(DateTime)
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    home_score = Column(Integer)
    away_score = Column(Integer)
    competition = Column(String)

    home_team = relationship('Team', foreign_keys=[home_team_id])
    away_team = relationship('Team', foreign_keys=[away_team_id])
    stats = relationship('MatchStats', back_populates='match', uselist=False)

class MatchStats(Base):
    __tablename__ = 'match_stats'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    possession_home = Column(Float)
    possession_away = Column(Float)
    shots_home = Column(Integer)
    shots_away = Column(Integer)
    fouls_home = Column(Integer)
    fouls_away = Column(Integer)
    corners_home = Column(Integer)
    corners_away = Column(Integer)

    match = relationship('Match', back_populates='stats')
