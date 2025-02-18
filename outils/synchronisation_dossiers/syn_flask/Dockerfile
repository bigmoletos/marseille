FROM debian:stable-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3-full \
    python3-pip \
    python3-venv \
    rsync \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création et définition du répertoire de travail
WORKDIR /app

# Copie des fichiers nécessaires
COPY . .

# Création et activation de l'environnement virtuel
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Installation des dépendances Python dans l'environnement virtuel
RUN pip3 install --no-cache-dir -r requirements.txt

# Rendre le script exécutable
RUN chmod +x sync_folders.sh

# Variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
# Chemin explicite vers rsync dans le conteneur
ENV RSYNC_PATH=/usr/bin/rsync

# Port exposé
EXPOSE 5001

# Commande de démarrage
CMD ["/app/venv/bin/python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]