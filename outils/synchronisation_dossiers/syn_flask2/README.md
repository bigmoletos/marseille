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

### Utilisation des volumes Docker

L'application utilise des volumes nommés pour les dossiers à synchroniser. Pour copier des fichiers vers ou depuis ces volumes, vous pouvez utiliser le script `copy_to_volumes.bat` (Windows) :

1. Exécutez le script en double-cliquant dessus
2. Suivez les instructions à l'écran pour copier des fichiers vers/depuis les volumes

## Structure des volumes

- `sync-folders-source` : Volume pour les fichiers source à synchroniser
- `sync-folders-dest` : Volume pour les fichiers de destination
- `sync-folders-data` : Volume pour les données persistantes de l'application

## Utilisation de l'interface web

Une fois l'application démarrée, accédez à http://localhost:5000 pour ouvrir l'interface web.

1. Configurez les paramètres de synchronisation (si nécessaire)
2. Exécutez la synchronisation en cliquant sur le bouton approprié
3. Consultez les résultats et les journaux de synchronisation

## Configuration avancée

Pour personnaliser l'application, vous pouvez modifier les variables d'environnement dans le fichier `compose.yml` :

- `PORT` : Port sur lequel l'application sera exposée (par défaut : 5000)
- `FLASK_ENV` : Environnement Flask (production ou development)
- `DOCKERHUB_USERNAME` : Nom d'utilisateur Docker Hub pour l'image

## Résolution des problèmes

### Erreur de montage de volume

Si vous rencontrez des erreurs liées aux volumes sous Windows, utilisez le script `copy_to_volumes.bat` pour gérer les fichiers au lieu de monter directement des chemins Windows.

### Container qui se termine immédiatement

Vérifiez les journaux du conteneur avec la commande :

```bash
docker logs sync-folders-app
```

## Développement

Pour développer localement sans Docker, suivez ces étapes :

1. Créez un environnement virtuel Python
2. Installez les dépendances : `pip install -r requirements.txt`
3. Exécutez l'application : `python app.py`