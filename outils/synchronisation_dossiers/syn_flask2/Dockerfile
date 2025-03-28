# syntax=docker/dockerfile:1

FROM python:3.11-alpine

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

# Installation des dépendances système
RUN apk add --no-cache tini libstdc++ tzdata rsync jq \
    && mkdir -p /app/data /app/logs \
    && chmod -R 777 /app/data /app/logs

# Copie du fichier requirements.txt avant les autres fichiers
# pour tirer parti du cache Docker
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie des autres fichiers de l'application
COPY . .

# Exposition du port
EXPOSE ${PORT}

# Démarrage de l'application avec Tini pour éviter les processus zombies
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["flask", "run", "--host=0.0.0.0"]