import os

DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
API_FOOTBALL_KEY = os.environ.get('API_FOOTBALL_KEY', '')
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"
