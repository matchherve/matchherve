import os

# Forcer l'utilisation de DATABASE_URL sur Render
DB_URL = os.environ.get('DATABASE_URL')

if not DB_URL:
    # En local, on utilise SQLite
    DB_URL = 'sqlite:///data.db'
else:
    # Sur Render, corrige l'URL PostgreSQL pour SQLAlchemy
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

SOFASCORE_BASE = 'https://api.sofascore.com/api/v1'
REQUEST_DELAY = float(os.environ.get('REQUEST_DELAY', '1.5'))
USER_AGENT = os.environ.get('USER_AGENT', 'Mozilla/5.0 (compatible; IA-Predictor/1.0)')
