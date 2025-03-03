# Guide d'utilisation avec Docker

Ce document détaille les procédures pour déployer, configurer et utiliser l'application de synchronisation de dossiers avec Docker.

## Table des matières

- [Installation de Docker](#installation-de-docker)
- [Configuration et démarrage](#configuration-et-démarrage)
- [Gestion des volumes](#gestion-des-volumes)
- [Résolution des problèmes](#résolution-des-problèmes)
- [Administration](#administration)

## Installation de Docker

### Windows

1. Téléchargez et installez [Docker Desktop pour Windows](https://www.docker.com/products/docker-desktop)
2. Assurez-vous que WSL 2 est activé (recommandé)
3. Lancez Docker Desktop et vérifiez qu'il fonctionne correctement

### Linux

```bash
# Mise à jour des paquets
sudo apt update

# Installation des dépendances
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Ajout du dépôt Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Installation de Docker
sudo apt update
sudo apt install docker-ce docker-compose

# Ajout de l'utilisateur au groupe docker
sudo usermod -aG docker ${USER}
```

## Configuration et démarrage

### Préparation

1. Clonez ou téléchargez le dépôt du projet
2. Accédez au répertoire de l'application
3. Modifiez le fichier `.env` pour configurer les chemins des dossiers à synchroniser:

```properties
# Exemple de .env
SOURCE_DIR=S:/sauve_dossier2
DEST_DIR=S:/sauve_dossier4
PORT=5000
```

### Construction de l'image

```bash
# Construction de l'image Docker
docker compose build
```

### Lancement de l'application

```bash
# Démarrage de l'application
docker compose up -d

# Vérification de l'état
docker compose ps

# Affichage des logs
docker compose logs -f
```

## Gestion des volumes

L'application utilise des volumes Docker pour persister les données et les dossiers à synchroniser.

### Volumes utilisés

- Les dossiers source et destination sont montés en tant que volumes
- Un volume de données est utilisé pour stocker les informations de l'application

### Utilisation de copy_to_volumes.bat

Le script `copy_to_volumes.bat` facilite la copie de fichiers vers/depuis les volumes Docker sous Windows:

1. Double-cliquez sur le script pour le lancer
2. Suivez les instructions à l'écran:
   - Option 1: Copier vers le volume source
   - Option 2: Copier vers le volume destination
   - Option 3: Extraire depuis le volume source
   - Option 4: Extraire depuis le volume destination

### Inspection des volumes

```bash
# Lister tous les volumes
docker volume ls

# Inspecter un volume
docker volume inspect sync-folders-data
```

## Résolution des problèmes

### Problèmes de réseau

Si l'application n'est pas accessible ou si les conteneurs ne peuvent pas communiquer:

1. Utilisez le script `relance_winnat.ps1` sous Windows:
   ```powershell
   # Exécuter en tant qu'administrateur
   .\relance_winnat.ps1
   ```

2. Redémarrez Docker Desktop
3. Redémarrez l'application:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Problèmes de montage de volumes

Si les volumes ne sont pas correctement montés:

1. Vérifiez que les chemins dans le fichier `.env` sont corrects
2. Utilisez la syntaxe appropriate pour votre système d'exploitation:
   - Windows: `C:/chemin/vers/dossier`
   - Linux: `/chemin/vers/dossier`

3. Essayez d'utiliser des volumes nommés plutôt que des montages directs

### Logs du conteneur

Pour diagnostiquer des problèmes:

```bash
# Afficher les logs complets
docker logs sync-folders-app

# Suivre les logs en temps réel
docker logs -f sync-folders-app
```

## Administration

### Maintenance des conteneurs

```bash
# Arrêter l'application
docker compose down

# Supprimer les volumes (attention: perte de données)
docker compose down -v

# Reconstruire l'image sans cache
docker compose build --no-cache
```

### Partage de l'image Docker

```bash
# Se connecter à Docker Hub
docker login

# Pousser l'image sur Docker Hub
docker push ${DOCKERHUB_USERNAME}/sync-folders:latest
```

### Mise à jour de l'application

1. Tirez les dernières modifications du dépôt
2. Reconstruisez l'image Docker
3. Redémarrez l'application:
   ```bash
   git pull
   docker compose build
   docker compose down
   docker compose up -d
   ```