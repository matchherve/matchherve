import os

DB_URL = os.environ.get('DATABASE_URL')
if not DB_URL:
    DB_URL = 'sqlite:///data.db'
else:
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Supprime SofaScore — on utilise API-Football
API_FOOTBALL_KEY = os.environ.get('API_FOOTBALL_KEY', '')
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"
