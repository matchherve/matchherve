from db import SessionLocal
from models import Team, Match, MatchStats
from sqlalchemy import or_, desc

session = SessionLocal()

def recent_matches_for_team(sofa_id, limit=10):
    t = session.query(Team).filter_by(sofascore_id=sofa_id).first()
    if not t:
        return []
    matches = session.query(Match).filter(or_(Match.home_team_id==t.id, Match.away_team_id==t.id)).order_by(desc(Match.event_date)).limit(limit).all()
    return matches

def compute_team_stats(sofa_id, limit=10):
    matches = recent_matches_for_team(sofa_id, limit)
    if not matches:
        return None
    total = {'possession_for':0,'possession_against':0,'shots_for':0,'shots_against':0,'fouls_for':0,'fouls_against':0,'corners_for':0,'corners_against':0,'count':0}
    for m in matches:
        if not m.stats:
            continue
        is_home = (m.home_team.sofascore_id == sofa_id)
        if is_home:
            total['possession_for'] += (m.stats.possession_home or 0)
            total['possession_against'] += (m.stats.possession_away or 0)
            total['shots_for'] += (m.stats.shots_home or 0)
            total['shots_against'] += (m.stats.shots_away or 0)
            total['fouls_for'] += (m.stats.fouls_home or 0)
            total['fouls_against'] += (m.stats.fouls_away or 0)
            total['corners_for'] += (m.stats.corners_home or 0)
            total['corners_against'] += (m.stats.corners_away or 0)
        else:
            total['possession_for'] += (m.stats.possession_away or 0)
            total['possession_against'] += (m.stats.possession_home or 0)
            total['shots_for'] += (m.stats.shots_away or 0)
            total['shots_against'] += (m.stats.shots_home or 0)
            total['fouls_for'] += (m.stats.fouls_away or 0)
            total['fouls_against'] += (m.stats.fouls_home or 0)
            total['corners_for'] += (m.stats.corners_away or 0)
            total['corners_against'] += (m.stats.corners_home or 0)
        total['count'] += 1

    c = total['count'] or 1
    avg = {k: (v / c if k != 'count' else v) for k,v in total.items()}
    return avg

def compare_teams(team_a_id, team_b_id, recent=8):
    a_stats = compute_team_stats(team_a_id, limit=recent)
    b_stats = compute_team_stats(team_b_id, limit=recent)
    if not a_stats or not b_stats:
        return {'error':'insufficient data for one or both teams'}

    score_a = 0.5 * ((a_stats['possession_for'] - b_stats['possession_for'])/100) + 1.2 * ((a_stats['shots_for'] - b_stats['shots_for'])/max(1,(a_stats['shots_for']+b_stats['shots_for']))) + 0.3 * ((a_stats['corners_for'] - b_stats['corners_for'])/max(1,(a_stats['corners_for']+b_stats['corners_for'])))
    fouls_diff = (b_stats['fouls_for'] - a_stats['fouls_for'])/max(1,(a_stats['fouls_for']+b_stats['fouls_for']))
    score_a += 0.1 * fouls_diff

    base = 1
    a_raw = max(0, base + score_a)
    b_raw = max(0, base - score_a)
    draw_raw = 0.6
    s = a_raw + b_raw + draw_raw
    pa = a_raw / s
    pd = draw_raw / s
    pb = b_raw / s

    return {
        'team_a_id': team_a_id,
        'team_b_id': team_b_id,
        'probabilities': {
            'team_a_win': round(pa,3),
            'draw': round(pd,3),
            'team_b_win': round(pb,3)
        },
        'a_stats': a_stats,
        'b_stats': b_stats
  }
