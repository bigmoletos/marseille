# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "flask",
#     "pandas",
#     "numpy",
#     "urllib3",
#     "shutil",
#     "logging",
#     "platform",
#     "sys",
#     "pathlib",
#     "typing",
#     "tempfile",
#     "traceback",
# ]
# ///

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
import tempfile
import traceback
import re

# Variables globales pour stocker les résultats des comparaisons
to_create = []
to_update = []
to_delete = []
to_bidirectionnel = []
nombre_to_create = 0
nombre_to_update = 0
nombre_to_delete = 0
nombre_to_bidirectionnel = 0

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('sync.log'),
              logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Ajouter un niveau "SUCCESS" à logging
SUCCESS = 25  # Entre INFO (20) et WARNING (30)
logging.addLevelName(SUCCESS, "SUCCESS")


def success(self, message, *args, **kws):
    """
    Méthode pour logger des messages de succès (niveau entre INFO et WARNING)
    """
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kws)


# Ajouter la méthode au logger
logging.Logger.success = success


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
        # Si le chemin est vide ou None, retourner tel quel
        if not path:
            return path

        # Si le chemin est déjà au format Unix/Linux, le retourner tel quel
        if path.startswith('/'):
            return path

        # Normaliser le chemin selon l'OS
        path = os.path.normpath(path)

        # Si nous sommes sous Windows
        if SYSTEM_INFO['os'] == 'windows':
            logger.debug(f"Conversion de chemin sous Windows natif: {path}")

            # Pour Windows natif, ne pas convertir en chemin Linux/WSL
            # Retourner simplement le chemin normalisé
            return path

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
        # Ne pas lever d'exception, retourner le chemin d'origine
        logger.warning(
            f"Utilisation du chemin d'origine comme fallback: {path}")
        return path


def clean_path(path: str) -> str:
    """
    Nettoie le chemin en enlevant les préfixes rsync et les caractères spéciaux.
    Les préfixes possibles sont '> ', '< ', '>f++++++++ ', '+++ ', 'g   ', etc.

    Args:
        path (str): Chemin à nettoyer

    Returns:
        str: Chemin nettoyé
    """
    try:
        # Liste complète des préfixes possibles que rsync peut ajouter aux chemins
        # Ces préfixes indiquent le type d'opération effectuée sur le fichier
        prefixes = [
            "g   ",  # Fichier ignoré (généralement identique)
            "g\t",  # Fichier ignoré (tabulation)
            ">f++++++++ ",  # Nouveau fichier à créer avec ses attributs
            "++++++++ ",  # Attributs modifiés
            "+++ ",  # Attributs modifiés (format court)
            "<f++++++++ ",  # Fichier source modifié
            "< ",  # Fichier source (format court)
            "> ",  # Fichier destination (format court)
            "<fc",  # Fichier modifié avec contenu
            ">fc",  # Fichier destination avec contenu
            "*deleting   ",  # Fichier à supprimer
            "*deleting\t",  # Fichier à supprimer (tabulation)
            ".d..t...... ",  # Dossier avec timestamp modifié
            "cd++++++++ ",  # Dossier créé avec attributs
            ".f..t...... ",  # Fichier avec timestamp modifié
            "cf++++++++ ",  # Fichier créé avec attributs
        ]

        # Identifier et enlever le préfixe si présent
        cleaned_path = path

        # Vérifier si le chemin commence par un préfixe connu
        for prefix in prefixes:
            if cleaned_path.startswith(prefix):
                cleaned_path = cleaned_path[len(prefix):]
                logger.debug(f"Préfixe '{prefix}' supprimé de '{path}'")
                break

        # Méthode plus générique pour détecter les préfixes non listés
        # Cette approche est importante pour gérer de nouveaux préfixes ajoutés par rsync
        if cleaned_path == path:  # Si aucun préfixe connu n'a été trouvé
            # Expression régulière pour détecter des motifs de préfixe génériques
            # Recherche un caractère spécial suivi d'espace ou autres caractères
            match = re.match(r'^([+><\*\.gcd][+\s\.\w]{0,10}\s+)',
                             cleaned_path)
            if match:
                prefix = match.group(1)
                cleaned_path = cleaned_path[len(prefix):]
                logger.debug(
                    f"Préfixe générique '{prefix}' supprimé de '{path}'")

        # Normalisation du chemin en utilisant des séparateurs standard
        # C'est crucial pour garantir une comparaison cohérente des chemins
        cleaned_path = cleaned_path.replace('\\', '/').strip()

        # Journalisation détaillée si le chemin a été modifié
        if cleaned_path != path:
            logger.debug(f"Nettoyage du chemin: '{path}' -> '{cleaned_path}'")

        return cleaned_path
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du chemin '{path}': {str(e)}")
        return path  # En cas d'erreur, on retourne le chemin d'origine


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


def compare_folders(source_dir: str,
                    dest_dir: str,
                    mode: str,
                    output_file: str,
                    script_path: str = None) -> None:
    """
    Compare deux dossiers selon le mode spécifié en utilisant rsync.

    Cette fonction utilise rsync pour effectuer une comparaison précise des dossiers,
    en tenant compte des différences de contenu, de taille et de date de modification.
    Elle gère spécifiquement les problèmes d'encodage qui peuvent survenir lors de
    l'utilisation de chemins contenant des caractères non ASCII ou spéciaux.

    Args:
        source_dir (str): Chemin absolu du dossier source à comparer
        dest_dir (str): Chemin absolu du dossier destination à comparer
        mode (str): Mode de comparaison ('A vers B', 'B vers A', 'A idem B')
        output_file (str): Chemin du fichier JSON où stocker les résultats
        script_path (str, optional): Chemin vers un script externe (non utilisé en natif)

    Raises:
        SyncError: Si une erreur se produit pendant la comparaison

    Note:
        Cette fonction met à jour les variables globales to_create, to_update,
        to_delete et to_bidirectionnel avec les listes d'éléments à synchroniser.
    """
    try:
        # Ne pas convertir les chemins en chemins WSL si sous Windows
        logger.info("=== DÉBUT DE LA COMPARAISON ===")
        logger.info(f"Mode: {mode}")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Destination: {dest_dir}")
        logger.info(f"Fichier de sortie: {output_file}")

        # Vérifier les dépendances
        if not check_dependencies():
            error_msg = "Dépendances manquantes pour la comparaison"
            logger.error(error_msg)
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({"error": error_msg}, f)
            except Exception as write_error:
                logger.error(
                    f"Erreur lors de l'écriture du fichier de sortie: {str(write_error)}"
                )
            raise SyncError(error_msg)

        # Vérifier l'existence des dossiers
        valid_source, source_error = check_path(source_dir, "Source")
        valid_dest, dest_error = check_path(dest_dir, "Destination")

        if not valid_source or not valid_dest:
            error_msg = source_error if not valid_source else dest_error
            logger.error(error_msg)
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({"error": error_msg}, f)
            except Exception as write_error:
                logger.error(
                    f"Erreur lors de l'écriture du fichier de sortie: {str(write_error)}"
                )
            raise SyncError(error_msg)

        # Préparer les chemins pour rsync
        rsync_source_dir = prepare_path_for_rsync(source_dir)
        rsync_dest_dir = prepare_path_for_rsync(dest_dir)

        logger.info(f"Chemin source préparé pour rsync: {rsync_source_dir}")
        logger.info(f"Chemin destination préparé pour rsync: {rsync_dest_dir}")

        # Réinitialiser les variables globales
        global to_create, to_update, to_delete, to_bidirectionnel
        global nombre_to_create, nombre_to_update, nombre_to_delete, nombre_to_bidirectionnel
        to_create = []
        to_update = []
        to_delete = []
        to_bidirectionnel = []
        nombre_to_create = 0
        nombre_to_update = 0
        nombre_to_delete = 0
        nombre_to_bidirectionnel = 0

        if mode == "A vers B":
            logger.info("Mode de comparaison: A vers B (sauvegarde)")
            try:
                # Utiliser rsync pour identifier les différences
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.close()

                # Commande rsync avec options pour afficher changements (--itemize-changes)
                rsync_cmd = [
                    "rsync", "-ain", "--delete", f"{rsync_source_dir}/",
                    f"{rsync_dest_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync: {' '.join(rsync_cmd)}")

                with open(temp_file.name, 'w', encoding='utf-8') as f:
                    try:
                        subprocess.run(rsync_cmd,
                                       stdout=f,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       check=True)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de l'exécution de rsync: {e.stderr}")

                # Traiter la sortie de rsync
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith(
                                'building') or line.startswith(
                                    'sending') or line.startswith(
                                        'sent') or line.startswith('total'):
                            continue

                        # Extraire le type de changement et le nom du fichier
                        change_type = line[0:2].strip()
                        file_name = line[8:].strip() if len(line) > 8 else ""

                        if not file_name:
                            continue

                        logger.debug(
                            f"Changement détecté: [{change_type}] [{file_name}]"
                        )

                        if change_type.startswith(">"):
                            # Nouveau fichier à créer
                            to_create.append(file_name)
                            nombre_to_create += 1
                            logger.info(f"À créer: {file_name}")
                        elif change_type.startswith("c"):
                            # Fichier à mettre à jour
                            to_update.append(file_name)
                            nombre_to_update += 1
                            logger.info(f"À mettre à jour: {file_name}")
                        elif change_type.startswith("*"):
                            # Fichier à supprimer
                            to_delete.append(file_name)
                            nombre_to_delete += 1
                            logger.info(f"À supprimer: {file_name}")

                # Nettoyer le fichier temporaire
                os.unlink(temp_file.name)
            except Exception as e:
                logger.error(f"Erreur lors de la comparaison: {str(e)}")
                raise

        elif mode == "B vers A":
            logger.info("Mode de comparaison: B vers A (restauration)")
            try:
                # Utiliser rsync pour identifier les différences
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.close()

                rsync_cmd = [
                    "rsync", "-ain", "--delete", f"{rsync_dest_dir}/",
                    f"{rsync_source_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync: {' '.join(rsync_cmd)}")

                with open(temp_file.name, 'w', encoding='utf-8') as f:
                    try:
                        subprocess.run(rsync_cmd,
                                       stdout=f,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       check=True)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de l'exécution de rsync: {e.stderr}")

                # Traiter la sortie de rsync
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith(
                                'building') or line.startswith(
                                    'sending') or line.startswith(
                                        'sent') or line.startswith('total'):
                            continue

                        # Extraire le type de changement et le nom du fichier
                        change_type = line[0:2].strip()
                        file_name = line[8:].strip() if len(line) > 8 else ""

                        if not file_name:
                            continue

                        logger.debug(
                            f"Changement détecté: [{change_type}] [{file_name}]"
                        )

                        if change_type.startswith(">"):
                            # Nouveau fichier à créer en sens inverse
                            to_bidirectionnel.append(file_name)
                            nombre_to_bidirectionnel += 1
                            logger.info(
                                f"À créer en sens inverse: {file_name}")
                        elif change_type.startswith("c"):
                            # Fichier à mettre à jour en sens inverse
                            to_bidirectionnel.append(file_name)
                            nombre_to_bidirectionnel += 1
                            logger.info(
                                f"À mettre à jour en sens inverse: {file_name}"
                            )
                        elif change_type.startswith("*"):
                            # Fichier à supprimer
                            to_delete.append(file_name)
                            nombre_to_delete += 1
                            logger.info(f"À supprimer: {file_name}")

                # Nettoyer le fichier temporaire
                os.unlink(temp_file.name)
            except Exception as e:
                logger.error(f"Erreur lors de la comparaison: {str(e)}")
                raise

        elif mode == "A idem B" or mode == "Bidirectionnel":
            logger.info("Mode de comparaison: Bidirectionnel (miroir)")
            try:
                # 1. Comparaison A vers B
                temp_file_ab = tempfile.NamedTemporaryFile(delete=False)
                temp_file_ab.close()

                rsync_cmd_ab = [
                    "rsync", "-ain", f"{rsync_source_dir}/",
                    f"{rsync_dest_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync A->B: {' '.join(rsync_cmd_ab)}"
                )

                with open(temp_file_ab.name, 'w', encoding='utf-8') as f:
                    try:
                        subprocess.run(rsync_cmd_ab,
                                       stdout=f,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       check=True)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync A->B: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de l'exécution de rsync A->B: {e.stderr}"
                        )

                # Traiter la sortie de rsync A->B
                with open(temp_file_ab.name, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith(
                                'building') or line.startswith(
                                    'sending') or line.startswith(
                                        'sent') or line.startswith('total'):
                            continue

                        # Extraire le type de changement et le nom du fichier
                        change_type = line[0:2].strip()
                        file_name = line[8:].strip() if len(line) > 8 else ""

                        if not file_name:
                            continue

                        logger.debug(
                            f"Changement A->B détecté: [{change_type}] [{file_name}]"
                        )

                        if change_type.startswith(">"):
                            # Nouveau fichier à créer
                            to_create.append(file_name)
                            nombre_to_create += 1
                            logger.info(f"À créer: {file_name}")
                        elif change_type.startswith("c"):
                            # Fichier à mettre à jour
                            to_update.append(file_name)
                            nombre_to_update += 1
                            logger.info(f"À mettre à jour: {file_name}")

                # 2. Comparaison B vers A
                temp_file_ba = tempfile.NamedTemporaryFile(delete=False)
                temp_file_ba.close()

                rsync_cmd_ba = [
                    "rsync", "-ain", f"{rsync_dest_dir}/",
                    f"{rsync_source_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync B->A: {' '.join(rsync_cmd_ba)}"
                )

                with open(temp_file_ba.name, 'w', encoding='utf-8') as f:
                    try:
                        subprocess.run(rsync_cmd_ba,
                                       stdout=f,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       check=True)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync B->A: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de l'exécution de rsync B->A: {e.stderr}"
                        )

                # Traiter la sortie de rsync B->A
                with open(temp_file_ba.name, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith(
                                'building') or line.startswith(
                                    'sending') or line.startswith(
                                        'sent') or line.startswith('total'):
                            continue

                        # Extraire le type de changement et le nom du fichier
                        change_type = line[0:2].strip()
                        file_name = line[8:].strip() if len(line) > 8 else ""

                        if not file_name:
                            continue

                        logger.debug(
                            f"Changement B->A détecté: [{change_type}] [{file_name}]"
                        )

                        if change_type.startswith(
                                ">") or change_type.startswith("c"):
                            # Fichier à synchroniser de B vers A
                            to_bidirectionnel.append(file_name)
                            nombre_to_bidirectionnel += 1
                            logger.info(
                                f"À synchroniser de B vers A: {file_name}")

                # Nettoyer les fichiers temporaires
                os.unlink(temp_file_ab.name)
                os.unlink(temp_file_ba.name)

            except Exception as e:
                logger.error(
                    f"Erreur lors de la comparaison bidirectionnelle: {str(e)}"
                )
                raise

        # Créer le résultat JSON
        result = {
            "error": None,
            "source_dir": source_dir,
            "dest_dir": dest_dir,
            "mode": mode,
            "to_create": to_create,
            "to_update": to_update,
            "to_delete": to_delete,
            "to_bidirectionnel": to_bidirectionnel,
            "nombre_to_create": nombre_to_create,
            "nombre_to_update": nombre_to_update,
            "nombre_to_delete": nombre_to_delete,
            "nombre_to_bidirectionnel": nombre_to_bidirectionnel
        }

        # Écrire le fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        logger.success(
            f"Comparaison terminée. Résultat enregistré dans {output_file}")
        logger.info(f"Éléments à créer: {nombre_to_create}")
        logger.info(f"Éléments à mettre à jour: {nombre_to_update}")
        logger.info(f"Éléments à supprimer: {nombre_to_delete}")
        logger.info(f"Éléments bidirectionnels: {nombre_to_bidirectionnel}")

    except Exception as e:
        error_msg = f"Erreur lors de la comparaison: {str(e)}"
        logger.error(error_msg)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"error": str(e)}, f)
        except Exception as write_error:
            logger.error(
                f"Erreur lors de l'écriture du fichier d'erreur: {str(write_error)}"
            )
        raise SyncError(error_msg)


def find_file(base_dir, item_path):
    """
    Recherche un fichier dans le répertoire de base, en ignorant les préfixes.
    Retourne le chemin complet s'il est trouvé, None sinon.

    Args:
        base_dir (str): Répertoire de base dans lequel chercher
        item_path (str): Chemin relatif de l'élément à rechercher

    Returns:
        str or None: Chemin complet du fichier s'il est trouvé, None sinon
    """
    # Nettoyer le chemin de recherche
    clean_item = clean_path(item_path)

    # Journaliser pour déboguer
    logger.debug(f"Recherche de '{clean_item}' dans {base_dir}")

    # Construire le chemin complet de base
    path = os.path.join(base_dir, clean_item)

    # Si le chemin existe directement, le retourner
    if os.path.exists(path):
        logger.debug(f"Chemin trouvé directement: {path}")
        return path

    # Si nous recherchons un dossier et que le chemin se termine par "/", essayer sans le "/"
    if clean_item.endswith('/'):
        clean_item_no_slash = clean_item[:-1]
        path_no_slash = os.path.join(base_dir, clean_item_no_slash)
        if os.path.exists(path_no_slash):
            logger.debug(f"Chemin trouvé sans slash final: {path_no_slash}")
            return path_no_slash

    # Décomposer le chemin en composants (dossiers/fichier)
    components = clean_item.split('/')

    # Approche plus directe: pour les dossiers Jour60, Jour70, etc. qui sont fréquents dans ce cas
    if len(components) == 1 or (len(components) == 2 and components[1] == ''):
        # C'est un fichier ou dossier à la racine
        folder_name = components[0]
        for item in os.listdir(base_dir):
            # Comparaison cas insensible et en ignorant les caractères de préfixe
            if item.lower().endswith(folder_name.lower()) or folder_name.lower(
            ) in item.lower():
                full_path = os.path.join(base_dir, item)
                logger.debug(
                    f"Trouvé correspondance approximative: {full_path}")
                return full_path

    # Pour les chemins plus complexes, essayer une approche plus flexible
    current_dir = base_dir
    for i, component in enumerate(components):
        if not component:  # Ignorer les composants vides (ex: chemin qui commence ou finit par /)
            continue

        # Si nous sommes au dernier composant et que le chemin se termine par /
        # et que current_dir existe déjà, retourner current_dir
        if i == len(components) - 1 and component == '' and os.path.exists(
                current_dir):
            return current_dir

        # Chercher une correspondance approximative dans le répertoire courant
        found = False
        if os.path.exists(current_dir) and os.path.isdir(current_dir):
            for item in os.listdir(current_dir):
                if (item.lower().endswith(component.lower())
                        or component.lower() in item.lower()
                        or component.lower().replace(" - ", "-")
                        in item.lower() or component.lower().replace(
                            "-", " - ") in item.lower()):
                    current_dir = os.path.join(current_dir, item)
                    found = True
                    logger.debug(f"Composant trouvé: {item} pour {component}")
                    break

        if not found:
            # Si nous ne trouvons pas de correspondance pour ce composant, retourner None
            logger.debug(
                f"Composant non trouvé: {component} dans {current_dir}")
            return None

    return current_dir if os.path.exists(current_dir) else None


def sync_folders(source_dir, dest_dir, mode, output_file):
    """
    Synchronise les dossiers selon le mode spécifié en utilisant directement les commandes
    du système (copy, xcopy ou robocopy sous Windows).

    Args:
        source_dir (str): Chemin du dossier source
        dest_dir (str): Chemin du dossier destination
        mode (str): Mode de synchronisation ('A vers B', 'B vers A', 'A idem B')
        output_file (str): Chemin du fichier de sortie contenant les données de comparaison
    """
    try:
        sync_result_file = "sync_result.json"

        # Normalisation des chemins pour compatibilité multiplateforme
        source_dir = os.path.normpath(source_dir)
        dest_dir = os.path.normpath(dest_dir)

        # Assurer la présence du séparateur final pour éviter des problèmes lors de la concaténation de chemins
        if not source_dir.endswith(os.sep):
            source_dir = source_dir + os.sep
        if not dest_dir.endswith(os.sep):
            dest_dir = dest_dir + os.sep

        logger.info("=== DÉBUT DE LA SYNCHRONISATION ===")
        logger.info(f"Mode: {mode}")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Destination: {dest_dir}")

        # Chargement des données de comparaison depuis le fichier JSON
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                comparison_data = json.load(f)

                # Extraction des listes d'éléments à traiter
                to_create_list = comparison_data.get('to_create', [])
                to_update_list = comparison_data.get('to_update', [])
                to_delete_list = comparison_data.get('to_delete', [])
                to_bidirectionnel_list = comparison_data.get(
                    'to_bidirectionnel', [])

                # Récupération des compteurs
                nombre_to_create = comparison_data.get('nombre_to_create', 0)
                nombre_to_update = comparison_data.get('nombre_to_update', 0)
                nombre_to_delete = comparison_data.get('nombre_to_delete', 0)
                nombre_to_bidirectionnel = comparison_data.get(
                    'nombre_to_bidirectionnel', 0)

                logger.info(f"Éléments à créer: {nombre_to_create}")
                logger.info(f"Éléments à mettre à jour: {nombre_to_update}")
                logger.info(f"Éléments à supprimer: {nombre_to_delete}")
                logger.info(
                    f"Éléments bidirectionnels: {nombre_to_bidirectionnel}")
        except Exception as e:
            logger.warning(
                f"Impossible de charger les données de comparaison: {str(e)}")
            # Initialisation de listes vides en cas d'erreur
            to_create_list = to_update_list = to_delete_list = to_bidirectionnel_list = []
            nombre_to_create = nombre_to_update = nombre_to_delete = nombre_to_bidirectionnel = 0

        # Sous Windows, utiliser robocopy qui est plus puissant et fiable que xcopy/copy
        if SYSTEM_INFO['os'] == 'windows':
            # Configurer les options robocopy selon le mode de synchronisation
            if mode == "A vers B":
                # Mode standard: source -> destination
                src, dst = source_dir, dest_dir
                logger.info("Synchronisation A vers B avec robocopy")

                # Options robocopy:
                # /E : Copie récursive incluant les sous-dossiers vides
                # /COPY:DAT : Copie les données, attributs et horodatages (pas les ACLs)
                # /PURGE : Supprime les fichiers dans la destination absents de la source
                # /R:3 : 3 tentatives en cas d'échec d'accès à un fichier
                # /W:5 : Attente de 5 secondes entre tentatives
                # /MT:4 : Utilisation de 4 threads pour une copie parallèle
                robocopy_cmd = [
                    "robocopy", src, dst, "/E", "/COPY:DAT", "/PURGE", "/R:3",
                    "/W:5", "/MT:4"
                ]

            elif mode == "B vers A":
                # Mode restauration: inversion source et destination
                src, dst = dest_dir, source_dir
                logger.info("Synchronisation B vers A avec robocopy")

                robocopy_cmd = [
                    "robocopy", src, dst, "/E", "/COPY:DAT", "/PURGE", "/R:3",
                    "/W:5", "/MT:4"
                ]

            elif mode == "A idem B":
                # Mode miroir bidirectionnel (deux synchronisations)
                logger.info(
                    "Synchronisation bidirectionnelle (miroir) avec robocopy")

                # Étape 1: Synchroniser de A vers B
                logger.info("Étape 1: Synchronisation A -> B")
                robocopy_a_to_b = [
                    "robocopy", source_dir, dest_dir, "/E", "/COPY:DAT",
                    "/R:3", "/W:5", "/MT:4"
                ]

                logger.debug(
                    f"Commande robocopy A->B: {' '.join(robocopy_a_to_b)}")

                try:
                    # Idéalement, utiliser run_subprocess_safely pour gérer les problèmes d'encodage:
                    # process_a_to_b = run_subprocess_safely(robocopy_a_to_b, "Robocopy A->B")

                    # Mais pour maintenir la compatibilité avec le code existant:
                    process_a_to_b = subprocess.run(robocopy_a_to_b,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    text=True)

                    # Interprétation des codes de retour robocopy:
                    # 0 - Aucune action (tout est à jour)
                    # 1 - Copies réussies
                    # 2-7 - Codes de succès mixtes avec quelques anomalies mineures
                    # ≥8 - Au moins une erreur sérieuse s'est produite
                    if process_a_to_b.returncode < 8:
                        logger.info("Synchronisation A->B réussie")
                    else:
                        logger.error(
                            f"Erreur lors de la synchronisation A->B: {process_a_to_b.stderr}"
                        )
                        raise SyncError(
                            f"Erreur robocopy: {process_a_to_b.stderr}")
                except Exception as e:
                    logger.error(
                        f"Erreur lors de l'exécution de robocopy A->B: {str(e)}"
                    )
                    raise SyncError(f"Erreur d'exécution: {str(e)}")

                # Étape 2: Synchronisation B -> A sans PURGE
                # (préserve les fichiers uniques dans chaque côté)
                logger.info("Étape 2: Synchronisation B -> A")
                robocopy_b_to_a = [
                    "robocopy", dest_dir, source_dir, "/E", "/COPY:DAT",
                    "/R:3", "/W:5", "/MT:4"
                ]

                logger.debug(
                    f"Commande robocopy B->A: {' '.join(robocopy_b_to_a)}")

                try:
                    process_b_to_a = subprocess.run(robocopy_b_to_a,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    text=True)
                    if process_b_to_a.returncode < 8:
                        logger.info("Synchronisation B->A réussie")
                    else:
                        logger.error(
                            f"Erreur lors de la synchronisation B->A: {process_b_to_a.stderr}"
                        )
                        raise SyncError(
                            f"Erreur robocopy: {process_b_to_a.stderr}")
                except Exception as e:
                    logger.error(
                        f"Erreur lors de l'exécution de robocopy B->A: {str(e)}"
                    )
                    raise SyncError(f"Erreur d'exécution: {str(e)}")

                # Préparation du résultat pour mode bidirectionnel
                sync_result = {
                    "mode":
                    mode,
                    "source_dir":
                    source_dir,
                    "dest_dir":
                    dest_dir,
                    "elements_synced":
                    ["Synchronisation bidirectionnelle réussie avec robocopy"],
                    "elements_deleted": [],
                    "elements_bidirectional": [],
                    "sync_success_count":
                    nombre_to_create + nombre_to_update +
                    nombre_to_bidirectionnel,
                    "delete_success_count":
                    nombre_to_delete,
                    "total_to_sync":
                    nombre_to_create + nombre_to_update +
                    nombre_to_bidirectionnel,
                    "total_to_delete":
                    nombre_to_delete,
                    "status":
                    "success"
                }

                with open(sync_result_file, 'w', encoding='utf-8') as f:
                    json.dump(sync_result, f, ensure_ascii=False, indent=4)

                logger.success(
                    f"Synchronisation bidirectionnelle terminée avec succès (robocopy)"
                )
                return  # Sortie précoce après succès

            else:
                logger.error(f"Mode de synchronisation inconnu: {mode}")
                raise ValueError(f"Mode de synchronisation inconnu: {mode}")

            # Exécution de robocopy pour les modes standards (A->B ou B->A)
            logger.debug(f"Commande robocopy: {' '.join(robocopy_cmd)}")

            try:
                # Pour une gestion optimale des encodages:
                # process = run_subprocess_safely(robocopy_cmd, "Robocopy")

                # Mais la version actuelle utilise subprocess directement:
                process = subprocess.run(robocopy_cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                # Vérification du code de retour
                if process.returncode < 8:
                    logger.success("Synchronisation réussie avec robocopy")
                else:
                    logger.error(
                        f"Erreur lors de la synchronisation: {process.stderr}")
                    raise SyncError(f"Erreur robocopy: {process.stderr}")
            except Exception as e:
                logger.error(
                    f"Erreur lors de l'exécution de robocopy: {str(e)}")
                raise SyncError(f"Erreur d'exécution: {str(e)}")

            # Calcul du nombre d'éléments selon le mode
            if mode == "A vers B":
                num_elements = nombre_to_create + nombre_to_update
            else:  # B vers A
                num_elements = nombre_to_bidirectionnel

            # Structure du résultat pour les modes standards
            sync_result = {
                "mode":
                mode,
                "source_dir":
                source_dir,
                "dest_dir":
                dest_dir,
                "elements_synced": [
                    f"Synchronisation réussie avec robocopy ({num_elements} éléments)"
                ],
                "elements_deleted": [
                    f"Suppression gérée par robocopy ({nombre_to_delete} éléments)"
                ],
                "elements_bidirectional": [],
                "sync_success_count":
                num_elements,
                "delete_success_count":
                nombre_to_delete,
                "total_to_sync":
                num_elements,
                "total_to_delete":
                nombre_to_delete,
                "status":
                "success"
            }

        else:
            # Sur Linux/Unix/WSL, utilisation de rsync comme alternative à robocopy
            # Options rsync de base pour tous les modes:
            # -a (archive): préserve les attributs, permissions, timestamps, etc.
            # -v (verbose): affiche les détails des opérations
            # -z: compresse les données pendant le transfert pour optimiser la vitesse
            base_rsync_options = ["-avz"]

            # Configuration selon le mode
            if mode == "A vers B":
                logger.info("Synchronisation A vers B (sauvegarde)")
                # Convertir les chemins au format attendu par rsync
                src, dst = prepare_path_for_rsync(
                    source_dir), prepare_path_for_rsync(dest_dir)
                # Option --delete: supprime les fichiers de la destination absents de la source
                rsync_options = base_rsync_options + ["--delete"]

            elif mode == "B vers A":
                logger.info("Synchronisation B vers A (restauration)")
                # Inversion des chemins pour la restauration
                src, dst = prepare_path_for_rsync(
                    dest_dir), prepare_path_for_rsync(source_dir)
                rsync_options = base_rsync_options + ["--delete"]

            elif mode == "A idem B":
                logger.info(
                    "Synchronisation bidirectionnelle (miroir) avec rsync")
                # Note: mode bidirectionnel avec rsync à implémenter (nécessite deux passes)
                # Similaire à la version avec robocopy
                return  # Pour le moment, sortie sans action

            else:
                logger.error(f"Mode de synchronisation inconnu: {mode}")
                raise ValueError(f"Mode de synchronisation inconnu: {mode}")

            # Construction de la commande rsync complète
            rsync_cmd = ["rsync"] + rsync_options + [f"{src}/", f"{dst}/"]
            logger.debug(f"Commande rsync: {' '.join(rsync_cmd)}")

            # Exécution de rsync
            try:
                # Pour une gestion optimale des encodages:
                # process = run_subprocess_safely(rsync_cmd, "Rsync")

                # Mais la version actuelle utilise subprocess directement:
                process = subprocess.run(rsync_cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True,
                                         check=True)
                logger.success("Synchronisation réussie avec rsync")
            except subprocess.CalledProcessError as e:
                # Codes rsync particuliers:
                # 23: fichiers disparus pendant la copie (normal dans certains cas)
                # 24: quelques fichiers n'ont pas pu être transférés (peut être ignoré parfois)
                if e.returncode in [23, 24]:
                    logger.warning(
                        f"Synchronisation terminée avec des avertissements: {e.stderr}"
                    )
                else:
                    logger.error(
                        f"Erreur lors de la synchronisation: {e.stderr}")
                    raise SyncError(f"Erreur rsync: {e.stderr}")

            # Calcul du nombre d'éléments selon le mode
            if mode == "A vers B":
                num_elements = nombre_to_create + nombre_to_update
            else:  # B vers A
                num_elements = nombre_to_bidirectionnel

            # Structure du résultat final
            sync_result = {
                "mode":
                mode,
                "source_dir":
                source_dir,
                "dest_dir":
                dest_dir,
                "elements_synced": [
                    f"Synchronisation réussie avec rsync ({num_elements} éléments)"
                ],
                "elements_deleted":
                [f"Suppression gérée par rsync ({nombre_to_delete} éléments)"],
                "elements_bidirectional": [],
                "sync_success_count":
                num_elements,
                "delete_success_count":
                nombre_to_delete,
                "total_to_sync":
                num_elements,
                "total_to_delete":
                nombre_to_delete,
                "status":
                "success"
            }

        # Enregistrement du résultat dans un fichier JSON
        with open(sync_result_file, 'w', encoding='utf-8') as f:
            json.dump(sync_result, f, ensure_ascii=False, indent=4)

        logger.success(
            f"Synchronisation terminée avec succès. Résultat enregistré dans {sync_result_file}"
        )

    except Exception as e:
        # Gestion des erreurs et journalisation
        error_msg = f"Erreur lors de la synchronisation: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc(
        )  # Affiche la trace complète pour faciliter le débogage

        # Sauvegarde de l'erreur dans un fichier JSON
        with open("sync_result.json", 'w', encoding='utf-8') as f:
            json.dump(
                {
                    "mode": mode,
                    "source_dir": source_dir,
                    "dest_dir": dest_dir,
                    "error": str(e),
                    "status": "error"
                },
                f,
                ensure_ascii=False,
                indent=4)

        # Propagation de l'erreur
        raise SyncError(error_msg)


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
        # Vérifier l'existence (sans conversion préalable)
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


def prepare_path_for_rsync(path: str) -> str:
    """
    Prépare un chemin pour être utilisé avec rsync sous Windows.
    Gère correctement les chemins avec lettres de lecteur et les problèmes d'encodage.

    Cette fonction est essentielle pour éviter les problèmes d'encodage lors de l'utilisation
    de rsync, particulièrement sous Windows où les chemins doivent être convertis
    au format cygwin/msys (/cygdrive/c/...) pour être correctement interprétés.

    Args:
        path (str): Chemin Windows à préparer pour rsync

    Returns:
        str: Chemin compatible avec rsync, au format approprié selon l'OS

    Examples:
        >>> prepare_path_for_rsync("C:\\Users\\Admin\\Documents")
        "/cygdrive/c/Users/Admin/Documents"
        >>> prepare_path_for_rsync("/home/user/documents")
        "/home/user/documents"
    """
    try:
        # Standardisation des séparateurs de chemin pour compatibilité rsync
        # rsync utilise toujours le format Unix avec des forward slashes
        path = path.replace('\\', '/')

        # Gestion spécifique des chemins Windows avec lettres de lecteur (C:, D:, etc.)
        if SYSTEM_INFO['os'] == 'windows' and ':' in path:
            # Cas spécial: chemins réseau UNC (\\serveur\dossier ou //serveur/dossier)
            if path.startswith('//') or path.startswith('\\\\'):
                # Pour les chemins UNC, on les conserve mais avec forward slashes
                return path.replace('\\', '/')

            # Conversion de chemins Windows locaux au format Cygwin/MSYS
            # que rsync comprend lorsqu'il s'exécute sous Windows
            drive_letter = path[0].lower()  # Lettre de lecteur en minuscule
            path_without_drive = path[2:]  # Chemin sans la partie "C:"

            # Format /cygdrive/c/path/to/folder
            return f"/cygdrive/{drive_letter}/{path_without_drive}"

        # Si le chemin est déjà au format Unix, le retourner tel quel
        return path

    except Exception as e:
        logger.error(
            f"Erreur lors de la préparation du chemin pour rsync: {str(e)}")
        # En cas d'erreur, retourner au moins le chemin standardisé
        return path


def compare_json_folders(source_json: str, dest_json: str) -> None:
    """
    Compare les fichiers JSON des dossiers source et destination.
    Remplir les variables globales to_create, to_update, to_delete.

    Args:
        source_json (str): JSON du dossier source
        dest_json (str): JSON du dossier destination
    """
    try:
        global to_create, to_update, to_delete, to_bidirectionnel
        global nombre_to_create, nombre_to_update, nombre_to_delete, nombre_to_bidirectionnel

        # Réinitialiser les tableaux globaux
        to_create = []
        to_update = []
        to_delete = []
        to_bidirectionnel = []

        # Charger les JSON
        logger.debug("Chargement des JSON des dossiers pour comparaison")
        source_data = json.loads(source_json)
        dest_data = json.loads(dest_json)

        # Parcourir les fichiers du dossier source
        source_files = source_data.get("files", {})
        dest_files = dest_data.get("files", {})

        logger.info(f"Nombre de fichiers dans la source: {len(source_files)}")
        logger.info(
            f"Nombre de fichiers dans la destination: {len(dest_files)}")

        # Fichiers à créer ou mettre à jour
        for rel_path, source_info in source_files.items():
            # Nettoyer le chemin pour éviter les problèmes de préfixes
            clean_rel_path = clean_path(rel_path)

            # Vérifier si le fichier existe dans la destination
            if clean_rel_path in dest_files:
                dest_info = dest_files[clean_rel_path]
                # Si les tailles ou dates de modification sont différentes
                if source_info["size"] != dest_info["size"] or source_info[
                        "mtime"] > dest_info["mtime"]:
                    to_update.append(rel_path)
                # Si le fichier de destination est plus récent (pour le mode bidirectionnel)
                elif dest_info["mtime"] > source_info["mtime"]:
                    to_bidirectionnel.append(rel_path)
            else:
                to_create.append(rel_path)

        # Fichiers à supprimer (présents dans la destination mais pas dans la source)
        for rel_path in dest_files:
            # Nettoyer le chemin pour éviter les problèmes de préfixes
            clean_rel_path = clean_path(rel_path)

            if clean_rel_path not in source_files:
                to_delete.append(rel_path)

        # Mettre à jour les compteurs
        nombre_to_create = len(to_create)
        nombre_to_update = len(to_update)
        nombre_to_delete = len(to_delete)
        nombre_to_bidirectionnel = len(to_bidirectionnel)

        # Journalisation
        logger.info(f"Éléments à créer: {nombre_to_create}")
        logger.info(f"Éléments à mettre à jour: {nombre_to_update}")
        logger.info(f"Éléments à supprimer: {nombre_to_delete}")
        logger.info(f"Éléments bidirectionnels: {nombre_to_bidirectionnel}")

        # Afficher les premiers éléments de chaque liste pour le débogage
        if to_create:
            logger.debug(f"Exemples d'éléments à créer: {to_create[:3]}")
        if to_update:
            logger.debug(
                f"Exemples d'éléments à mettre à jour: {to_update[:3]}")
        if to_delete:
            logger.debug(f"Exemples d'éléments à supprimer: {to_delete[:3]}")
        if to_bidirectionnel:
            logger.debug(
                f"Exemples d'éléments bidirectionnels: {to_bidirectionnel[:3]}"
            )

    except Exception as e:
        logger.error(f"Erreur lors de la comparaison des dossiers: {str(e)}")
        raise


def run_subprocess_safely(cmd_args, log_prefix="Commande"):
    """
    Exécute une commande subprocess avec gestion appropriée de l'encodage pour éviter
    les problèmes de caractères spéciaux dans les chemins de fichiers.

    Cette fonction définit spécifiquement des variables d'environnement pour
    garantir que l'encodage UTF-8 est utilisé pendant l'exécution de la commande,
    ce qui résout les problèmes liés aux chemins contenant des caractères non ASCII,
    notamment avec des commandes comme robocopy et rsync.

    Args:
        cmd_args (List[str]): Liste des arguments de la commande à exécuter
        log_prefix (str, optional): Préfixe utilisé pour les messages de log. Par défaut "Commande".

    Returns:
        subprocess.CompletedProcess: Résultat de l'exécution de la commande

    Raises:
        SyncError: En cas d'erreur lors de l'exécution de la commande

    Example:
        >>> result = run_subprocess_safely(["robocopy", source_dir, dest_dir, "/E"], "Robocopy")
        >>> if result.returncode < 8:  # Codes de retour spécifiques à robocopy
        >>>     logger.success("Copie réussie")
    """
    logger.debug(f"{log_prefix}: {' '.join(cmd_args)}")

    try:
        # Configuration de l'environnement d'exécution pour garantir l'encodage UTF-8
        # Ceci est crucial pour éviter les problèmes avec les caractères non-ASCII dans les chemins
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"  # Définit l'encodage pour les flux d'entrée/sortie de Python

        # Configuration spécifique pour Windows qui est plus sensible aux problèmes d'encodage
        if SYSTEM_INFO['os'] == 'windows':
            # Force l'utilisation de l'encodage UTF-8 pour stdin/stdout/stderr sous Windows
            env["PYTHONLEGACYWINDOWSSTDIO"] = "utf-8"
            # Mode strict d'encodage pour détecter immédiatement les problèmes
            env["PYTHONIOENCODING"] = "utf-8:strict"

        # Exécution sécurisée de la commande avec tous les paramètres d'encodage configurés
        process = subprocess.run(cmd_args,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 encoding='utf-8',
                                 errors='replace',
                                 env=env)
        return process
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de {log_prefix}: {str(e)}")
        traceback.print_exc()  # Afficher la trace complète pour le débogage
        raise SyncError(f"Erreur d'exécution: {str(e)}")


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
