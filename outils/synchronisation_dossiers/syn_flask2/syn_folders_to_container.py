import os
import json
import subprocess
import datetime
import shutil
import logging
import platform
import sys
from pathlib import Path
from typing import List, Dict, Union, Optional

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('sync.log'),
              logging.StreamHandler()])
logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Classe personnalisée pour les erreurs de synchronisation"""
    pass


def setup_logging() -> None:
    """
    Configure le système de logging avec des handlers pour fichier et console.
    """
    try:
        # Création du dossier logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)

        # Configuration du logger principal
        logger.setLevel(logging.INFO)

        # Handler pour le fichier de log avec rotation
        file_handler = logging.FileHandler('logs/sync.log', encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        logger.info("Système de logging initialisé avec succès")
    except Exception as e:
        print(f"ERREUR lors de l'initialisation du logging: {str(e)}")
        raise


def get_system_info() -> Dict[str, str]:
    """
    Détecte et retourne les informations sur le système d'exploitation.

    Returns:
        Dict[str, str]: Dictionnaire contenant les informations système
    """
    try:
        system_info = {
            'os': platform.system().lower(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'is_wsl': False
        }

        # Détection de WSL
        if system_info['os'] == 'linux':
            try:
                with open('/proc/version', 'r') as f:
                    if 'microsoft' in f.read().lower():
                        system_info['is_wsl'] = True
            except:
                pass

        logger.debug(f"Informations système détectées: {system_info}")
        return system_info
    except Exception as e:
        logger.error(f"Erreur lors de la détection du système: {str(e)}")
        raise


# Variable globale pour stocker les informations système
SYSTEM_INFO = get_system_info()


def convert_path(path: str) -> str:
    """
    Convertit un chemin selon le système d'exploitation.

    Args:
        path (str): Chemin à convertir

    Returns:
        str: Chemin converti selon le système

    Raises:
        ValueError: Si le chemin est invalide
        OSError: Si une erreur système survient lors de la conversion
    """
    try:
        # Si le chemin est déjà au format Git Bash, le retourner tel quel
        if path.startswith('/'):
            return path

        # Normaliser le chemin selon l'OS
        path = os.path.normpath(path)

        # Si nous sommes sous Windows
        if SYSTEM_INFO['os'] == 'windows':
            logger.debug(f"Conversion de chemin sous Windows: {path}")

            # Gérer les chemins réseau avec lettre de lecteur (ex: S:/)
            if ':' in path:
                drive_letter = path[0].lower()
                path_normalized = path[2:].replace('\\', '/').lstrip('/')
                return f"/mnt/{drive_letter}/{path_normalized}"

            # Gérer les chemins UNC
            if path.startswith('\\\\'):
                clean_path = path[2:].replace('\\', '/')
                return f"/mnt/{clean_path}"

            # Chemin local Windows
            return os.path.abspath(path)

        # Si nous sommes sous Linux/Unix
        elif SYSTEM_INFO['os'] == 'linux':
            logger.debug(f"Conversion de chemin sous Linux: {path}")

            # Si nous sommes sous WSL
            if SYSTEM_INFO['is_wsl']:
                logger.debug("Détection de WSL - adaptation du chemin")

                # Convertir les chemins Windows en chemins WSL
                if ':' in path:  # C'est un chemin Windows
                    drive_letter = path[0].lower()
                    path = path[2:].replace('\\', '/')
                    return f"/mnt/{drive_letter}/{path.lstrip('/')}"

                # Gérer les chemins UNC
                if path.startswith('\\\\'):
                    clean_path = path[2:].replace('\\', '/')
                    return f"/mnt/{clean_path}"

                return path

            # Linux natif
            return os.path.abspath(path).replace('\\', '/')

        # Pour les autres systèmes
        else:
            logger.warning(
                f"Système d'exploitation non reconnu: {SYSTEM_INFO['os']}")
            return os.path.abspath(path).replace('\\', '/')

    except Exception as e:
        logger.error(
            f"Erreur lors de la conversion du chemin '{path}': {str(e)}")
        raise ValueError(f"Impossible de convertir le chemin: {str(e)}")


def clean_path(path: str) -> str:
    """
    Nettoie et normalise un chemin.

    Args:
        path (str): Chemin à nettoyer

    Returns:
        str: Chemin nettoyé et normalisé

    Raises:
        ValueError: Si le chemin est invalide
    """
    try:
        cleaned_path = str(Path(path).resolve())
        return cleaned_path.strip()
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du chemin '{path}': {str(e)}")
        raise ValueError(f"Impossible de nettoyer le chemin: {str(e)}")


def log(message: str) -> None:
    """
    Enregistre un message dans le fichier de log et l'affiche dans la console.

    Args:
        message (str): Message à logger
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"

        # Écriture dans le fichier de log
        with open('sync.log', 'a', encoding='utf-8') as log_file:
            log_file.write(log_message + '\n')

        # Affichage console
        print(log_message)

        # Utilisation du logger
        logger.info(message)
    except Exception as e:
        logger.error(f"Erreur lors du logging: {str(e)}")
        print(f"ERREUR de logging: {str(e)}")


def show_progress(current: int, total: int, width: int = 50) -> None:
    """
    Affiche une barre de progression.

    Args:
        current (int): Valeur actuelle
        total (int): Valeur totale
        width (int, optional): Largeur de la barre. Defaults to 50.
    """
    try:
        progress = int(current * width / total)
        percentage = int(current * 100 / total)
        bar = f"[{'=' * progress}{' ' * (width - progress)}] {percentage}%"
        message = f"{bar} ({current}/{total})"
        logger.info(message)
        log(message)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de la progression: {str(e)}")


def count_total_files(files_to_create: List[str], files_to_update: List[str],
                      files_to_delete: List[str],
                      files_to_create_reverse: List[str]) -> int:
    """
    Compte le nombre total de fichiers à traiter.

    Args:
        files_to_create (List[str]): Fichiers à créer
        files_to_update (List[str]): Fichiers à mettre à jour
        files_to_delete (List[str]): Fichiers à supprimer
        files_to_create_reverse (List[str]): Fichiers à créer en sens inverse

    Returns:
        int: Nombre total de fichiers
    """
    try:
        total = len(files_to_create) + len(files_to_update) + \
                len(files_to_delete) + len(files_to_create_reverse)
        logger.debug(f"Nombre total de fichiers à traiter: {total}")
        return total
    except Exception as e:
        logger.error(f"Erreur lors du comptage des fichiers: {str(e)}")
        raise


# Fonction pour vérifier les dépendances
def check_dependencies() -> bool:
    """
    Vérifie la présence des dépendances système nécessaires.

    Returns:
        bool: True si toutes les dépendances sont présentes, False sinon
    """
    try:
        missing_deps = []
        if shutil.which('rsync') is None:
            missing_deps.append('rsync')
        if shutil.which('jq') is None:
            missing_deps.append('jq')

        if missing_deps:
            logger.error(f"Dépendances manquantes : {', '.join(missing_deps)}")
            log(f"Dépendances manquantes : {', '.join(missing_deps)}")
            log("Veuillez installer les dépendances manquantes manuellement ou utiliser un gestionnaire de paquets comme Chocolatey."
                )
            return False

        logger.info("Toutes les dépendances sont présentes")
        return True
    except Exception as e:
        logger.error(
            f"Erreur lors de la vérification des dépendances: {str(e)}")
        raise


def log_array(array_name: str, array_content: List[str]) -> None:
    """
    Affiche le contenu d'un tableau dans les logs.

    Args:
        array_name (str): Nom du tableau
        array_content (List[str]): Contenu du tableau
    """
    try:
        logger.info(f"Contenu du tableau {array_name}:")
        log(f"Contenu du tableau {array_name}:")
        for item in array_content:
            logger.info(f"  - {item}")
            log(f"  - {item}")
    except Exception as e:
        logger.error(
            f"Erreur lors de l'affichage du tableau {array_name}: {str(e)}")


def is_subpath(path: str, array: List[str]) -> bool:
    """
    Vérifie si un chemin est un sous-chemin d'un des éléments du tableau.

    Args:
        path (str): Chemin à vérifier
        array (List[str]): Liste des chemins de référence

    Returns:
        bool: True si le chemin est un sous-chemin, False sinon
    """
    try:
        for item in array:
            if path != item and path.startswith(item + '/'):
                logger.debug(
                    f"Le chemin '{path}' est un sous-chemin de '{item}'")
                return True
        return False
    except Exception as e:
        logger.error(
            f"Erreur lors de la vérification du sous-chemin '{path}': {str(e)}"
        )
        raise


def add_to_array(path: str, array: List[str]) -> None:
    """
    Ajoute un chemin à un tableau sans redondance et en gérant les sous-chemins.

    Args:
        path (str): Chemin à ajouter
        array (List[str]): Tableau de destination

    Raises:
        ValueError: Si le chemin est invalide
    """
    try:
        path = clean_path(path)
        if not is_subpath(path, array):
            # Supprime les chemins qui sont des sous-chemins du nouveau chemin
            array[:] = [
                item for item in array if not item.startswith(path + '/')
            ]
            if path not in array:
                array.append(path)
                logger.debug(f"Chemin '{path}' ajouté au tableau")
    except Exception as e:
        logger.error(
            f"Erreur lors de l'ajout du chemin '{path}' au tableau: {str(e)}")
        raise


def get_relative_path(path: str, base_path: str) -> str:
    """
    Obtient le chemin relatif par rapport à un chemin de base.

    Args:
        path (str): Chemin complet
        base_path (str): Chemin de base

    Returns:
        str: Chemin relatif
    """
    try:
        # Convertir les deux chemins en objets Path
        path = Path(path)
        base_path = Path(base_path)

        # Obtenir le chemin relatif
        rel_path = str(path.relative_to(base_path))

        # Normaliser selon l'OS
        if SYSTEM_INFO['os'] == 'windows':
            return rel_path.replace('/', '\\')
        return rel_path.replace('\\', '/')

    except Exception as e:
        logger.error(f"Erreur lors du calcul du chemin relatif: {str(e)}")
        return str(path)


def generate_folder_json(dir_path: str) -> str:
    """
    Génère une représentation JSON d'un dossier.

    Args:
        dir_path (str): Chemin du dossier

    Returns:
        str: Représentation JSON du dossier

    Raises:
        OSError: Si le dossier n'est pas accessible
        ValueError: Si le chemin est invalide
    """
    try:
        # Convertir et nettoyer le chemin
        dir_path = clean_path(dir_path)
        folders = []
        files = []

        logger.info(f"Génération du JSON pour le dossier: {dir_path}")

        for entry in Path(dir_path).iterdir():
            try:
                # Utiliser seulement le nom du fichier/dossier
                name = entry.name

                if entry.is_dir():
                    folder_date = datetime.datetime.fromtimestamp(
                        entry.stat().st_mtime).strftime('%Y%m%d%H%M%S')
                    folders.append({"name": name, "date": folder_date})
                    logger.debug(f"Dossier ajouté: {name}")
                elif entry.is_file():
                    file_date = datetime.datetime.fromtimestamp(
                        entry.stat().st_mtime).strftime('%Y%m%d%H%M%S')
                    file_size = entry.stat().st_size
                    files.append({
                        "name": name,
                        "date": file_date,
                        "size": file_size
                    })
                    logger.debug(f"Fichier ajouté: {name}")
            except Exception as e:
                logger.warning(
                    f"Erreur lors du traitement de l'entrée {entry}: {str(e)}")
                continue

        result = json.dumps({"folders": folders, "files": files}, indent=2)
        logger.debug("Génération du JSON terminée avec succès")
        return result

    except Exception as e:
        logger.error(
            f"Erreur lors de la génération du JSON pour {dir_path}: {str(e)}")
        raise


def normalize_path_for_json(path: str) -> str:
    """
    Normalise un chemin pour le stockage JSON selon le système d'exploitation.

    Args:
        path (str): Chemin à normaliser

    Returns:
        str: Chemin normalisé
    """
    try:
        # Obtenir le chemin relatif par rapport au répertoire courant
        try:
            rel_path = os.path.relpath(path)
        except ValueError:
            # Si le chemin est sur un autre lecteur, garder le chemin absolu
            rel_path = path

        # Convertir selon l'OS
        if SYSTEM_INFO['os'] == 'windows':
            # Garder les backslashes pour Windows
            return rel_path.replace('/', '\\')
        else:
            # Convertir en forward slashes pour Unix
            return rel_path.replace('\\', '/')

    except Exception as e:
        logger.error(
            f"Erreur lors de la normalisation du chemin '{path}': {str(e)}")
        return path


def compare_json_folders(source_json: str, dest_json: str) -> None:
    """
    Compare deux représentations JSON de dossiers et génère les listes de différences.

    Args:
        source_json (str): JSON du dossier source
        dest_json (str): JSON du dossier destination
    """
    try:
        global nombre_to_create, nombre_to_update, nombre_to_delete, nombre_to_bidirectionnel
        nombre_to_create = nombre_to_update = nombre_to_delete = nombre_to_bidirectionnel = 0
        global to_create, to_update, to_delete
        to_create = []
        to_update = []
        to_delete = []

        source_data = json.loads(source_json)
        dest_data = json.loads(dest_json)

        source_folders = {
            folder['name']: folder['date']
            for folder in source_data['folders']
        }
        dest_folders = {
            folder['name']: folder['date']
            for folder in dest_data['folders']
        }

        # Traitement des dossiers
        for folder, source_date in source_folders.items():
            if folder not in dest_folders:
                if "Copie" in folder:
                    to_create.append(folder)
                    nombre_to_create += 1
                else:
                    to_update.append(folder)
                    nombre_to_update += 1
            else:
                dest_date = dest_folders[folder]
                if source_date != dest_date:
                    if "Copie" in folder:
                        to_create.append(folder)
                        nombre_to_create += 1
                    else:
                        to_update.append(folder)
                        nombre_to_update += 1

        for folder in dest_folders.keys():
            if folder not in source_folders:
                to_delete.append(folder)
                nombre_to_delete += 1

        # Traitement des fichiers
        source_files = {
            file['name']: (file['size'], file['date'])
            for file in source_data['files']
        }
        dest_files = {
            file['name']: (file['size'], file['date'])
            for file in dest_data['files']
        }

        for file, (source_size, source_date) in source_files.items():
            if file not in dest_files:
                to_create.append(file)
                nombre_to_create += 1
            else:
                dest_size, dest_date = dest_files[file]
                if source_size != dest_size or source_date != dest_date:
                    if file == "sync_manifest.json":
                        to_create.append(file)
                        nombre_to_create += 1
                    else:
                        to_update.append(file)
                        nombre_to_update += 1

        for file in dest_files.keys():
            if file not in source_files:
                to_delete.append(file)
                nombre_to_delete += 1

        # Trier les listes pour une meilleure lisibilité
        to_create.sort()
        to_update.sort()
        to_delete.sort()

        logger.info(
            f"Comparaison terminée: {nombre_to_create} à créer, {nombre_to_update} à mettre à jour, {nombre_to_delete} à supprimer"
        )

    except Exception as e:
        logger.error(f"Erreur lors de la comparaison des dossiers: {str(e)}")
        raise


def check_path(path: str, description: str) -> tuple[bool, str]:
    """
    Vérifie l'existence et l'accessibilité d'un chemin.

    Args:
        path (str): Chemin à vérifier
        description (str): Description du chemin pour les messages d'erreur

    Returns:
        tuple[bool, str]: (valide, message d'erreur)
            - valide: True si le chemin existe et est accessible
            - message d'erreur: Message explicatif si non valide, chaîne vide si valide
    """
    try:
        # Convertir le chemin selon l'OS
        path = convert_path(path)

        # Vérifier l'existence
        if not os.path.exists(path):
            error_msg = f"ERREUR: {description} n'existe pas: {path}"
            logger.error(error_msg)
            logger.error(
                "Veuillez vérifier que le chemin est correct et accessible")
            return False, error_msg

        # Vérifier les permissions de lecture
        if not os.access(path, os.R_OK):
            error_msg = f"ERREUR: {description} n'est pas accessible en lecture: {path}"
            logger.error(error_msg)
            return False, error_msg

        # Vérifier si c'est un dossier
        if not os.path.isdir(path):
            error_msg = f"ERREUR: {description} n'est pas un dossier: {path}"
            logger.error(error_msg)
            return False, error_msg

        logger.debug(f"Chemin {description} vérifié avec succès: {path}")
        return True, ""

    except Exception as e:
        error_msg = f"ERREUR lors de la vérification de {description}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def compare_folders(source_dir: str,
                    dest_dir: str,
                    mode: str,
                    output_file: str,
                    script_path: str = None) -> None:
    """
    Compare deux dossiers et génère un fichier JSON avec les différences.

    Args:
        source_dir (str): Chemin du dossier source
        dest_dir (str): Chemin du dossier destination
        mode (str): Mode de comparaison ('A vers B', 'B vers A', 'A idem B')
        output_file (str): Chemin du fichier de sortie JSON
        script_path (str, optional): Chemin du script bash. Si None, utilise le script au même niveau.

    Raises:
        SyncError: Si une erreur survient pendant la comparaison
    """
    try:
        logger.info("=== DÉBUT DE LA COMPARAISON ===")
        logger.info(f"Mode: {mode}")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Destination: {dest_dir}")
        logger.info(f"Fichier de sortie: {output_file}")

        # Vérifier les dépendances
        if not check_dependencies():
            raise SyncError("Impossible d'installer les dépendances")

        # Convertir et vérifier les chemins
        source_dir = convert_path(source_dir)
        dest_dir = convert_path(dest_dir)
        output_file = convert_path(output_file)

        if not check_path(source_dir, "Source") or not check_path(
                dest_dir, "Destination"):
            raise SyncError(
                "Un des dossiers n'existe pas ou n'est pas accessible")

        # Utiliser le script bash au même niveau que ce fichier si non spécifié
        if script_path is None:
            script_path = os.path.join(os.path.dirname(__file__),
                                       "sync_folders.sh")

        script_path = convert_path(script_path)
        script_dir = os.path.dirname(script_path)

        # Vérifier que le script existe
        if not os.path.isfile(script_path):
            raise SyncError(f"Le script {script_path} n'existe pas")

        # Rendre le script exécutable
        try:
            os.chmod(script_path, 0o755)
            logger.info(f"Script {script_path} rendu exécutable")
        except Exception as e:
            logger.error(f"Erreur lors du chmod +x: {str(e)}")
            raise

        # Exécuter le script bash pour la comparaison
        script_name = os.path.basename(script_path)

        # Construire la commande avec les chemins convertis
        cmd = f'cd "{script_dir}" && chmod +x "{script_name}" && ./{script_name} compare "{source_dir}" "{dest_dir}" "{mode}" "{output_file}"'
        logger.info(f"Commande à exécuter: {cmd}")

        # Exécuter la commande
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:" + env.get("PATH", "")

        result = subprocess.run(cmd,
                                shell=True,
                                capture_output=True,
                                text=True,
                                env=env)

        # Afficher la sortie standard et d'erreur pour le débogage
        if result.stdout:
            logger.info(f"Sortie standard:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Sortie d'erreur:\n{result.stderr}")

        if result.returncode != 0:
            error_msg = f"Erreur lors de la comparaison (code {result.returncode}): {result.stderr}"
            logger.error(error_msg)
            raise SyncError(error_msg)

        # Vérifier que le fichier de sortie a été créé
        if not os.path.isfile(output_file):
            raise SyncError(
                f"Le fichier de sortie {output_file} n'a pas été créé")

        logger.info("=== COMPARAISON TERMINÉE ===")

    except Exception as e:
        error_msg = f"Erreur lors de la comparaison: {str(e)}"
        logger.error(error_msg)
        # Sauvegarder l'erreur dans le fichier de sortie
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"error": error_msg}, f, indent=2)
        except Exception as write_error:
            logger.error(
                f"Erreur lors de l'écriture du fichier d'erreur: {str(write_error)}"
            )
        raise SyncError(error_msg)


def sync_folders(source_dir: str,
                 dest_dir: str,
                 mode: str,
                 output_file: str = "sync_results.json",
                 script_path: str = None) -> None:
    """
    Synchronise deux dossiers selon le mode spécifié.

    Args:
        source_dir (str): Chemin du dossier source
        dest_dir (str): Chemin du dossier destination
        mode (str): Mode de synchronisation ('A vers B', 'B vers A', 'A idem B')
        output_file (str, optional): Chemin du fichier de sortie JSON. Defaults to "sync_results.json".
        script_path (str, optional): Chemin du script bash. Si None, utilise le script au même niveau.
    """
    try:
        # Convertir tous les chemins
        source_dir = convert_path(source_dir)
        dest_dir = convert_path(dest_dir)
        output_file = convert_path(output_file)

        log("=== DÉBUT DE LA SYNCHRONISATION ===")
        log(f"Mode: {mode}")
        log(f"Source: {source_dir}")
        log(f"Destination: {dest_dir}")
        log(f"Fichier de sortie: {output_file}")

        # Utiliser le script bash au même niveau que ce fichier si non spécifié
        if script_path is None:
            script_path = os.path.join(os.path.dirname(__file__),
                                       "sync_folders.sh")

        script_path = convert_path(script_path)
        script_dir = os.path.dirname(script_path)

        # Vérifier que le script existe
        if not os.path.isfile(script_path):
            raise SyncError(f"Le script {script_path} n'existe pas")

        # Rendre le script exécutable
        try:
            os.chmod(script_path, 0o755)
            logger.info(f"Script {script_path} rendu exécutable")
        except Exception as e:
            logger.error(f"Erreur lors du chmod +x: {str(e)}")
            raise

        # Exécuter le script bash pour la synchronisation
        script_name = os.path.basename(script_path)

        # Construire la commande avec les chemins convertis
        cmd = f'cd "{script_dir}" && chmod +x "{script_name}" && ./{script_name} sync "{source_dir}" "{dest_dir}" "{mode}" "{output_file}"'
        logger.info(f"Commande à exécuter: {cmd}")

        # Exécuter la commande
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:" + env.get("PATH", "")

        result = subprocess.run(cmd,
                                shell=True,
                                capture_output=True,
                                text=True,
                                env=env)

        # Afficher la sortie standard et d'erreur pour le débogage
        if result.stdout:
            logger.info(f"Sortie standard:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Sortie d'erreur:\n{result.stderr}")

        if result.returncode != 0:
            error_msg = f"Erreur lors de la synchronisation (code {result.returncode}): {result.stderr}"
            logger.error(error_msg)
            raise SyncError(error_msg)

        # Vérifier que le fichier de sortie a été créé
        if not os.path.isfile(output_file):
            raise SyncError(
                f"Le fichier de sortie {output_file} n'a pas été créé")

        log("=== SYNCHRONISATION TERMINÉE AVEC SUCCÈS ===")

    except Exception as e:
        error_msg = f"Erreur lors de la synchronisation: {str(e)}"
        log(f"ERREUR: {error_msg}")

        # Sauvegarder l'erreur dans le fichier JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        "status":
                        "error",
                        "mode":
                        mode,
                        "source":
                        source_dir,
                        "destination":
                        dest_dir,
                        "error":
                        error_msg,
                        "timestamp":
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    },
                    f,
                    indent=2)
        except Exception as write_error:
            logger.error(
                f"Erreur lors de l'écriture du fichier d'erreur: {str(write_error)}"
            )

        log("=== SYNCHRONISATION TERMINÉE AVEC ERREUR ===")
        raise SyncError(error_msg)


# Point d'entrée principal
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py {compare|sync} [arguments]")
        sys.exit(1)

    command = sys.argv[1]

    # Fichiers de sortie par défaut
    default_compare_output = "output_comparison.json"
    default_sync_output = "sync_results.json"

    if command == "compare":
        if len(sys.argv) == 5:
            # Sans fichier de sortie spécifié
            source_dir = sys.argv[2]
            dest_dir = sys.argv[3]
            mode = sys.argv[4]
            output_file = default_compare_output
        elif len(sys.argv) == 6:
            # Avec fichier de sortie spécifié
            source_dir = sys.argv[2]
            dest_dir = sys.argv[3]
            mode = sys.argv[4]
            output_file = sys.argv[5]
        else:
            print(
                "Usage: python script.py compare <source_dir> <dest_dir> <mode> [output_file]"
            )
            sys.exit(1)

        compare_folders(source_dir, dest_dir, mode, output_file)

    elif command == "sync":
        if len(sys.argv) == 5:
            # Sans fichier de sortie spécifié
            source_dir = sys.argv[2]
            dest_dir = sys.argv[3]
            mode = sys.argv[4]
            output_file = default_sync_output
        elif len(sys.argv) == 6:
            # Avec fichier de sortie spécifié
            source_dir = sys.argv[2]
            dest_dir = sys.argv[3]
            mode = sys.argv[4]
            output_file = sys.argv[5]
        else:
            print(
                "Usage: python script.py sync <source_dir> <dest_dir> <mode> [output_file]"
            )
            sys.exit(1)

        sync_folders(source_dir, dest_dir, mode, output_file)
    else:
        print("Usage: python script.py {compare|sync} [arguments]")
        sys.exit(1)
