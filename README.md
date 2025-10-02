# 📊 Analyse de Matchs - Backend Flask

Ce projet est un backend Flask conçu pour **analyser les matchs de football** en utilisant des **données légales et fiables** (API-Football).  
Il collecte les statistiques avancées des équipes (possession, tirs, corners, etc.), stocke les données dans une base PostgreSQL,  
et fournit des endpoints API pour comparer les équipes et prédire les résultats.

## 🔑 Fonctionnalités

- ✅ **Collecte légale** via [API-Football](https://rapidapi.com/api-sports/api/api-football) (100 requêtes/jour gratuites)
- 💾 **Stockage persistant** dans **PostgreSQL** (compatible avec Render)
- 📈 **Analyse comparative** : possession moyenne, tirs, corners, fautes
- 🌐 **Endpoints REST** :
  - `GET /compare/team_a_id/team_b_id` → prédiction + stats
  - `POST /collect/team/team_id` → mise à jour manuelle des données
- 🔒 **Sécurité** : clé API stockée dans les variables d’environnement

## 🗂️ Structure du projet

- `app.py`          → Serveur Flask principal
- `collector.py`    → Collecte les données depuis API-Football
- `analyze.py`      → Logique de comparaison et prédiction
- `models.py`       → Modèles SQLAlchemy (Team, Match, MatchStats)
- `db.py`           → Connexion à la base de données
- `config.py`       → Configuration (clé API, URL de la base)
- `requirements.txt`→ Dépendances (sans pandas, avec psycopg2)
- `Procfile`        → Configuration pour Render
- `.gitignore`      → Exclusion des fichiers sensibles

## 🚀 Déploiement

1. Crée un compte gratuit sur [RapidAPI](https://rapidapi.com/)
2. Abonne-toi à [API-Football](https://rapidapi.com/api-sports/api/api-football) (plan gratuit)
3. Copie ta clé API dans les **variables d’environnement de Render** :
