# syntax=docker/dockerfile:1

# ÉTAPE 1: Base minimale pour compiler les dépendances avec Alpine Linux
FROM python:3.11-alpine AS compile-image

# Installation des dépendances de compilation uniquement
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev

# ÉTAPE 2: Installation des dépendances Python
FROM compile-image AS build-image

# Empêcher Python d'écrire des fichiers .pyc et d'utiliser le buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copier app.py pour référence (même si nous n'utilisons pas scriptkit)
COPY app.py ./

# Installer les dépendances Python standard
RUN pip install --no-cache-dir \
    flask>=2.0.0 \
    gunicorn>=20.1.0 \
    requests>=2.27.1 \
    pandas>=1.4.0 \
    numpy>=1.22.0 \
    urllib3>=1.26.8 \
    && find /usr/local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local -name "*.pyc" -delete \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# ÉTAPE 3: Image finale ultra-légère
FROM python:3.11-alpine AS final

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    SYNC_MODE=container

# Métadonnées
LABEL maintainer="bigmoletos" \
      version="1.0" \
      description="Synchronisation de dossiers avec Flask"

WORKDIR /app

# Installation des dépendances d'exécution uniquement - ajout de rsync et jq
RUN apk add --no-cache tini libstdc++ tzdata rsync jq wget \
    && mkdir -p /app/data /app/logs /sync/source /sync/dest \
    && chmod -R 777 /app/data /app/logs \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Création d'un utilisateur non-privilégié
RUN adduser -D -h /app -s /sbin/nologin appuser

# Copie sélective des fichiers Python nécessaires du builder
COPY --from=build-image /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build-image /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copie du script d'entrée
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copie des fichiers de l'application
COPY --chown=appuser:appuser . .

# Élimination des répertoires inutiles pour l'exécution
RUN find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /app -name "*.pyc" -delete \
    && rm -rf /app/tests /app/.pytest_cache /app/.coverage /app/htmlcov 2>/dev/null || true \
    && chmod -R 755 /app \
    && chown -R appuser:appuser /app/data /app/logs

# IMPORTANT: Nous utilisons root pour résoudre le problème de permissions
USER root

# Exposition du port
EXPOSE ${PORT}

# Démarrage de l'application avec Tini pour éviter les processus zombies
ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=2", "--threads=4", "--timeout", "60", "--log-level=info", "app:app"]