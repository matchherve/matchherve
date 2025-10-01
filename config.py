import os

DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
SOFASCORE_BASE = 'https://api.sofascore.com/api/v1'
REQUEST_DELAY = float(os.environ.get('REQUEST_DELAY', '1.5'))  # secondes entre requêtes
USER_AGENT = os.environ.get('USER_AGENT', 'Mozilla/5.0 (compatible; IA-Predictor/1.0)')
