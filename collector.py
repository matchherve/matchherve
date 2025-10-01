import time
import requests
from db import SessionLocal, engine
from models import Base, Team, Match, MatchStats
from config import SOFASCORE_BASE, REQUEST_DELAY, USER_AGENT
from sqlalchemy.exc import IntegrityError
from datetime import datetime

headers = { 'User-Agent': USER_AGENT }

Base.metadata.create_all(bind=engine)
session = SessionLocal()

def get_team_events(team_id):
    url = f"{SOFASCORE_BASE}/team/{team_id}/events"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_event_statistics(event_id):
    url = f"{SOFASCORE_BASE}/event/{event_id}/statistics"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def ensure_team(sofascore_id, name=None):
    t = session.query(Team).filter_by(sofascore_id=sofascore_id).first()
    if not t:
        t = Team(sofascore_id=sofascore_id, name=name or f"Team {sofascore_id}")
        session.add(t)
        session.commit()
    return t

def store_match(event_json):
    event_id = event_json.get('id') or event_json.get('eventId')
    if not event_id:
        return None

    existing = session.query(Match).filter_by(sofascore_id=event_id).first()
    if existing:
        return existing

    home = event_json.get('homeTeam') or event_json.get('home')
    away = event_json.get('awayTeam') or event_json.get('away')
    comp = event_json.get('competition', {}).get('name') if isinstance(event_json.get('competition'), dict) else event_json.get('competition')

    home_team = ensure_team(home.get('id'), home.get('name'))
    away_team = ensure_team(away.get('id'), away.get('name'))

    home_score = None
    away_score = None
    # différentes structures possibles : on tente la lecture
    if event_json.get('homeScore') is not None and event_json.get('awayScore') is not None:
        try:
            home_score = int(event_json.get('homeScore'))
            away_score = int(event_json.get('awayScore'))
        except:
            home_score = away_score = None

    dt = None
    if event_json.get('startTimestamp'):
        dt = datetime.fromtimestamp(int(event_json.get('startTimestamp')))

    m = Match(sofascore_id=event_id, event_date=dt, home_team_id=home_team.id, away_team_id=away_team.id, home_score=home_score, away_score=away_score, competition=comp)
    session.add(m)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        m = session.query(Match).filter_by(sofascore_id=event_id).first()

    return m

def fetch_and_store_team(team_id, max_events=50):
    print(f"Collecte pour team {team_id}...")
    events = get_team_events(team_id)
    results = events.get('events') or events.get('results') or events
    count = 0
    for e in results:
        if count >= max_events: break
        event_id = e.get('id') or e.get('eventId')
        try:
            ev_url = f"{SOFASCORE_BASE}/event/{event_id}"
            r = requests.get(ev_url, headers=headers)
            r.raise_for_status()
            event_json = r.json()

            m = store_match(event_json)

            time.sleep(REQUEST_DELAY)
            stats_json = get_event_statistics(event_id)

            stats_obj = { 'possession_home': None, 'possession_away': None, 'shots_home': 0, 'shots_away': 0, 'fouls_home':0, 'fouls_away':0, 'corners_home':0, 'corners_away':0 }
            if stats_json and stats_json.get('statistics'):
                for group in stats_json['statistics']:
                    for item in group.get('statisticsItems', []):
                        name = (item.get('name') or '').lower()
                        if 'possession' in name:
                            stats_obj['possession_home'] = float(item.get('home') or 0)
                            stats_obj['possession_away'] = float(item.get('away') or 0)
                        if 'shots' in name or 'tir' in name:
                            stats_obj['shots_home'] = int(item.get('home') or 0)
                            stats_obj['shots_away'] = int(item.get('away') or 0)
                        if 'foul' in name or 'faute' in name:
                            stats_obj['fouls_home'] = int(item.get('home') or 0)
                            stats_obj['fouls_away'] = int(item.get('away') or 0)
                        if 'corner' in name:
                            stats_obj['corners_home'] = int(item.get('home') or 0)
                            stats_obj['corners_away'] = int(item.get('away') or 0)

            if m:
                ms = session.query(MatchStats).filter_by(match_id=m.id).first()
                if not ms:
                    ms = MatchStats(match_id=m.id,
                                    possession_home=stats_obj['possession_home'],
                                    possession_away=stats_obj['possession_away'],
                                    shots_home=stats_obj['shots_home'],
                                    shots_away=stats_obj['shots_away'],
                                    fouls_home=stats_obj['fouls_home'],
                                    fouls_away=stats_obj['fouls_away'],
                                    corners_home=stats_obj['corners_home'],
                                    corners_away=stats_obj['corners_away'])
                    session.add(ms)
                    session.commit()

            count += 1
            time.sleep(REQUEST_DELAY)
        except Exception as ex:
            print('Erreur collect event', event_id, ex)
            time.sleep(REQUEST_DELAY)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python collector.py <sofascore_team_id> [max_events]')
        sys.exit(1)
    team = int(sys.argv[1])
    max_ev = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    fetch_and_store_team(team, max_events=max_ev)
