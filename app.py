from flask import Flask, jsonify, request, render_template_string
from db import SessionLocal, engine
from models import Team, Match, MatchStats, Base
from analyze import compare_teams

app = Flask(__name__)

# Route pour initialiser la base de données (à appeler une seule fois)
@app.route('/init-db')
def init_db():
    Base.metadata.create_all(bind=engine)
    return jsonify({"status": "Tables créées avec succès"})

# Page d'accueil avec interface utilisateur
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analyse de Match - API-Football</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 30px auto;
                padding: 20px;
                background: #f9fbfd;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .info {
                background: #e8f4fc;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 14px;
            }
            .input-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 6px;
                font-weight: bold;
                color: #2980b9;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 14px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #2980b9;
            }
            #result {
                margin-top: 25px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 14px;
                max-height: 400px;
                overflow: auto;
                border: 1px solid #ddd;
            }
            .loading {
                text-align: center;
                color: #e67e22;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>🔍 Analyse de Match - API-Football</h1>
        
        <div class="info">
            <strong>IDs d'équipes utiles :</strong><br>
            PSG = 85, OM = 91, Real Madrid = 541, Barça = 529, Man Utd = 33, Liverpool = 40
        </div>

        <div class="input-group">
            <label for="team1">ID Équipe 1</label>
            <input type="number" id="team1" placeholder="Ex: 85 (PSG)" />
        </div>
        <div class="input-group">
            <label for="team2">ID Équipe 2</label>
            <input type="number" id="team2" placeholder="Ex: 91 (OM)" />
        </div>
        <button onclick="analyser()">Lancer l'analyse</button>

        <div id="result"></div>

        <script>
            async function analyser() {
                const t1 = document.getElementById("team1").value;
                const t2 = document.getElementById("team2").value;
                const resultDiv = document.getElementById("result");

                if (!t1 || !t2) {
                    alert("Veuillez entrer deux IDs d'équipes.");
                    return;
                }

                resultDiv.innerHTML = '<div class="loading">🔄 Collecte des données... (cela peut prendre 20-30 secondes)</div>';

                try {
                    // Collecte les deux équipes
                    await fetch(`/collect/team/${t1}?max=10`, { method: "POST" });
                    await fetch(`/collect/team/${t2}?max=10`, { method: "POST" });

                    // Compare
                    const res = await fetch(`/compare/${t1}/${t2}`);
                    const data = await res.json();

                    if (data.error) {
                        resultDiv.textContent = "Erreur : " + data.error;
                    } else {
                        resultDiv.textContent = JSON.stringify(data, null, 2);
                    }
                } catch (err) {
                    resultDiv.textContent = "❌ Erreur de connexion : " + err.message;
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    session = SessionLocal()
    t = session.query(Team).filter_by(sofascore_id=team_id).first()
    if not t:
        return jsonify({'error': 'team not found'}), 404
    return jsonify({'sofascore_id': t.sofascore_id, 'name': t.name})

@app.route('/collect/team/<int:team_id>', methods=['POST'])
def collect_team(team_id):
    from collector import fetch_and_store_team
    max_events = int(request.args.get('max', 10))
    fetch_and_store_team(team_id, max_events=max_events)
    return jsonify({'status': 'started'})

@app.route('/compare')
def compare_query():
    a = request.args.get('team_a')
    b = request.args.get('team_b')
    if not a or not b:
        return jsonify({'error': 'team_a and team_b required'}), 400
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
