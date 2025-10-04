from flask import Flask, jsonify, request
from db import SessionLocal, engine
from models import Team, Match, MatchStats, Base
from analyze import compare_teams

app = Flask(__name__)

# Route temporaire pour initialiser la base (à appeler une seule fois)
@app.route('/init-db')
def init_db():
    Base.metadata.create_all(bind=engine)
    return jsonify({"status": "Tables créées avec succès"})

@app.route('/')
def home():
    return jsonify({"status": "OK", "message": "API-Football backend is running!"})

@app.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    session = SessionLocal()
    t = session.query(Team).filter_by(sofascore_id=team_id).first()
    if not t:
        return jsonify({'error':'team not found'}), 404
    return jsonify({'sofascore_id': t.sofascore_id, 'name': t.name})

@app.route('/collect/team/<int:team_id>', methods=['POST'])
def collect_team(team_id):
    from collector import fetch_and_store_team
    max_events = int(request.args.get('max', 50))
    fetch_and_store_team(team_id, max_events=max_events)
    return jsonify({'status':'started'})

@app.route('/compare')
def compare_query():
    a = request.args.get('team_a')
    b = request.args.get('team_b')
    if not a or not b:
        return jsonify({'error':'team_a and team_b required'}), 400
    result = compare_teams(int(a), int(b))
    return jsonify(result)

@app.route('/compare/<int:team_a_id>/<int:team_b_id>')
def compare_path(team_a_id, team_b_id):
    result = compare_teams(team_a_id, team_b_id)
    return jsonify(result)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
