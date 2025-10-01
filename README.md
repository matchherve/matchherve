# Flask Sofascore Backend

Ce projet est un backend Flask conçu pour analyser les matchs de football. 
Il collecte les statistiques des équipes depuis Sofascore, stocke les données dans une base de données, 
et fournit des endpoints API pour comparer les équipes et prédire les résultats.

## Fonctionnalités

- Collecte automatique des anciens matchs et statistiques des équipes
- Stockage des données dans SQLite (ou PostgreSQL pour Render)
- Endpoints Flask pour récupérer les équipes et leurs statistiques
- Analyse comparative entre deux équipes

## Structure du projet

- `app.py` : serveur Flask principal
- `collector.py` : script de collecte des matchs et statistiques
- `models.py` : définition des tables SQLAlchemy
- `db.py` : connexion à la base de données
- `analyze.py` : fonctions pour l’analyse des équipes
- `config.py` : configuration globale
- `requirements.txt` : dépendances Python
- `Procfile` : configuration pour Render
- `run_collector.sh` : script pour exécuter le collecteur périodiquement
