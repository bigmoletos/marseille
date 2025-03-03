# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "flask",
#     "pandas",
#     "numpy",
#     "urllib3",
#     "gunicorn>=20.1.0",
# ]
# ///
"""Application Flask pour la synchronisation de dossiers.

Cette application fournit une interface web pour synchroniser des dossiers.

Requires:
    - Python 3.6+
    - Flask
    - syn_folders_to_container.py dans le même répertoire

Auteur: bigmoletos
Version: 1.0.0-a2
Date de création: 2024-02-21
Dernière modification: 2025-03-02
Licence: Propriétaire

"""

import json
import os
import platform
import subprocess
from pathlib import Path, PureWindowsPath
from flask import Flask, render_template, request, jsonify, session
import datetime
import shutil
from typing import List, Dict
import uuid

# Import depuis le même répertoire
import syn_folders_to_container
from syn_folders_to_container import (compare_folders, sync_folders, SyncError,
                                      setup_logging, logger, convert_path,
                                      check_path, generate_folder_json,
                                      compare_json_folders)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
OUTPUT_FILE = os.path.join(DATA_DIR, "comparison_result.json")

# Configurer le dossier de données
app.config['UPLOAD_FOLDER'] = DATA_DIR
app.config[
    'MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB pour les uploads

# Dictionnaire global pour stocker la correspondance des chemins (fallback si session non disponible)
# La clé est un identifiant unique de session, la valeur est un dictionnaire des chemins
PATH_MAPPINGS = {}


# Détecter le mode de fonctionnement (Docker ou local)
def is_running_in_docker():
    """Vérifier si l'application s'exécute dans un conteneur Docker."""
    try:
        with open('/proc/self/cgroup', 'r') as procfile:
            for line in procfile:
                if '/docker' in line:
                    return True
        return os.path.exists('/.dockerenv') or os.environ.get(
            'SYNC_MODE') == 'container'
    except Exception:
        return os.environ.get('SYNC_MODE') == 'container'


# Indique si l'application fonctionne en mode conteneur
CONTAINER_MODE = is_running_in_docker()


def map_to_docker_path(windows_path):
    """
    Convertit un chemin Windows en chemin Docker monté.
    Utilise une approche générique qui fonctionne avec n'importe quels dossiers.

    Args:
        windows_path (str): Chemin Windows à convertir

    Returns:
        str: Chemin Docker correspondant
    """
    if not CONTAINER_MODE:
        return windows_path

    # Générer un ID de session si nécessaire
    session_id = session.get('session_id', None)
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['path_mapping'] = {}
        logger.warning(
            f"Création d'une nouvelle session à l'intérieur de map_to_docker_path: {session_id}"
        )

    # Récupérer ou initialiser le dictionnaire de mappages pour la session
    path_mapping = session.get('path_mapping', {})

    # Si le chemin est déjà connu, retourner son mappage
    if windows_path in path_mapping:
        logger.info(
            f"Utilisation du mappage existant: {windows_path} -> {path_mapping[windows_path]}"
        )
        return path_mapping[windows_path]

    # Pour les chemins commençant par S: on utilise un mapping direct
    if windows_path.upper().startswith('S:'):
        if windows_path.upper().startswith(
                'S:\\SAUVE_DOSSIER2') or windows_path.upper().startswith(
                    'S:/SAUVE_DOSSIER2'):
            docker_path = "/sync/source"
            logger.info(
                f"Mappage direct dossier source: {windows_path} -> {docker_path}"
            )
        elif windows_path.upper().startswith(
                'S:\\SAUVE_DOSSIER4') or windows_path.upper().startswith(
                    'S:/SAUVE_DOSSIER4'):
            docker_path = "/sync/dest"
            logger.info(
                f"Mappage direct dossier destination: {windows_path} -> {docker_path}"
            )
        else:
            # Sinon, utiliser la logique existante basée sur l'ordre
            existing_paths = len(path_mapping)

            if existing_paths == 0:
                # Premier chemin -> /sync/source
                docker_path = "/sync/source"
                logger.info(
                    f"Premier chemin mappé: {windows_path} -> {docker_path}")
            elif existing_paths == 1:
                # Deuxième chemin -> /sync/dest
                docker_path = "/sync/dest"
                logger.info(
                    f"Deuxième chemin mappé: {windows_path} -> {docker_path}")
            else:
                # Pour les chemins supplémentaires (cas non prévu), utiliser un mappage par défaut
                logger.warning(
                    f"Plus de deux chemins mappés! Utilisation du mappage par défaut pour: {windows_path}"
                )
                docker_path = "/sync/source"
    else:
        # Pour les autres lecteurs, on utilise la logique standard
        existing_paths = len(path_mapping)

        if existing_paths == 0:
            # Premier chemin -> /sync/source
            docker_path = "/sync/source"
            logger.info(
                f"Premier chemin mappé: {windows_path} -> {docker_path}")
        elif existing_paths == 1:
            # Deuxième chemin -> /sync/dest
            docker_path = "/sync/dest"
            logger.info(
                f"Deuxième chemin mappé: {windows_path} -> {docker_path}")
        else:
            # Pour les chemins supplémentaires (cas non prévu), utiliser un mappage par défaut
            logger.warning(
                f"Plus de deux chemins mappés! Utilisation du mappage par défaut pour: {windows_path}"
            )
            docker_path = "/sync/source"

    # Enregistrer le mappage pour utilisation future
    path_mapping[windows_path] = docker_path
    session['path_mapping'] = path_mapping

    # Sauvegarder également dans le dictionnaire global comme fallback
    if session_id not in PATH_MAPPINGS:
        PATH_MAPPINGS[session_id] = {}
    PATH_MAPPINGS[session_id][windows_path] = docker_path

    logger.info(f"Nouveau mappage créé: {windows_path} -> {docker_path}")
    return docker_path


def validate_path(path: str, description: str) -> tuple[bool, str]:
    """
    Valide un chemin générique (Windows ou Linux).

    Args:
        path (str): Chemin à valider
        description (str): Description pour les messages d'erreur

    Returns:
        tuple: (succès, message d'erreur)
    """
    try:
        if CONTAINER_MODE:
            # En mode conteneur, vérifier les chemins Docker
            path_obj = Path(path)
            if not path_obj.exists():
                error_msg = f"{description} n'existe pas: {path}"
                logger.error(error_msg)
                return False, error_msg

            if not path_obj.is_dir():
                error_msg = f"{description} n'est pas un dossier: {path}"
                logger.error(error_msg)
                return False, error_msg

            return True, ""
        else:
            # En mode normal, utiliser la validation Windows
            return validate_windows_path(path, description)
    except Exception as e:
        error_msg = f"Erreur lors de la validation du chemin {description}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def validate_windows_path(path: str, description: str) -> tuple[bool, str]:
    """
    Valide un chemin Windows.

    Args:
        path (str): Chemin Windows à valider
        description (str): Description pour les messages d'erreur

    Returns:
        tuple: (succès, message d'erreur)
    """
    try:
        # Si nous sommes en mode conteneur, rediriger vers la validation Docker
        if CONTAINER_MODE:
            docker_path = map_to_docker_path(path)
            return validate_path(docker_path, description)

        # Pour les chemins réseau, on fait confiance
        if path.startswith('\\\\') or path.startswith('//') or ':' in path[:2]:
            # Vérification standard pour Windows
            path_obj = Path(path)

            if not path_obj.exists():
                error_msg = f"{description} n'existe pas: {path}"
                logger.error(error_msg)
                return False, error_msg

            if not path_obj.is_dir():
                error_msg = f"{description} n'est pas un dossier: {path}"
                logger.error(error_msg)
                return False, error_msg

            return True, ""

    except Exception as e:
        error_msg = f"Erreur lors de la validation du chemin {description}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        logger.info("Répertoires créés avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création des répertoires: {str(e)}")
        raise


@app.route('/')
def index():
    """Page d'accueil avec le formulaire de synchronisation."""
    # Réinitialiser la session pour chaque nouvelle visite
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['path_mapping'] = {}
    logger.info(f"Nouvelle session créée: {session_id}")

    return render_template('index.html')


@app.route('/compare_folders', methods=['POST'])
def compare_folders_route():
    """Route pour comparer les dossiers."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']

        # Validation des chemins
        if CONTAINER_MODE:
            # En mode conteneur, utiliser les chemins Docker
            docker_source = map_to_docker_path(source_dir)
            docker_dest = map_to_docker_path(dest_dir)

            source_valid, source_error = validate_path(docker_source, "Source")
            if not source_valid:
                return render_template('index.html', error=source_error)

            dest_valid, dest_error = validate_path(docker_dest, "Destination")
            if not dest_valid:
                return render_template('index.html', error=dest_error)

            # Utiliser les chemins Docker pour la comparaison
            source_dir_bash = docker_source
            dest_dir_bash = docker_dest
        else:
            # Validation en mode normal (Windows)
            source_valid, source_error = validate_windows_path(
                source_dir, "Source")
            if not source_valid:
                return render_template('index.html', error=source_error)

            dest_valid, dest_error = validate_windows_path(
                dest_dir, "Destination")
            if not dest_valid:
                return render_template('index.html', error=dest_error)

            # Convertir les chemins pour Git Bash
            source_dir_bash = convert_path(source_dir)
            dest_dir_bash = convert_path(dest_dir)

        # Adapter le mode
        mode_mapping = {
            'A vers B (sauvegarde)': 'A vers B',
            'B vers A (restauration)': 'B vers A',
            'Bidirectionnel (miroir)': 'A idem B'
        }
        mode_syn = mode_mapping.get(mode, 'A vers B')

        # Chemin du fichier de sortie
        output_file = os.path.join(DATA_DIR, "comparison_result.json")

        # Lancer la comparaison
        compare_folders(source_dir_bash, dest_dir_bash, mode_syn, output_file)

        # Charger les résultats
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        # Récupérer les listes de fichiers
        to_create = result.get('to_create', [])
        to_update = result.get('to_update', [])
        to_delete = result.get('to_delete', [])

        # Préparer l'objet de résultat pour le template
        comparison_result = {
            'source_dir': source_dir,
            'dest_dir': dest_dir,
            'mode': mode,
            'to_create': to_create,
            'to_update': to_update,
            'to_delete': to_delete,
            'nombre_to_create': len(to_create),
            'nombre_to_update': len(to_update),
            'nombre_to_delete': len(to_delete)
        }

        # Afficher le résultat
        return render_template('index.html',
                               comparison_result=comparison_result,
                               source_dir=source_dir,
                               dest_dir=dest_dir,
                               mode=mode)

    except SyncError as e:
        logger.error(f"Erreur de synchronisation: {str(e)}")
        return render_template('index.html', error=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison: {str(e)}", exc_info=True)
        return render_template('index.html', error=f"Erreur: {str(e)}")


def perform_sync(source_dir: str, dest_dir: str, mode: str) -> None:
    """
    Effectue la synchronisation entre les dossiers.

    Args:
        source_dir (str): Dossier source
        dest_dir (str): Dossier destination
        mode (str): Mode de synchronisation
    """
    try:
        # Vérifier si nous sommes en mode conteneur
        if CONTAINER_MODE:
            # Utiliser les chemins Docker
            docker_source = map_to_docker_path(source_dir)
            docker_dest = map_to_docker_path(dest_dir)

            # Valider les chemins
            source_valid, source_error = validate_path(docker_source, "Source")
            if not source_valid:
                raise SyncError(source_error)

            dest_valid, dest_error = validate_path(docker_dest, "Destination")
            if not dest_valid:
                raise SyncError(dest_error)

            # Chemin du fichier de sortie
            output_file = os.path.join(DATA_DIR, "sync_result.json")

            # Lancer la synchronisation avec les chemins Docker
            sync_folders(docker_source, docker_dest, mode, output_file)
        else:
            # Validation en mode normal (Windows)
            source_valid, source_error = validate_windows_path(
                source_dir, "Source")
            if not source_valid:
                raise SyncError(source_error)

            dest_valid, dest_error = validate_windows_path(
                dest_dir, "Destination")
            if not dest_valid:
                raise SyncError(dest_error)

            # Convertir les chemins pour Git Bash
            source_dir_bash = convert_path(source_dir)
            dest_dir_bash = convert_path(dest_dir)

            # Chemin du fichier de sortie
            output_file = os.path.join(DATA_DIR, "sync_result.json")

            # Lancer la synchronisation
            sync_folders(source_dir_bash, dest_dir_bash, mode, output_file)

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation: {str(e)}")
        raise


@app.route('/sync_folders', methods=['POST'])
def sync_folders_route():
    """Route pour synchroniser les dossiers."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']

        # Adapter le mode
        mode_mapping = {
            'A vers B (sauvegarde)': 'A vers B',
            'B vers A (restauration)': 'B vers A',
            'Bidirectionnel (miroir)': 'A idem B'
        }
        mode_syn = mode_mapping.get(mode, 'A vers B')

        # Effectuer la synchronisation
        perform_sync(source_dir, dest_dir, mode_syn)

        # Charger les résultats
        with open(os.path.join(DATA_DIR, "sync_result.json"),
                  'r',
                  encoding='utf-8') as f:
            result = json.load(f)

        # Récupérer les listes de fichiers
        to_create = result.get('to_create', [])
        to_update = result.get('to_update', [])
        to_delete = result.get('to_delete', [])

        # Préparer l'objet de résultat pour le template
        sync_result = {
            'source_dir': source_dir,
            'dest_dir': dest_dir,
            'mode': mode,
            'to_create': to_create,
            'to_update': to_update,
            'to_delete': to_delete,
            'nombre_to_create': len(to_create),
            'nombre_to_update': len(to_update),
            'nombre_to_delete': len(to_delete),
            'status': 'Terminé avec succès'
        }

        # Afficher le résultat
        return render_template('index.html',
                               sync_result=sync_result,
                               source_dir=source_dir,
                               dest_dir=dest_dir,
                               mode=mode,
                               success="Synchronisation terminée avec succès")

    except SyncError as e:
        logger.error(f"Erreur de synchronisation: {str(e)}")
        return render_template('index.html', error=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation: {str(e)}",
                     exc_info=True)
        return render_template('index.html', error=f"Erreur: {str(e)}")


@app.errorhandler(404)
def not_found_error(error):
    """Gestion des erreurs 404."""
    return render_template('index.html', error="Page non trouvée"), 404


@app.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500."""
    return render_template('index.html',
                           error="Erreur interne du serveur"), 500


if __name__ == '__main__':
    try:
        # Redémarrer winnat en exécutant le script PowerShell avec privilèges admin
        try:
            logger.info("Redémarrage de winnat...")
            # Chemin du script PowerShell
            script_path = os.path.join(SCRIPT_DIR, "relance_winnat.ps1")

            # Vérifier que le script existe
            if not os.path.exists(script_path):
                raise FileNotFoundError(
                    f"Le script {script_path} n'existe pas")

            # Exécuter le script PowerShell avec privilèges administrateur
            process = subprocess.run([
                'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-File', script_path
            ],
                                     capture_output=True,
                                     text=True)

            # Vérifier si l'exécution a réussi
            if process.returncode == 0:
                logger.info("Redémarrage de winnat effectué avec succès")
                if process.stdout:
                    logger.info(f"Sortie du script: {process.stdout}")
            else:
                logger.error(
                    f"Erreur lors du redémarrage de winnat: {process.stderr}")
                logger.warning(
                    "L'application continue malgré l'erreur de winnat")

        except Exception as e:
            logger.error(f"Erreur lors du redémarrage de winnat: {str(e)}")
            logger.warning("L'application continue malgré l'erreur de winnat")

        # Initialisation
        ensure_directories()
        setup_logging()
        logger.info("Application démarrée avec succès")

        # Démarrage de l'application
        # Si nous sommes en développement (pas dans Docker)
        if not is_running_in_docker():
            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            # En production (Docker), pas de debug pour de meilleures performances
            app.run(host='0.0.0.0', port=5000, debug=False)

    except Exception as e:
        logger.critical(
            f"Erreur fatale lors du démarrage de l'application: {str(e)}",
            exc_info=True)
        raise
