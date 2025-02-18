# Cheatsheet : Debugging Docker API sur Serveur Ubuntu

## Commandes de Base

### Afficher les logs d'un conteneur
```bash
docker logs api_modelisation
```

### Afficher les logs détaillés (Nouvelles commandes)

#### 1. Logs en temps réel (suivre les logs)
```bash
# Pour l'API IHM
docker logs -f api_ihm

# Pour l'API Modélisation
docker logs -f api_modelisation

# Pour les tests
docker logs -f api_ihm_test
```

#### 2. Afficher les dernières lignes des logs
```bash
# Dernières 100 lignes pour l'IHM
docker logs --tail 100 api_ihm

# Dernières 100 lignes pour l'API
docker logs --tail 100 api_modelisation

# Dernières 100 lignes pour les tests
docker logs --tail 100 api_ihm_test
```

#### 3. Logs avec horodatage
```bash
# Logs avec timestamps pour l'IHM
docker logs -t api_ihm

# Logs avec timestamps pour l'API
docker logs -t api_modelisation

# Logs avec timestamps pour les tests
docker logs -t api_ihm_test
```

#### 4. Logs depuis une certaine date
```bash
# Logs depuis les 30 dernières minutes
docker logs --since 30m api_ihm
docker logs --since 30m api_modelisation
docker logs --since 30m api_ihm_test
```

#### 5. Filtrer les logs par niveau
```bash
# Filtrer les erreurs uniquement
docker logs api_ihm 2>&1 | grep ERROR
docker logs api_modelisation 2>&1 | grep ERROR
docker logs api_ihm_test 2>&1 | grep ERROR
```

#### 6. Sauvegarder les logs dans un fichier
```bash
# Sauvegarder les logs de l'IHM
docker logs api_ihm > ihm_logs.txt

# Sauvegarder les logs de l'API
docker logs api_modelisation > api_logs.txt

# Sauvegarder les logs des tests
docker logs api_ihm_test > test_logs.txt
```

#### Options utiles pour les logs
- `-f` ou `--follow` : Suivre les logs en temps réel
- `--tail N` : Afficher les N dernières lignes
- `-t` ou `--timestamps` : Ajouter les horodatages
- `--since` : Logs depuis une certaine date
- `--until` : Logs jusqu'à une certaine date
- `--details` : Ajouter les détails supplémentaires

Exemple de commande combinée :
```bash
# Suivre les logs en temps réel avec horodatage et détails
docker logs -f -t --details api_ihm
```

### Lister les conteneurs actifs
```bash
docker ps
```

### Lister tous les conteneurs (actifs et arrêtés)
```bash
docker ps -a
```

### Obtenir les ports exposés par le conteneur
```bash
docker inspect api_modelisation | grep HostPort
```

---

## Utilisation avec Docker Compose

### Vérifier la configuration d'un fichier Docker Compose
```bash
docker-compose -f docker-compose.test.yml config
```

### Relancer les services définis dans Docker Compose
```bash
docker-compose up --force-recreate --build
```

### Arrêter et supprimer les conteneurs, réseaux et volumes liés
```bash
docker-compose down -v
```


## Commandes de Filtrage

### Filtrer les conteneurs par nom
```bash
docker ps --filter "name=api_modelisation"
# ou
docker ps -a --filter "ancestor=76f849a84ff3"

```

### Vérifier l'état d'un conteneur spécifique savoir s'il est run ou non
```bash
docker inspect --format='{{.State.Status}}' api_modelisation
```

---

# Pour vérifier et mettre à jour la VM avec la dernière version, suivez ces étapes :

D'abord, vérifiez la version actuelle de XGBoost sur la VM :

```bash
# Se connecter au conteneur api_modelisation
docker exec -it api_modelisation bash

# Vérifier la version de XGBoost installée
docker inspect --format='{{.State.Status}}' api_modelisation

# 2. Si ce n'est pas la bonne version, reconstruisez l'image avec --no-cache :

# Arrêter les conteneurs
docker-compose down

# Supprimer les images existantes
docker rmi projet_qualite_air_api_modelisation

# Reconstruire sans cache
docker-compose build --no-cache api_modelisation

# Redémarrer les services
docker-compose up -d

# Vérifiez les logs pendant le build pour confirmer l'installation de XGBoost 1.7.3 :

# Voir les logs du conteneur
docker logs api_modelisation
```

---

## Déboguer les Réseaux

### Lister les réseaux Docker
```bash
docker network ls
```

### Inspecter un réseau Docker
```bash
docker network inspect <nom_du_reseau>
```

---

## Déboguer les Volumes

### Lister les volumes Docker
```bash
docker volume ls
```

### Inspecter un volume Docker
```bash
docker volume inspect <nom_du_volume>
```

---

## Dépannage Avancé

### Vérifier les événements Docker en temps réel
```bash
docker events
```

### Entrer dans un conteneur en cours d'exécution
```bash
docker exec -it api_modelisation /bin/bash
```

### Redémarrer un conteneur
```bash
docker restart api_modelisation
```

### Supprimer un conteneur
```bash
docker rm api_modelisation
```

### Supprimer une image Docker
```bash
docker rmi <image_id>
```

---

## Conseils Généraux

1. **Vérifiez les logs fréquemment** : Les logs sont souvent la première source d'information pour déboguer.
   ```bash
   docker logs api_modelisation
   ```

2. **Utilisez des filtres pour simplifier vos recherches** : Par exemple, utilisez `--filter` pour cibler des conteneurs ou des réseaux spécifiques.

3. **Nettoyez les ressources inutilisées** :
   ```bash
   docker system prune -a
   ```
   Cette commande supprime les conteneurs arrêtés, les images inutilisées et les réseaux inutiles.

---

## debug erreur : Une tentative d'accès à un socket de manière interdite par ses autorisations d'accès a été tentée

```bash
erreur:
PS C:\AJC_projets\projet_qualite_air\services\api_ihm\src> python api_ihm.py
 * Debug mode: on
Une tentative d'accès à un socket de manière interdite par ses autorisations d'accès a été tentée

ou avec un autre message:
"C:\Users\romar\AppData\Local\Programs\Python\Python312\Lib\socketserver.py", line 473, in server_bind
    self.socket.bind(self.server_address)
PermissionError: [WinError 10013] Une tentative d'accès à un socket de manière interdite par ses autorisations d'accès a été tentée
```

### actions correctives sous windows powershell en mode administrateur:

utilisation des ports :

```bash
netstat -ano
```

Redémarrez les services réseau :

```bash
net stop winnat
net start winnat
```

# Cheatsheet : Debugging Docker

## Débogage Docker sous Windows avec WSL

### Problèmes courants et solutions

#### 1. Erreur de démarrage du daemon Docker
```powershell
# Dans PowerShell (Administrateur)
# Arrêter tous les processus
wsl --shutdown
taskkill /F /IM "Docker Desktop.exe"
taskkill /F /IM "com.docker.service"
taskkill /F /IM "com.docker.cli"

# Redémarrer Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

#### 2. Erreur WSL "Failed to mount"
```powershell
# Dans PowerShell (Administrateur)
# Réinitialisation complète de WSL
wsl --shutdown
wsl --unregister Ubuntu
wsl --update
wsl --set-default-version 2
wsl --install Ubuntu

# Dans le nouveau terminal Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io -y
sudo usermod -aG docker $USER
sudo service docker start
```

#### 3. Activation de systemd dans WSL
```bash
# Éditer /etc/wsl.conf
sudo nano /etc/wsl.conf

# Ajouter ces lignes
[boot]
systemd=true

# Redémarrer WSL depuis PowerShell
wsl --shutdown
wsl
```

#### 4. Problèmes de permissions Docker
```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier les permissions
groups
docker ps
```

#### 5. Redémarrage complet de Docker
```powershell
# Dans PowerShell (Administrateur)
net stop "com.docker.service"
wsl --shutdown
net start "com.docker.service"
```

## Commandes de Nettoyage Docker

### Nettoyage complet
```bash
# Arrêter tous les conteneurs
docker stop $(docker ps -a -q)

# Supprimer tous les conteneurs
docker rm $(docker ps -a -q)

# Supprimer toutes les images
docker rmi $(docker images -q)

# Supprimer tous les volumes
docker volume prune -f

# Nettoyer le système
docker system prune -a --volumes
```

### Nettoyage sélectif
```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune

# Supprimer les réseaux non utilisés
docker network prune
```

## Débogage des Performances

### Surveillance des ressources
```bash
# Statistiques en direct
docker stats

# Statistiques d'un conteneur spécifique
docker stats <container_name>

# Inspecter les limites de ressources
docker inspect <container_name> | grep -A 20 "HostConfig"
```

### Gestion de la mémoire
```bash
# Voir la consommation mémoire
docker stats --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Limiter la mémoire d'un conteneur
docker update --memory 512m <container_name>
```

## Erreurs de Build et Pull d'Images

### 1. Erreur "failed to resolve source metadata"
```bash
# Problème de résolution d'image
# 1. Vérifier la connexion internet
ping 8.8.8.8

# 2. Vérifier le DNS Docker
docker run --rm busybox nslookup docker.io

# 3. Forcer la mise à jour du cache Docker
docker pull --platform linux/amd64 debian:stable-slim

# 4. Alternative : utiliser une image spécifique
# Remplacer dans le Dockerfile :
# FROM debian:slim
# par :
FROM debian:stable-slim
# ou
FROM debian:bullseye-slim
```

### 2. Erreurs de Registry
```bash
# Vérifier le statut de Docker Hub
curl -v https://registry-1.docker.io/v2/

# Nettoyer le cache des images
docker builder prune -a

# Forcer la reconstruction sans cache
docker-compose build --no-cache --pull

# Vérifier la configuration du registry
docker info | grep Registry
```

### 3. Problèmes de réseau pendant le build
```bash
# Vérifier la configuration réseau Docker
docker network ls
docker network inspect bridge

# Reconfigurer le DNS Docker
# Éditer /etc/docker/daemon.json :
{
    "dns": ["8.8.8.8", "8.8.4.4"]
}

# Redémarrer Docker
sudo service docker restart
```

## Construction et Lancement d'Images

### 1. Construction d'Images
```bash
# Construction simple
docker build -t nom_image .

# Construction avec tag spécifique
docker build -t nom_image:version .

# Construction sans cache
docker build --no-cache -t nom_image .

# Construction multi-plateforme
docker buildx build --platform linux/amd64,linux/arm64 -t nom_image .

# Construction avec variables d'environnement
docker build --build-arg VAR=valeur -t nom_image .
```

### 2. Lancement avec Docker Run
```bash
# Lancement simple
docker run -d nom_image

# Lancement avec port mapping
docker run -d -p 5001:5001 nom_image

# Lancement avec variables d'environnement
docker run -d -e "VAR=valeur" nom_image

# Lancement avec volumes
docker run -d -v /chemin/local:/chemin/container nom_image

# Lancement avec nom personnalisé
docker run -d --name mon_container nom_image

# Lancement avec redémarrage automatique
docker run -d --restart unless-stopped nom_image
```

### 3. Gestion avec Docker Compose
```bash
# Construction des images
docker-compose build

# Construction sans cache
docker-compose build --no-cache

# Lancement des services
docker-compose up -d

# Arrêt des services
docker-compose down

# Reconstruction et lancement
docker-compose up -d --build

# Voir les logs
docker-compose logs -f
```

### 4. Exemples Pratiques
```bash
# Construction et lancement d'une application Flask
# 1. Construction
docker build -t mon_app_flask .

# 2. Lancement simple
docker run -d -p 5001:5001 mon_app_flask

# 3. Lancement avec volumes et variables
docker run -d \
    -p 5001:5001 \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/data:/app/data \
    -e FLASK_ENV=production \
    --name flask_app \
    --restart unless-stopped \
    mon_app_flask

# 4. Avec Docker Compose
docker-compose up -d --build
```

### 5. Commandes de Maintenance
```bash
# Voir les images construites
docker images

# Supprimer une image
docker rmi nom_image

# Voir les conteneurs en cours d'exécution
docker ps

# Voir tous les conteneurs
docker ps -a

# Arrêter un conteneur
docker stop nom_container

# Redémarrer un conteneur
docker restart nom_container

# Supprimer un conteneur
docker rm nom_container
```

### 6. Bonnes Pratiques
```bash
# 1. Toujours tagger les images
docker build -t mon_app:1.0 .

# 2. Utiliser des volumes pour les données persistantes
docker run -v $(pwd)/data:/app/data mon_app

# 3. Définir des healthchecks
docker run --health-cmd="curl -f http://localhost:5001/health || exit 1" mon_app

# 4. Limiter les ressources
docker run --memory=512m --cpus=0.5 mon_app

# 5. Utiliser des réseaux personnalisés
docker network create mon_reseau
docker run --network mon_reseau mon_app
```

## Reconstruction Complète des Conteneurs

### Procédure de reconstruction propre
```bash
# 1. Arrêter les conteneurs
docker-compose down

# 2. Nettoyer
docker system prune -f

# 3. Reconstruire
docker-compose build --no-cache

# 4. Démarrer
docker-compose up -d


# en 1 seule commande
docker-compose down ; docker system prune -f ; docker-compose build --no-cache ; docker-compose up -d ; docker-compose logs -f


# 5. Vérifier les logs
docker-compose logs -f
```

Cette séquence de commandes permet de :
1. Arrêter proprement tous les conteneurs
2. Nettoyer les ressources Docker inutilisées (conteneurs arrêtés, réseaux non utilisés, images en cache)
3. Reconstruire les images sans utiliser le cache
4. Démarrer les conteneurs en mode détaché

