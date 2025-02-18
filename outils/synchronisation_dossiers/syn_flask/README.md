# Application de Synchronisation de Dossiers

## Description
Application web Flask permettant la synchronisation bidirectionnelle de dossiers, fonctionnant de manière autonome sur Windows et Linux via Docker. L'application utilise `rsync` pour une synchronisation efficace et fiable des fichiers.

## Fonctionnalités Principales
- Interface web intuitive pour la sélection des dossiers
- Trois modes de synchronisation :
  - A vers B (sauvegarde)
  - B vers A (restauration)
  - Bidirectionnel (miroir)
- Comparaison détaillée avant synchronisation
- Visualisation des différences entre dossiers
- Journalisation complète des opérations
- Support natif des chemins Windows et Linux
- Fonctionnement totalement indépendant du système d'exploitation

## Prérequis

### Windows
- Docker Desktop
  - Téléchargeable sur [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
  - Installation standard (pas besoin de WSL)
- 4 GB RAM minimum
- Virtualisation activée dans le BIOS

### Linux
- Docker Engine
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install docker.io docker-compose

  # Fedora
  sudo dnf install docker docker-compose

  # Arch Linux
  sudo pacman -S docker docker-compose
  ```
- Ajout de l'utilisateur au groupe docker
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```

### Commun aux deux systèmes
- Port 5001 disponible
- Connexion Internet pour le pull initial des images

## Installation

### 1. Récupération du projet
```bash
git clone <url_du_projet>
cd syn_flask
```

### 2. Configuration selon le système d'exploitation

#### Windows
```powershell
# Vérifier que Docker Desktop est en cours d'exécution
# Pas besoin de WSL, l'application fonctionne de manière native
```

#### Linux
```bash
# Vérifier que le service Docker est actif
sudo systemctl status docker
# Si inactif, démarrer le service
sudo systemctl start docker
```

## Démarrage

### 1. Construction et lancement
```bash
# Windows (PowerShell) ou Linux (Bash)
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### 2. Vérification du démarrage
```bash
# Vérifier que le conteneur est en cours d'exécution
docker ps | grep sync_app

# Vérifier les logs
docker-compose logs -f
```

### 3. Accès à l'application
Ouvrez votre navigateur et accédez à :
```
http://localhost:5001
```

## Utilisation

### 1. Interface Principale
- Sélectionnez le dossier source (A) via le bouton "Parcourir"
- Sélectionnez le dossier destination (B)
- Choisissez le mode de synchronisation
- Cliquez sur "Comparer les dossiers"

### 2. Gestion des Chemins
L'application gère automatiquement la conversion des chemins :
- Windows : `C:\Users\nom\Documents`
- Linux : `/home/nom/documents`

### 3. Comparaison et Synchronisation
L'application affiche :
- Fichiers à créer
- Fichiers à mettre à jour
- Fichiers à supprimer
- Fichiers à créer en sens inverse (mode bidirectionnel)

## Architecture

### Structure des Fichiers
```
syn_flask/
├── app.py                 # Application Flask principale
├── Dockerfile            # Configuration Docker multi-plateforme
├── docker-compose.yml    # Orchestration des services
├── requirements.txt      # Dépendances Python
├── sync_folders.sh       # Script de synchronisation
├── templates/            # Templates HTML
│   └── index.html       # Interface utilisateur
└── logs/                # Fichiers de logs
```

### Composants Principaux
1. **Interface Web (Flask)**
   - Gestion des requêtes HTTP
   - Rendu des templates
   - Traitement des formulaires

2. **Module de Synchronisation**
   - Utilisation de rsync intégré au conteneur
   - Conversion automatique des chemins selon l'OS
   - Gestion des erreurs multi-plateformes

3. **Système de Logging**
   - Logs applicatifs
   - Logs de synchronisation
   - Logs Docker

## Débogage

### Logs Application
```bash
# Windows (PowerShell) ou Linux (Bash)
docker-compose logs -f
```

### Problèmes Courants

#### 1. Erreur de Port
```bash
# Windows
netstat -ano | findstr 5001

# Linux
netstat -tulpn | grep 5001

# Solution : Modifier le port dans docker-compose.yml
```

#### 2. Erreurs de Permissions
```bash
# Windows
icacls "chemin_du_dossier" /grant Utilisateurs:F

# Linux
chmod -R 755 chemin_du_dossier
```

#### 3. Erreurs Docker
```bash
# Vérifier l'état de Docker
# Windows
Get-Service docker

# Linux
systemctl status docker
```

## Maintenance

### Mise à Jour
```bash
# Windows ou Linux
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Nettoyage
```bash
# Windows ou Linux
docker-compose down
docker system prune -a
```

## Sécurité
- Isolation complète via Docker
- Pas de dépendance au système hôte
- Validation des chemins selon l'OS
- Logs détaillés des opérations

## Support Multi-Plateforme
L'application est testée et validée sur :
- Windows 10/11
- Ubuntu 20.04+
- Debian 10+
- CentOS 8+
- Fedora 34+

## Contribution et Support
1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Versions
- 1.0.0 : Version initiale
- 1.1.0 : Support multi-plateforme
- 1.2.0 : Indépendance totale du système d'exploitation

## Auteurs
- Équipe de développement Marseille
- Contributeurs
- Contributeurs