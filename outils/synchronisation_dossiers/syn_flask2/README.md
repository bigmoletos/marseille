# Application de Synchronisation de Dossiers

Cette application Flask permet de synchroniser des dossiers en utilisant une interface web. Elle est containerisée avec Docker pour faciliter son déploiement.

## Installation et exécution

### Prérequis

- Docker Desktop installé et en cours d'exécution
- Une connaissance de base de Docker et des conteneurs

### Démarrage de l'application

1. Clonez ce dépôt dans un répertoire de votre choix
2. Depuis le répertoire de l'application, exécutez la commande suivante :

```bash
docker compose up -d
```

L'application sera disponible à l'adresse : http://localhost:5000

## Méthodes d'utilisation

L'application peut être utilisée de trois manières différentes :

### 1. Script shell direct (Linux/WSL)

Utilisez le script `sync_folders.sh` directement sous Linux ou WSL :

```bash
# Pour comparer des dossiers
./sync_folders.sh compare "S:/sauve_dossier2" "S:/sauve_dossier3" "A vers B" "./output.json"

# Pour synchroniser des dossiers
./sync_folders.sh sync "S:/sauve_dossier2" "S:/sauve_dossier3" "A vers B" "./output.json"
```

### 2. Script Python via CLI

Utilisez le script Python `syn_folders_to_container.py` pour une interface en ligne de commande :

```bash
# Lancer la synchronisation via Python
python syn_folders_to_container.py --source "S:/sauve_dossier2" --dest "S:/sauve_dossier3" --mode "A vers B"
```

### 3. Interface web avec Flask

Lancez l'application Flask (`app.py`) pour utiliser l'interface web :

```bash
# Exécution directe (hors conteneur)
python app.py

# Via Docker (recommandé)
docker compose up -d
```

Puis accédez à http://localhost:5000 dans votre navigateur.

## Structure des volumes

- `sync-folders-source` : Volume pour les fichiers source à synchroniser
- `sync-folders-dest` : Volume pour les fichiers de destination
- `sync-folders-data` : Volume pour les données persistantes de l'application

## Description des fichiers du projet

| Fichier | Description |
|---------|-------------|
| **sync_folders.sh** | Script shell principal permettant de comparer et synchroniser des dossiers sous Linux/WSL. Gère la conversion des chemins Windows en chemins Unix et utilise rsync pour les opérations. |
| **syn_folders_to_container.py** | Script Python qui sert d'interface en ligne de commande pour la synchronisation des dossiers. |
| **app.py** | Application Flask qui fournit l'interface web pour la synchronisation des dossiers. |
| **relance_winnat.ps1** | Script PowerShell qui redémarre le service Windows NAT (winnat) pour résoudre les problèmes de connexion réseau avec Docker sous Windows. |
| **entrypoint.sh** | Script d'entrée pour le conteneur Docker, qui initialise l'environnement, vérifie les dépendances, et configure les permissions. |
| **Dockerfile** | Définit l'image Docker pour l'application, en utilisant une approche multi-étapes pour minimiser la taille de l'image finale. |
| **compose.yml** | Configuration Docker Compose qui définit les services, réseaux et volumes nécessaires pour l'application. |
| **copy_to_volumes.bat** | Script Windows qui facilite la copie de fichiers vers et depuis les volumes Docker. |
| **.env** | Fichier de configuration contenant les variables d'environnement pour l'application. |

## Utilisation de l'interface web

Une fois l'application démarrée, accédez à http://localhost:5000 pour ouvrir l'interface web.

1. Configurez les paramètres de synchronisation (source, destination, mode)
2. Cliquez sur "Comparer les Dossiers" pour voir les différences
3. Cliquez sur "Lancer la Synchronisation" pour effectuer la synchronisation
4. Consultez les résultats et les journaux de synchronisation

## Configuration avancée

Pour personnaliser l'application, vous pouvez modifier les variables d'environnement dans le fichier `.env` :

- `PORT` : Port sur lequel l'application sera exposée (par défaut : 5000)
- `FLASK_ENV` : Environnement Flask (production ou development)
- `SOURCE_DIR` : Chemin vers le dossier source (par exemple: S:/sauve_dossier2)
- `DEST_DIR` : Chemin vers le dossier destination (par exemple: S:/sauve_dossier4)
- `DOCKERHUB_USERNAME` : Nom d'utilisateur Docker Hub pour l'image

## Résolution des problèmes

### Erreur de montage de volume

Si vous rencontrez des erreurs liées aux volumes sous Windows, utilisez le script `copy_to_volumes.bat` pour gérer les fichiers au lieu de monter directement des chemins Windows.

### Problèmes de réseau Docker sous Windows

Si vous rencontrez des problèmes de connexion réseau avec Docker :
1. Exécutez le script `relance_winnat.ps1` en tant qu'administrateur pour redémarrer le service NAT de Windows
2. Redémarrez Docker Desktop après l'exécution du script

### Container qui se termine immédiatement

Vérifiez les journaux du conteneur avec la commande :

```bash
docker logs sync-folders-app
```

## Documentation

La documentation complète générée à partir des docstrings du code est disponible dans le dossier `docs/`. Pour générer ou mettre à jour cette documentation, exécutez :

```bash
# Installation de pydoc-markdown (si nécessaire)
pip install pydoc-markdown

# Génération de la documentation
pydoc-markdown -I . -m app -m syn_folders_to_container --render-toc > docs/documentation.md
```

## Développement

Pour développer localement sans Docker, suivez ces étapes :

1. Créez un environnement virtuel Python
2. Installez les dépendances : `pip install -r requirements.txt`
3. Exécutez l'application : `python app.py`