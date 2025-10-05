import requests
from db import SessionLocal
from models import Team, Match, MatchStats
from config import API_FOOTBALL_KEY, API_FOOTBALL_HOST
from sqlalchemy.exc import IntegrityError
from datetime import datetime

headers = {
    'X-RapidAPI-Key': API_FOOTBALL_KEY,
    'X-RapidAPI-Host': API_FOOTBALL_HOST
}

session = SessionLocal()

def ensure_team(team_id, name):
    t = session.query(Team).filter_by(sofascore_id=team_id).first()
    if not t:
        t = Team(sofascore_id=team_id, name=name)
        session.add(t)
        session.commit()
    return t

def fetch_and_store_team(team_id, max_events=10):
    if not API_FOOTBALL_KEY:
        raise Exception("Clé API-Football manquante")

    # Récupérer les derniers matchs
    url = f"https://{API_FOOTBALL_HOST}/v3/fixtures"
    params = {"team": team_id, "last": max_events}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    fixtures = r.json()['response']

    for fix in fixtures:
        fixture_id = fix['fixture']['id']
        
        # Récupérer les stats du match
        stats_obj = {
            'possession_home': None, 'possession_away': None,
            'shots_home': 0, 'shots_away': 0,
            'fouls_home': 0, 'fouls_away': 0,
            'corners_home': 0, 'corners_away': 0
        }

        stats_url = f"https://{API_FOOTBALL_HOST}/v3/fixtures/statistics"
        stats_r = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
        if stats_r.status_code == 200:
            stats_data = stats_r.json()['response']
            if stats_data:
                for team_stat in stats_data:
                    side = 'home' if team_stat['team']['id'] == fix['teams']['home']['id'] else 'away'
                    for stat in team_stat['statistics']:
                        t = stat['type']
                        v = stat['value']
                        if t == 'Ball Possession':
                            stats_obj[f'possession_{side}'] = float(str(v).replace('%', '') or 0)
                        elif t == 'Total Shots':
                            stats_obj[f'shots_{side}'] = int(v or 0)
                        elif t == 'Fouls':
                            stats_obj[f'fouls_{side}'] = int(v or 0)
                        elif t == 'Corners':
                            stats_obj[f'corners_{side}'] = int(v or 0)

        # Sauvegarder le match
        home_team = ensure_team(fix['teams']['home']['id'], fix['teams']['home']['name'])
        away_team = ensure_team(fix['teams']['away']['id'], fix['teams']['away']['name'])

        dt = datetime.fromisoformat(fix['fixture']['date'].replace('Z', '+00:00'))
        home_score = fix['goals']['home']
        away_score = fix['goals']['away']

        m = Match(
            sofascore_id=fixture_id,
            event_date=dt,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            home_score=home_score,
            away_score=away_score,
            competition=fix['league']['name']
        )
        session.add(m)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            m = session.query(Match).filter_by(sofascore_id=fixture_id).first()

        # Sauvegarder les stats
        if m:
            ms = session.query(MatchStats).filter_by(match_id=m.id).first()
            if not ms:
                ms = MatchStats(
                    match_id=m.id,
                    possession_home=stats_obj['possession_home'],
                    possession_away=stats_obj['possession_away'],
                    shots_home=stats_obj['shots_home'],
                    shots_away=stats_obj['shots_away'],
                    fouls_home=stats_obj['fouls_home'],
                    fouls_away=stats_obj['fouls_away'],
                    corners_home=stats_obj['corners_home'],
                    corners_away=stats_obj['corners_away']
                )
                session.add(ms)
                session.commit()
