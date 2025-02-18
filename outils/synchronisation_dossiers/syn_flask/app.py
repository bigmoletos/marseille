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

import logging
import sys
import traceback
import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for

# Configuration du logging avancé
logging.basicConfig(
    filename='flask_app.log',
    level=logging.DEBUG,
    format=
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Ajouter aussi le logging vers la console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Pour les messages flash

# Obtenir le chemin absolu du répertoire de l'application
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger.debug(f"Répertoire de l'application : {SCRIPT_DIR}")


def debug_list_host_directory():
    """Liste le contenu des répertoires montés pour le débogage."""
    try:
        logger.info("=== Vérification des lecteurs Windows ===")
        # Utilisation de dir pour lister les lecteurs sous Windows
        cmd = [
            'cmd', '/c', 'wmic', 'logicaldisk', 'get', 'caption,description'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Lecteurs disponibles :")
            logger.info(result.stdout)
        else:
            logger.error(
                f"Erreur lors de la lecture des lecteurs : {result.stderr}")

        # Pour chaque lecteur, vérifier son existence et son contenu
        for drive_letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                logger.info(f"=== Contenu du lecteur {drive_path} ===")
                try:
                    # Utiliser dir pour lister le contenu
                    cmd = ['cmd', '/c', 'dir', drive_path]
                    result = subprocess.run(cmd,
                                            capture_output=True,
                                            text=True)
                    if result.returncode == 0:
                        logger.info(result.stdout)
                    else:
                        logger.error(
                            f"Erreur lors du listage de {drive_path} : {result.stderr}"
                        )
                except Exception as e:
                    logger.error(
                        f"Erreur lors de l'accès au lecteur {drive_path} : {str(e)}"
                    )

    except Exception as e:
        logger.error(f"Erreur lors du listage des répertoires : {str(e)}")
        logger.error(traceback.format_exc())


def convert_path_to_container(windows_path):
    """
    Convertit un chemin Windows en format compatible avec le système de fichiers local.

    Args:
        windows_path (str): Chemin au format Windows

    Returns:
        str: Chemin au format local
    """
    logger.debug(f"Conversion du chemin : {windows_path}")
    if not windows_path:
        logger.warning("Chemin vide reçu pour la conversion")
        return ""

    try:
        # Normalisation du chemin
        path = os.path.normpath(windows_path)
        path = path.replace('\\', '/')

        # Gestion des chemins avec lettre de lecteur (ex: C:\...)
        if len(path) > 1 and path[1] == ':':
            # Pour Windows, on garde le format original
            logger.info(
                f"Utilisation du chemin Windows original : {windows_path}")
            return windows_path

        # Gestion des chemins UNC (ex: \\server\share\...)
        if path.startswith('//') or path.startswith('\\\\'):
            # Pour Windows, on garde le format UNC original
            logger.info(f"Utilisation du chemin UNC original : {windows_path}")
            return windows_path

        # Si le chemin est déjà au format approprié, le retourner tel quel
        logger.info(f"Utilisation du chemin tel quel : {windows_path}")
        return windows_path

    except Exception as e:
        logger.error(f"Erreur lors de la conversion du chemin : {str(e)}")
        logger.error(traceback.format_exc())
        return windows_path


def convert_to_wsl_path(windows_path):
    """
    Convertit un chemin Windows en chemin WSL.

    Args:
        windows_path (str): Chemin au format Windows

    Returns:
        str: Chemin au format WSL
    """
    try:
        # Si c'est un chemin réseau commençant par S:
        if windows_path.upper().startswith('S:'):
            # Conserver le chemin tel quel pour le moment car il sera géré par sync_folders.sh
            return windows_path

        # Pour les chemins locaux
        # 1. Normaliser les slashes
        path = windows_path.replace('\\', '/')
        # 2. Supprimer le : après la lettre de lecteur
        if ':' in path:
            drive_letter = path[0].lower()
            path = f"/mnt/{drive_letter}" + path[2:]
        return path
    except Exception as e:
        logger.error(f"Erreur lors de la conversion du chemin WSL : {str(e)}")
        return windows_path


@app.route('/')
def index():
    """Page d'accueil de l'application."""
    logger.debug("Accès à la page d'accueil")
    return render_template('index.html')


@app.route('/compare_folders', methods=['POST'])
def compare_folders():
    """
    Compare les dossiers et affiche les différences en utilisant sync_folders.sh.
    """
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']
        output_file = os.path.join(SCRIPT_DIR, 'comparison_output.json')

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA COMPARAISON DES DOSSIERS")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Conversion des chemins pour WSL
        wsl_script_path = convert_to_wsl_path(
            os.path.join(SCRIPT_DIR, 'sync_folders.sh'))
        wsl_output_file = convert_to_wsl_path(output_file)

        logger.info(f"Chemin du script WSL : {wsl_script_path}")
        logger.info(f"Chemin du fichier de sortie WSL : {wsl_output_file}")

        # Appel du script bash via WSL
        cmd = [
            'wsl', 'bash', wsl_script_path, 'compare', source_dir, dest_dir,
            mode, wsl_output_file
        ]

        logger.info(f"Commande exécutée : {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as file:
                    comparison_result = json.load(file)

                # Affichage de la synthèse
                logger.info("SYNTHÈSE DE LA COMPARAISON :")
                logger.info(
                    f"Nombre de fichiers à créer : {len(comparison_result.get('to_create', []))}"
                )
                if comparison_result.get('to_create'):
                    logger.info("Fichiers à créer :")
                    for file in comparison_result['to_create']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à mettre à jour : {len(comparison_result.get('to_update', []))}"
                )
                if comparison_result.get('to_update'):
                    logger.info("Fichiers à mettre à jour :")
                    for file in comparison_result['to_update']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à supprimer : {len(comparison_result.get('to_delete', []))}"
                )
                if comparison_result.get('to_delete'):
                    logger.info("Fichiers à supprimer :")
                    for file in comparison_result['to_delete']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à créer en sens inverse : {len(comparison_result.get('to_create_reverse', []))}"
                )
                if comparison_result.get('to_create_reverse'):
                    logger.info("Fichiers à créer en sens inverse :")
                    for file in comparison_result['to_create_reverse']:
                        logger.info(f"  - {file}")

                logger.info("=" * 80)
                logger.info("COMPARAISON TERMINÉE AVEC SUCCÈS")
                logger.info("=" * 80)

                return render_template(
                    'index.html',
                    comparison_result=comparison_result,
                    source_dir=source_dir,
                    dest_dir=dest_dir,
                    mode=mode,
                    success="Comparaison effectuée avec succès")
            except json.JSONDecodeError as e:
                logger.error("ERREUR DE LECTURE DES RÉSULTATS :")
                logger.error(
                    f"Erreur lors de la lecture du fichier JSON : {str(e)}")
                logger.error("-" * 80)
                return render_template(
                    'index.html',
                    error="Erreur lors de la lecture des résultats",
                    source_dir=source_dir,
                    dest_dir=dest_dir,
                    mode=mode)
        else:
            error_msg = result.stderr or "Erreur inconnue lors de la comparaison"
            logger.error("ERREUR DE COMPARAISON :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error("ERREUR INATTENDUE :")
        logger.error(f"Erreur lors de la comparaison : {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("-" * 80)
        return render_template(
            'index.html',
            error=str(e),
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


@app.route('/sync_folders', methods=['POST'])
def sync_folders():
    """
    Synchronise les dossiers selon les différences trouvées en utilisant sync_folders.sh.
    """
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA SYNCHRONISATION")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Conversion des chemins pour WSL
        wsl_script_path = convert_to_wsl_path(
            os.path.join(SCRIPT_DIR, 'sync_folders.sh'))

        logger.info(f"Chemin du script WSL : {wsl_script_path}")

        # Appel du script bash via WSL
        cmd = [
            'wsl', 'bash', wsl_script_path, 'sync', source_dir, dest_dir, mode
        ]

        logger.info("EXÉCUTION DE LA SYNCHRONISATION :")
        logger.info(f"Commande : {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("=" * 80)
            logger.info("SYNCHRONISATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 80)
            return redirect(url_for('compare_folders'),
                            code=307)  # Réutilise les données POST
        else:
            error_msg = result.stderr or "Erreur inconnue lors de la synchronisation"
            logger.error("ERREUR DE SYNCHRONISATION :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error("ERREUR INATTENDUE :")
        logger.error(f"Erreur lors de la synchronisation : {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("-" * 80)
        return render_template(
            'index.html',
            error=str(e),
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


if __name__ == '__main__':
    try:
        app.run(debug=True, port=5001)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application : {str(e)}")
