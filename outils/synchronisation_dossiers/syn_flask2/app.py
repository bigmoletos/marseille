# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "flask",
#     "pandas",
#     "numpy",
#     "urllib3",
# ]
# ///
"""Application Flask pour la synchronisation de dossiers.

Cette application fournit une interface web pour synchroniser des dossiers.

Requires:
    - Python 3.6+
    - Flask
    - syn_folders_to_container.py dans le même répertoire

Auteur: bigmoletos
Version: 1.0.0-a1
Date de création: 2024-02-21
Dernière modification: 2025-03-02
Licence: Propriétaire

"""

import json
import os
import platform
import subprocess
from pathlib import Path, PureWindowsPath
from flask import Flask, render_template, request, jsonify
import datetime
import shutil
from typing import List

# Import depuis le même répertoire
import syn_folders_to_container
from syn_folders_to_container import (compare_folders, sync_folders, SyncError,
                                      setup_logging, logger, convert_path,
                                      check_path, generate_folder_json,
                                      compare_json_folders)

app = Flask(__name__)

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")

# Configurer le dossier de données
app.config['UPLOAD_FOLDER'] = DATA_DIR
app.config[
    'MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB pour les uploads


def validate_windows_path(path: str, description: str) -> tuple[bool, str]:
    """Valide un chemin Windows avant conversion.

    Args:
        path (str): Chemin à valider
        description (str): Description pour les messages d'erreur

    Returns:
        tuple[bool, str]: (valide, message d'erreur)
    """
    try:
        # Pour les chemins réseau, on fait confiance
        if path.startswith('\\\\') or path.startswith('//') or ':' in path[:2]:
            return True, ""

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
    return render_template('index.html')


@app.route('/compare_folders', methods=['POST'])
def compare_folders_route():
    """Route pour comparer les dossiers."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']

        # Validation des chemins Windows
        source_valid, source_error = validate_windows_path(
            source_dir, "Source")
        if not source_valid:
            return render_template('index.html', error=source_error)

        dest_valid, dest_error = validate_windows_path(dest_dir, "Destination")
        if not dest_valid:
            return render_template('index.html', error=dest_error)

        # Convertir les chemins pour Git Bash
        source_dir_bash = convert_path(source_dir)
        dest_dir_bash = convert_path(dest_dir)

        # Adapter le mode pour correspondre aux attentes du script
        mode_mapping = {
            "A vers B (sauvegarde)": "A vers B",
            "B vers A (restauration)": "B vers A",
            "Bidirectionnel (miroir)": "A idem B"
        }
        mode = mode_mapping.get(mode, mode)

        # Fichier de sortie temporaire pour la comparaison
        output_file = os.path.join(DATA_DIR, 'comparison_result.json')

        logger.info(f"""
Paramètres de comparaison:
- Source: {source_dir}
- Source (Bash): {source_dir_bash}
- Destination: {dest_dir}
- Destination (Bash): {dest_dir_bash}
- Mode: {mode}
- Fichier de sortie: {output_file}
""")

        # Utiliser directement la fonction compare_folders du module syn_folders_to_container
        # au lieu de notre logique personnalisée
        compare_folders(source_dir, dest_dir, mode, output_file)

        # Créer le résultat de la comparaison en utilisant les variables globales du module
        comparison_result = {
            'source_dir': source_dir,
            'dest_dir': dest_dir,
            'mode': mode,
            'to_create': syn_folders_to_container.to_create,
            'to_update': syn_folders_to_container.to_update,
            'to_delete': syn_folders_to_container.to_delete,
            'nombre_to_create': syn_folders_to_container.nombre_to_create,
            'nombre_to_update': syn_folders_to_container.nombre_to_update,
            'nombre_to_delete': syn_folders_to_container.nombre_to_delete
        }

        # Sauvegarder le résultat
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_result, f, indent=2)

        logger.info("Comparaison terminée avec succès")
        return render_template('index.html',
                               comparison_result=comparison_result,
                               source_dir=source_dir,
                               dest_dir=dest_dir,
                               mode=mode)

    except Exception as e:
        logger.error(f"Erreur lors de la comparaison: {str(e)}", exc_info=True)
        return render_template(
            'index.html',
            error=f"Erreur lors de la comparaison: {str(e)}",
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


def perform_sync(source_dir: str, dest_dir: str, mode: str) -> None:
    """Effectue la synchronisation des dossiers en utilisant la fonction sync_folders
    du module syn_folders_to_container.

    Args:
        source_dir (str): Chemin du dossier source
        dest_dir (str): Chemin du dossier destination
        mode (str): Mode de synchronisation
    """
    try:
        # Fichier de sortie pour la synchronisation
        output_file = os.path.join(DATA_DIR, 'temp_comparison.json')

        # Utiliser directement la fonction sync_folders du module syn_folders_to_container
        # au lieu d'implémenter notre propre logique
        sync_folders(source_dir, dest_dir, mode, output_file)

        logger.info(f"""
Synchronisation terminée:
- {syn_folders_to_container.nombre_to_create} éléments créés
- {syn_folders_to_container.nombre_to_update} éléments mis à jour
- {syn_folders_to_container.nombre_to_delete} éléments supprimés
""")

    except Exception as e:
        error_msg = f"Erreur lors de la synchronisation: {str(e)}"
        logger.error(error_msg)
        raise SyncError(error_msg)


@app.route('/sync_folders', methods=['POST'])
def sync_folders_route():
    """Route pour synchroniser les dossiers."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']

        # Validation des chemins Windows
        source_valid, source_error = validate_windows_path(
            source_dir, "Source")
        if not source_valid:
            return render_template('index.html', error=source_error)

        dest_valid, dest_error = validate_windows_path(dest_dir, "Destination")
        if not dest_valid:
            return render_template('index.html', error=dest_error)

        # Adapter le mode
        mode_mapping = {
            "A vers B (sauvegarde)": "A vers B",
            "B vers A (restauration)": "B vers A",
            "Bidirectionnel (miroir)": "A idem B"
        }
        mode = mode_mapping.get(mode, mode)

        # Fichier de sortie pour la synchronisation
        output_file = os.path.join(DATA_DIR, 'sync_result.json')

        logger.info(f"""
Paramètres de synchronisation:
- Source: {source_dir}
- Destination: {dest_dir}
- Mode: {mode}
- Fichier de sortie: {output_file}
""")

        # Effectuer la synchronisation
        perform_sync(source_dir, dest_dir, mode)

        # Créer le résultat de la synchronisation
        sync_result = {
            'status': 'success',
            'source_dir': source_dir,
            'dest_dir': dest_dir,
            'mode': mode,
            'to_create': syn_folders_to_container.to_create,
            'to_update': syn_folders_to_container.to_update,
            'to_delete': syn_folders_to_container.to_delete,
            'nombre_to_create': syn_folders_to_container.nombre_to_create,
            'nombre_to_update': syn_folders_to_container.nombre_to_update,
            'nombre_to_delete': syn_folders_to_container.nombre_to_delete,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Sauvegarder le résultat
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sync_result, f, indent=2)

        logger.info("Synchronisation terminée avec succès")
        success_message = "Synchronisation terminée avec succès"
        return render_template('index.html',
                               success=success_message,
                               sync_result=sync_result,
                               source_dir=source_dir,
                               dest_dir=dest_dir,
                               mode=mode)

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation: {str(e)}",
                     exc_info=True)
        return render_template(
            'index.html',
            error=f"Erreur lors de la synchronisation: {str(e)}",
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


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
        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as e:
        logger.critical(
            f"Erreur fatale lors du démarrage de l'application: {str(e)}",
            exc_info=True)
        raise
