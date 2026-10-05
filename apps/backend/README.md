# DocuFlow — Backend

API et worker Python pour l'extraction, la validation et l'export de données documentaires.

---

## Stack

| Outil | Rôle |
|---|---|
| Python 3.12 | Langage |
| FastAPI | Framework API |
| SQLAlchemy | ORM |
| Alembic | Migrations de base de données |
| PostgreSQL 18 | Base de données |
| uv | Gestion des dépendances |
| ruff | Linter et formateur |
| pytest | Tests |

---

## Structure

```
apps/backend/
├── src/docuflow/
│   ├── api/          # Routes et dépendances HTTP
│   ├── core/         # Configuration et journalisation
│   ├── db/           # Connexion et modèles SQLAlchemy
│   ├── extractors/   # Interface commune et moteurs d'extraction
│   ├── schemas/      # Schémas Pydantic (entrées / résultats)
│   ├── services/     # Logique métier (import, extraction, export)
│   ├── storage/      # Accès aux fichiers originaux
│   └── worker.py     # Point d'entrée des traitements en arrière-plan
├── migrations/       # Migrations Alembic
├── tests/            # Tests unitaires et d'intégration
├── .env              # Variables locales (non versionné)
├── .env.example      # Template des variables d'environnement
└── pyproject.toml    # Dépendances et configuration
```

---

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker (pour PostgreSQL en local)

---

## Installation

```bash
# Depuis la racine du dépôt
cd apps/backend

# Installer les dépendances
uv sync

# Copier les variables d'environnement
cp .env.example .env
```

Ajuster les valeurs dans `.env` si nécessaire.

---

## Lancer PostgreSQL

```bash
# Depuis la racine du dépôt
docker compose up -d db
```

---

## Démarrer l'API

```bash
uv run uvicorn docuflow.main:app --reload
```

L'API est accessible sur `http://localhost:8000`.  
La documentation interactive est disponible sur `http://localhost:8000/docs`.

---

## Lancer les tests

```bash
uv run pytest
```

---

## Linter et formateur

```bash
# Vérifier
uv run ruff check .

# Formater
uv run ruff format .
```

---

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `APP_ENV` | Environnement (`development`, `production`) | `development` |
| `APP_DEBUG` | Mode debug | `true` |
| `APP_SECRET_KEY` | Clé secrète de l'application | — |
| `DATABASE_URL` | URL de connexion PostgreSQL | — |
| `STORAGE_PATH` | Chemin de stockage des fichiers | `./storage` |
| `CORS_ORIGINS` | Origines autorisées (séparées par une virgule) | `http://localhost:3000` |
