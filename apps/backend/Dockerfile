FROM python:3.12-slim

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copier les fichiers de dépendances en premier pour bénéficier du cache Docker
COPY pyproject.toml uv.lock README.md ./

# Installer les dépendances sans le package lui-même
RUN uv sync --frozen --no-dev --no-install-project

# Copier le code source
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Installer le package
RUN uv sync --frozen --no-dev

# Créer le dossier de stockage
RUN mkdir -p /app/storage

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "docuflow.main:app", "--host", "0.0.0.0", "--port", "8000"]
