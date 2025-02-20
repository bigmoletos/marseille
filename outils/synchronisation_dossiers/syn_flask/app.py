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

# Configuration du logging
logging.basicConfig(
    filename='flask_app.log',
    level=logging.DEBUG,
    format=
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Ajout du logging console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Flask(__name__)
app.secret_key = os.urandom(24)

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


def find_git_bash():
    """
    Trouve le chemin de Git Bash sur le système Windows.

    Returns:
        str: Chemin vers git-bash.exe ou None si non trouvé
    """
    possible_paths = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Git\\bin\\bash.exe")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def convert_to_git_bash_path(windows_path):
    """
    Convertit un chemin Windows en format compatible avec Git Bash.

    Args:
        windows_path (str): Chemin Windows

    Returns:
        str: Chemin compatible Git Bash
    """
    # Pour les chemins réseau (S:), les retourner tels quels
    if windows_path.upper().startswith('S:'):
        return windows_path.replace('\\', '/')

    # Pour les chemins locaux, convertir en format Git Bash
    path = windows_path.replace('\\', '/')
    if ':' in path:
        drive_letter = path[0].lower()
        path = f"/{drive_letter}{path[2:]}"
    return path


def clean_mode(mode):
    """
    Nettoie le mode en enlevant les parenthèses et autres caractères spéciaux.

    Args:
        mode (str): Mode de synchronisation avec potentiellement des parenthèses

    Returns:
        str: Mode nettoyé
    """
    # Enlever les parenthèses et le texte entre parenthèses
    mode = mode.split('(')[0].strip()
    return mode


@app.route('/')
def index():
    """Page d'accueil de l'application."""
    return render_template('index.html')


def check_git_bash_commands():
    """
    Vérifie la présence des commandes nécessaires dans Git Bash.
    """
    git_bash = find_git_bash()
    if not git_bash:
        raise Exception("Git Bash n'est pas installé sur le système")

    # Commande pour vérifier la présence des outils
    check_command = """
export PATH="/usr/bin:$PATH"
command -v rsync >/dev/null 2>&1 || { echo "rsync non trouvé"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq non trouvé"; exit 1; }
echo "Toutes les commandes sont disponibles"
"""

    logger.info("Vérification des commandes Git Bash...")
    cmd = [git_bash, '--login', '-c', check_command]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        logger.info(f"Sortie standard : {result.stdout}")
    if result.stderr:
        logger.error(f"Sortie d'erreur : {result.stderr}")

    if result.returncode != 0:
        raise Exception(
            "Certaines commandes requises ne sont pas disponibles dans Git Bash. Assurez-vous que Git Bash est correctement installé avec les outils rsync et jq."
        )

    logger.info("Toutes les commandes requises sont disponibles dans Git Bash")


@app.route('/compare_folders', methods=['POST'])
def compare_folders():
    """Compare les dossiers en utilisant sync_folders.sh."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = clean_mode(request.form['mode'])
        output_file = os.path.join(SCRIPT_DIR, 'comparaison_output.json')

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA COMPARAISON DES DOSSIERS")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Vérification des commandes Git Bash
        try:
            check_git_bash_commands()
            logger.info("Vérification des commandes Git Bash réussie")
        except Exception as e:
            error_msg = f"Erreur lors de la vérification des commandes Git Bash : {str(e)}"
            logger.error(error_msg)
            return render_template('index.html', error=error_msg)

        # Trouver Git Bash
        git_bash = find_git_bash()
        if not git_bash:
            error_msg = "Git Bash n'est pas installé sur le système"
            logger.error(error_msg)
            return render_template('index.html', error=error_msg)

        # Conversion des chemins pour Git Bash
        script_path = os.path.join(SCRIPT_DIR, 'sync_folders.sh')
        script_path_bash = convert_to_git_bash_path(script_path)
        output_file_bash = convert_to_git_bash_path(output_file)
        source_dir_bash = source_dir.replace('\\', '/')
        dest_dir_bash = dest_dir.replace('\\', '/')

        # Vérification des chemins
        logger.info(f"Script path (Windows) : {script_path}")
        logger.info(f"Script path (Bash)    : {script_path_bash}")
        logger.info(f"Output file (Bash)    : {output_file_bash}")
        logger.info(f"Source dir           : {source_dir_bash}")
        logger.info(f"Dest dir            : {dest_dir_bash}")

        # Construction de la commande bash
        bash_command = f"""
export PATH="/usr/bin:$PATH"
cd "{os.path.dirname(script_path_bash)}" && chmod +x "{os.path.basename(script_path_bash)}" && ./"{os.path.basename(script_path_bash)}" compare "{source_dir_bash}" "{dest_dir_bash}" "{mode}" "{output_file_bash}"
"""

        # Appel du script bash via Git Bash
        cmd = [git_bash, '--login', '-c', bash_command]

        logger.info("Commande bash complète :")
        logger.info("-" * 80)
        logger.info(bash_command)
        logger.info("-" * 80)

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Log de la sortie standard et d'erreur
        if result.stdout:
            logger.info("Sortie standard :")
            logger.info(result.stdout)
        if result.stderr:
            logger.error("Sortie d'erreur :")
            logger.error(result.stderr)

        if result.returncode == 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as file:
                    comparison_result = json.load(file)

                # Affichage de la synthèse
                logger.info("SYNTHÈSE DE LA COMPARAISON :")
                logger.info(
                    f"Fichiers à créer : {len(comparison_result.get('to_create', []))}"
                )
                logger.info(
                    f"Fichiers à mettre à jour : {len(comparison_result.get('to_update', []))}"
                )
                logger.info(
                    f"Fichiers à supprimer : {len(comparison_result.get('to_delete', []))}"
                )

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
                error_msg = f"Erreur lors de la lecture du fichier JSON : {str(e)}"
                logger.error(error_msg)
                return render_template('index.html',
                                       error=error_msg,
                                       source_dir=source_dir,
                                       dest_dir=dest_dir,
                                       mode=mode)
        else:
            error_msg = result.stderr if result.stderr else "Erreur inconnue lors de la comparaison"
            logger.error(
                f"Erreur lors de la comparaison (code {result.returncode}) : {error_msg}"
            )
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return render_template(
            'index.html',
            error=str(e),
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


@app.route('/sync_folders', methods=['POST'])
def sync_folders():
    """Synchronise les dossiers en utilisant sync_folders.sh."""
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = clean_mode(request.form['mode'])

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA SYNCHRONISATION")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Trouver Git Bash
        git_bash = find_git_bash()
        if not git_bash:
            error_msg = "Git Bash n'est pas installé sur le système"
            logger.error(error_msg)
            return render_template('index.html', error=error_msg)

        # Conversion des chemins pour Git Bash
        script_path = convert_to_git_bash_path(
            os.path.join(SCRIPT_DIR, 'sync_folders.sh'))
        source_dir_bash = source_dir.replace(
            '\\',
            '/')  # Juste remplacer les backslashes pour les chemins réseau
        dest_dir_bash = dest_dir.replace(
            '\\',
            '/')  # Juste remplacer les backslashes pour les chemins réseau

        # Construction de la commande bash
        bash_command = f"chmod +x '{script_path}' && '{script_path}' sync '{source_dir_bash}' '{dest_dir_bash}' '{mode}'"

        # Appel du script bash via Git Bash
        cmd = [git_bash, '--login', '-c', bash_command]

        logger.info(f"Commande exécutée : {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("=" * 80)
            logger.info("SYNCHRONISATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 80)

            # Au lieu de rediriger, on appelle directement la comparaison
            output_file = os.path.join(SCRIPT_DIR, 'comparison_output.json')
            output_file_bash = convert_to_git_bash_path(output_file)

            # Construction de la commande de comparaison
            bash_command_compare = f"chmod +x '{script_path}' && '{script_path}' compare '{source_dir_bash}' '{dest_dir_bash}' '{mode}' '{output_file_bash}'"

            # Appel du script de comparaison via Git Bash
            cmd_compare = [git_bash, '--login', '-c', bash_command_compare]

            # Appel du script de comparaison via Git Bash
            result_compare = subprocess.run(cmd_compare,
                                            capture_output=True,
                                            text=True)

            if result_compare.returncode == 0:
                try:
                    with open(output_file, 'r', encoding='utf-8') as file:
                        comparison_result = json.load(file)
                    return render_template(
                        'index.html',
                        comparison_result=comparison_result,
                        source_dir=source_dir,
                        dest_dir=dest_dir,
                        mode=mode,
                        success=
                        "Synchronisation et comparaison effectuées avec succès"
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Erreur lors de la lecture du fichier JSON : {str(e)}"
                    )
                    return render_template(
                        'index.html',
                        error=
                        "Synchronisation réussie mais erreur lors de la comparaison finale",
                        source_dir=source_dir,
                        dest_dir=dest_dir,
                        mode=mode)
            else:
                return render_template(
                    'index.html',
                    error=
                    "Synchronisation réussie mais erreur lors de la comparaison finale",
                    source_dir=source_dir,
                    dest_dir=dest_dir,
                    mode=mode)
        else:
            error_msg = result.stderr or "Erreur inconnue lors de la synchronisation"
            logger.error(f"Erreur lors de la synchronisation : {error_msg}")
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
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
