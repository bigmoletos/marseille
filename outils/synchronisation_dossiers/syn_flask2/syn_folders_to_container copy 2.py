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


def compare_folders(source_dir: str,
                    dest_dir: str,
                    mode: str,
                    output_file: str,
                    script_path: str = None) -> None:
    """
    Compare deux dossiers selon le mode spécifié.

    Args:
        source_dir (str): Chemin du dossier source
        dest_dir (str): Chemin du dossier destination
        mode (str): Mode de comparaison ('A vers B', 'B vers A', 'A idem B')
        output_file (str): Chemin du fichier de sortie JSON
        script_path (str, optional): Chemin du script bash (non utilisé en natif)
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
        # Ne pas convertir systématiquement les chemins
        logger.info("=== DÉBUT DE LA SYNCHRONISATION ===")
        logger.info(f"Mode: {mode}")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Destination: {dest_dir}")
        logger.info(f"Fichier de sortie: {output_file}")

        # Vérifier que les dossiers existent et sont accessibles
        valid_source, source_error = check_path(source_dir, "Source")
        valid_dest, dest_error = check_path(dest_dir, "Destination")

        if not valid_source or not valid_dest:
            error_msg = source_error if not valid_source else dest_error
            logger.error(error_msg)
            raise SyncError(error_msg)

        # Préparer les chemins pour rsync
        rsync_source_dir = prepare_path_for_rsync(source_dir)
        rsync_dest_dir = prepare_path_for_rsync(dest_dir)

        logger.info(f"Chemin source préparé pour rsync: {rsync_source_dir}")
        logger.info(f"Chemin destination préparé pour rsync: {rsync_dest_dir}")

        # Si un fichier de résultat de comparaison est fourni
        sync_result = {
            "status": "success",
            "error": None,
            "source_dir": source_dir,
            "dest_dir": dest_dir,
            "mode": mode,
            "files_created": [],
            "files_updated": [],
            "files_deleted": []
        }

        # Vérifier si on a des données de comparaison
        comparison_data = None
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    comparison_data = json.load(f)
                    logger.info(
                        f"Données de comparaison chargées depuis {output_file}"
                    )
            except Exception as e:
                logger.warning(
                    f"Impossible de charger les données de comparaison: {str(e)}"
                )

        if mode == "A vers B":
            logger.info("Mode de synchronisation: A vers B (sauvegarde)")

            if comparison_data:
                # Utiliser les résultats de la comparaison
                to_create = comparison_data.get("to_create", [])
                to_update = comparison_data.get("to_update", [])
                to_delete = comparison_data.get("to_delete", [])

                # Synchronisation des fichiers à créer et mettre à jour
                if to_create or to_update:
                    logger.info(
                        f"Synchronisation de {len(to_create) + len(to_update)} éléments à créer/mettre à jour"
                    )

                    # Créer un fichier d'inclusion pour rsync
                    include_file = tempfile.NamedTemporaryFile(delete=False,
                                                               mode='w')
                    for item in to_create + to_update:
                        include_file.write(f"+ {item}\n")
                        include_file.write(f"+ {item}/**\n")
                    include_file.write("- *\n")
                    include_file.close()

                    # Exécuter rsync avec le fichier d'inclusion
                    rsync_cmd = [
                        "rsync", "-rtlv", "--progress",
                        f"--include-from={include_file.name}",
                        f"{rsync_source_dir}/", f"{rsync_dest_dir}/"
                    ]
                    logger.debug(
                        f"Exécution de la commande rsync (créer/mettre à jour): {' '.join(rsync_cmd)}"
                    )

                    try:
                        subprocess.run(rsync_cmd,
                                       check=True,
                                       text=True,
                                       capture_output=True)
                        sync_result["files_created"] = to_create
                        sync_result["files_updated"] = to_update
                    except subprocess.CalledProcessError as e:
                        logger.error(
                            f"Erreur rsync (créer/mettre à jour): {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de la synchronisation (créer/mettre à jour): {e.stderr}"
                        )
                    finally:
                        os.unlink(include_file.name)

                # Suppression des fichiers si nécessaire
                if to_delete:
                    logger.info(f"Suppression de {len(to_delete)} éléments")
                    for item in to_delete:
                        path_to_delete = os.path.join(dest_dir, item)
                        if os.path.exists(path_to_delete):
                            try:
                                if os.path.isfile(path_to_delete):
                                    os.remove(path_to_delete)
                                    logger.info(f"Fichier supprimé: {item}")
                                elif os.path.isdir(path_to_delete):
                                    shutil.rmtree(path_to_delete)
                                    logger.info(f"Dossier supprimé: {item}")
                                sync_result["files_deleted"].append(item)
                            except Exception as e:
                                logger.error(
                                    f"Erreur lors de la suppression de {item}: {str(e)}"
                                )
            else:
                # Synchronisation directe avec rsync
                logger.info(
                    "Synchronisation directe avec rsync (pas de données de comparaison)"
                )
                rsync_cmd = [
                    "rsync", "-rtlv", "--progress", "--delete",
                    f"{rsync_source_dir}/", f"{rsync_dest_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync: {' '.join(rsync_cmd)}")

                try:
                    subprocess.run(rsync_cmd,
                                   check=True,
                                   text=True,
                                   capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Erreur rsync: {e.stderr}")
                    raise SyncError(
                        f"Erreur lors de la synchronisation: {e.stderr}")

        elif mode == "B vers A":
            logger.info("Mode de synchronisation: B vers A (restauration)")

            if comparison_data:
                # Utiliser les résultats de la comparaison
                to_bidirectionnel = comparison_data.get(
                    "to_bidirectionnel", [])
                to_delete = comparison_data.get("to_delete", [])

                # Synchronisation des fichiers à créer et mettre à jour
                if to_bidirectionnel:
                    logger.info(
                        f"Synchronisation de {len(to_bidirectionnel)} éléments à créer/mettre à jour"
                    )

                    # Créer un fichier d'inclusion pour rsync
                    include_file = tempfile.NamedTemporaryFile(delete=False,
                                                               mode='w')
                    for item in to_bidirectionnel:
                        include_file.write(f"+ {item}\n")
                        include_file.write(f"+ {item}/**\n")
                    include_file.write("- *\n")
                    include_file.close()

                    # Exécuter rsync avec le fichier d'inclusion
                    rsync_cmd = [
                        "rsync", "-rtlv", "--progress",
                        f"--include-from={include_file.name}",
                        f"{rsync_dest_dir}/", f"{rsync_source_dir}/"
                    ]
                    logger.debug(
                        f"Exécution de la commande rsync (créer/mettre à jour): {' '.join(rsync_cmd)}"
                    )

                    try:
                        subprocess.run(rsync_cmd,
                                       check=True,
                                       text=True,
                                       capture_output=True)
                        sync_result["files_created"] = to_bidirectionnel
                    except subprocess.CalledProcessError as e:
                        logger.error(
                            f"Erreur rsync (créer/mettre à jour): {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de la synchronisation (créer/mettre à jour): {e.stderr}"
                        )
                    finally:
                        os.unlink(include_file.name)

                # Suppression des fichiers si nécessaire
                if to_delete:
                    logger.info(f"Suppression de {len(to_delete)} éléments")
                    for item in to_delete:
                        path_to_delete = os.path.join(source_dir, item)
                        if os.path.exists(path_to_delete):
                            try:
                                if os.path.isfile(path_to_delete):
                                    os.remove(path_to_delete)
                                    logger.info(f"Fichier supprimé: {item}")
                                elif os.path.isdir(path_to_delete):
                                    shutil.rmtree(path_to_delete)
                                    logger.info(f"Dossier supprimé: {item}")
                                sync_result["files_deleted"].append(item)
                            except Exception as e:
                                logger.error(
                                    f"Erreur lors de la suppression de {item}: {str(e)}"
                                )
            else:
                # Synchronisation directe avec rsync
                logger.info(
                    "Synchronisation directe avec rsync (pas de données de comparaison)"
                )
                rsync_cmd = [
                    "rsync", "-rtlv", "--progress", "--delete",
                    f"{rsync_dest_dir}/", f"{rsync_source_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync: {' '.join(rsync_cmd)}")

                try:
                    subprocess.run(rsync_cmd,
                                   check=True,
                                   text=True,
                                   capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Erreur rsync: {e.stderr}")
                    raise SyncError(
                        f"Erreur lors de la synchronisation: {e.stderr}")

        elif mode == "A idem B" or mode == "Bidirectionnel":
            logger.info("Mode de synchronisation: Bidirectionnel (miroir)")

            if comparison_data:
                # Utiliser les résultats de la comparaison
                to_create = comparison_data.get("to_create", [])
                to_update = comparison_data.get("to_update", [])
                to_bidirectionnel = comparison_data.get(
                    "to_bidirectionnel", [])

                # 1. Synchronisation A vers B
                if to_create or to_update:
                    logger.info(
                        f"Synchronisation A vers B: {len(to_create) + len(to_update)} éléments"
                    )

                    # Créer un fichier d'inclusion pour rsync
                    include_file_ab = tempfile.NamedTemporaryFile(delete=False,
                                                                  mode='w')
                    for item in to_create + to_update:
                        include_file_ab.write(f"+ {item}\n")
                        include_file_ab.write(f"+ {item}/**\n")
                    include_file_ab.write("- *\n")
                    include_file_ab.close()

                    # Exécuter rsync avec le fichier d'inclusion
                    rsync_cmd_ab = [
                        "rsync", "-rtlv", "--progress",
                        f"--include-from={include_file_ab.name}",
                        f"{rsync_source_dir}/", f"{rsync_dest_dir}/"
                    ]
                    logger.debug(
                        f"Exécution de la commande rsync A->B: {' '.join(rsync_cmd_ab)}"
                    )

                    try:
                        subprocess.run(rsync_cmd_ab,
                                       check=True,
                                       text=True,
                                       capture_output=True)
                        sync_result["files_created"] = to_create
                        sync_result["files_updated"] = to_update
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync A->B: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de la synchronisation A->B: {e.stderr}"
                        )
                    finally:
                        os.unlink(include_file_ab.name)

                # 2. Synchronisation B vers A
                if to_bidirectionnel:
                    logger.info(
                        f"Synchronisation B vers A: {len(to_bidirectionnel)} éléments"
                    )

                    # Créer un fichier d'inclusion pour rsync
                    include_file_ba = tempfile.NamedTemporaryFile(delete=False,
                                                                  mode='w')
                    for item in to_bidirectionnel:
                        include_file_ba.write(f"+ {item}\n")
                        include_file_ba.write(f"+ {item}/**\n")
                    include_file_ba.write("- *\n")
                    include_file_ba.close()

                    # Exécuter rsync avec le fichier d'inclusion
                    rsync_cmd_ba = [
                        "rsync", "-rtlv", "--progress",
                        f"--include-from={include_file_ba.name}",
                        f"{rsync_dest_dir}/", f"{rsync_source_dir}/"
                    ]
                    logger.debug(
                        f"Exécution de la commande rsync B->A: {' '.join(rsync_cmd_ba)}"
                    )

                    try:
                        subprocess.run(rsync_cmd_ba,
                                       check=True,
                                       text=True,
                                       capture_output=True)
                        sync_result["files_bidirectional"] = to_bidirectionnel
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Erreur rsync B->A: {e.stderr}")
                        raise SyncError(
                            f"Erreur lors de la synchronisation B->A: {e.stderr}"
                        )
                    finally:
                        os.unlink(include_file_ba.name)
            else:
                # Synchronisation bidirectionnelle directe
                logger.info(
                    "Synchronisation bidirectionnelle directe (pas de données de comparaison)"
                )

                # Synchronisation A vers B
                rsync_cmd_ab = [
                    "rsync", "-rtlv", "--progress", f"{rsync_source_dir}/",
                    f"{rsync_dest_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync A->B: {' '.join(rsync_cmd_ab)}"
                )

                try:
                    subprocess.run(rsync_cmd_ab,
                                   check=True,
                                   text=True,
                                   capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Erreur rsync A->B: {e.stderr}")
                    raise SyncError(
                        f"Erreur lors de la synchronisation A->B: {e.stderr}")

                # Synchronisation B vers A
                rsync_cmd_ba = [
                    "rsync", "-rtlv", "--progress", f"{rsync_dest_dir}/",
                    f"{rsync_source_dir}/"
                ]
                logger.debug(
                    f"Exécution de la commande rsync B->A: {' '.join(rsync_cmd_ba)}"
                )

                try:
                    subprocess.run(rsync_cmd_ba,
                                   check=True,
                                   text=True,
                                   capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Erreur rsync B->A: {e.stderr}")
                    raise SyncError(
                        f"Erreur lors de la synchronisation B->A: {e.stderr}")

        # Sauvegarder le résultat de la synchronisation
        sync_result_file = os.path.join(os.path.dirname(output_file),
                                        "sync_result.json")
        with open(sync_result_file, 'w', encoding='utf-8') as f:
            json.dump(sync_result, f, indent=2)

        logger.success(
            f"Synchronisation terminée avec succès. Résultat enregistré dans {sync_result_file}"
        )

    except Exception as e:
        error_msg = f"Erreur lors de la synchronisation: {str(e)}"
        logger.error(error_msg)
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
    Prépare un chemin pour être utilisé avec rsync.
    Si nécessaire sous Windows, convertit le format du chemin.

    Args:
        path (str): Chemin à préparer

    Returns:
        str: Chemin préparé pour rsync
    """
    try:
        # Si nous sommes sous Windows et que le chemin contient un lecteur (e.g., C:)
        if SYSTEM_INFO['os'] == 'windows' and ':' in path:
            # Utiliser le format cygwin/msys pour rsync
            drive_letter = path[0].lower()
            path_normalized = path[2:].replace('\\', '/')
            return f"/cygdrive/{drive_letter}/{path_normalized}"

        # Normaliser les séparateurs pour rsync (toujours forward slash)
        return path.replace('\\', '/')

    except Exception as e:
        logger.error(
            f"Erreur lors de la préparation du chemin pour rsync: {str(e)}")
        # En cas d'erreur, retourner le chemin normalisé
        return path.replace('\\', '/')


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
