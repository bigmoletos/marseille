"""
Module dédié à la synchronisation bidirectionnelle de dossiers.
Ne fait que copier les fichiers manquants ou plus récents dans les deux sens.

Ce module permet de :
- Sélectionner deux dossiers via l'explorateur Windows
- Comparer les fichiers entre les deux dossiers
- Copier les fichiers manquants dans les deux sens
- Mettre à jour les fichiers plus récents dans les deux sens
- Créer automatiquement les dossiers manquants
- Préserver les dates de modification

Utilisation:
    python sync_bidirectional.py

Logs:
    Les logs sont écrits dans la console et dans un fichier 'sync.log'
"""

import os
import shutil
import logging
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Tuple, List, Set, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('sync.log', encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)


def select_folder() -> Optional[Path]:
    """
    Ouvre une boîte de dialogue pour sélectionner un dossier via l'explorateur Windows.

    Returns:
        Path: Chemin du dossier sélectionné
        None: Si l'utilisateur annule la sélection

    Raises:
        OSError: En cas d'erreur d'accès au système de fichiers
    """
    try:
        logger.debug("Ouverture du sélecteur de dossiers")

        # Cacher la fenêtre principale Tkinter
        root = tk.Tk()
        root.withdraw()

        # Ouvrir le sélecteur de dossier
        folder_path = filedialog.askdirectory(
            title="Sélectionner un dossier",
            initialdir=os.path.expanduser("~"))

        if folder_path:
            path = Path(folder_path)
            logger.info(f"Dossier sélectionné: {path}")
            return path

        logger.info("Sélection annulée par l'utilisateur")
        return None

    except Exception as e:
        logger.error(f"Erreur lors de la sélection du dossier: {e}")
        raise


def get_files_to_sync(source: Path,
                      dest: Path) -> Tuple[List[Path], List[Path]]:
    """
    Compare deux dossiers et retourne les fichiers à synchroniser dans chaque direction.

    La comparaison se fait sur :
    - L'existence des fichiers
    - Les dates de modification

    Args:
        source: Dossier source
        dest: Dossier destination

    Returns:
        Tuple[List[Path], List[Path]]:
            - Liste des fichiers à copier de source vers dest
            - Liste des fichiers à copier de dest vers source

    Raises:
        FileNotFoundError: Si un des dossiers n'existe pas
        PermissionError: Si accès refusé à un dossier
        OSError: Pour les autres erreurs système
    """
    try:
        logger.info("=== DÉBUT ANALYSE DES DIFFÉRENCES ===")
        logger.info(f"Comparaison de:")
        logger.info(f"  Source: {source}")
        logger.info(f"  Destination: {dest}")

        to_copy_to_dest = []
        to_copy_to_source = []

        # Vérification des dossiers
        if not source.exists() or not dest.exists():
            raise FileNotFoundError("Les deux dossiers doivent exister")

        # Parcourir les fichiers du dossier source
        logger.info("Analyse des fichiers source...")
        for src_file in source.rglob('*'):
            try:
                if src_file.is_file():
                    rel_path = src_file.relative_to(source)
                    dst_file = dest / rel_path

                    if not dst_file.exists():
                        to_copy_to_dest.append(rel_path)
                        logger.debug(
                            f"À copier vers dest (absent): {rel_path}")
                    elif src_file.stat().st_mtime > dst_file.stat().st_mtime:
                        to_copy_to_dest.append(rel_path)
                        logger.debug(
                            f"À copier vers dest (plus récent): {rel_path}")
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {src_file}: {e}")
                continue

        # Parcourir les fichiers du dossier destination
        logger.info("Analyse des fichiers destination...")
        for dst_file in dest.rglob('*'):
            try:
                if dst_file.is_file():
                    rel_path = dst_file.relative_to(dest)
                    src_file = source / rel_path

                    if not src_file.exists():
                        to_copy_to_source.append(rel_path)
                        logger.debug(
                            f"À copier vers source (absent): {rel_path}")
                    elif dst_file.stat().st_mtime > src_file.stat().st_mtime:
                        to_copy_to_source.append(rel_path)
                        logger.debug(
                            f"À copier vers source (plus récent): {rel_path}")
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {dst_file}: {e}")
                continue

        logger.info("=== RÉSUMÉ DE L'ANALYSE ===")
        logger.info(
            f"Fichiers à copier vers destination: {len(to_copy_to_dest)}")
        logger.info(f"Fichiers à copier vers source: {len(to_copy_to_source)}")

        return to_copy_to_dest, to_copy_to_source

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des différences: {e}")
        raise


def sync_bidirectional(source: Path, dest: Path) -> None:
    """
    Synchronise deux dossiers de manière bidirectionnelle.

    Le processus :
    1. Vérifie l'existence des dossiers
    2. Compare les fichiers dans les deux sens
    3. Copie les fichiers manquants ou plus récents
    4. Crée les dossiers parents si nécessaire

    Args:
        source: Premier dossier
        dest: Second dossier

    Raises:
        FileNotFoundError: Si un des dossiers n'existe pas
        PermissionError: Si accès refusé
        OSError: Pour les autres erreurs système
    """
    try:
        logger.info("=== DÉBUT SYNCHRONISATION ===")
        logger.info(f"Source: {source}")
        logger.info(f"Destination: {dest}")

        # Vérifier que les dossiers existent
        if not source.exists() or not dest.exists():
            raise FileNotFoundError("Les deux dossiers doivent exister")

        # Obtenir les listes de fichiers à synchroniser
        to_copy_to_dest, to_copy_to_source = get_files_to_sync(source, dest)

        # Copier les fichiers vers la destination
        logger.info("Copie des fichiers vers destination...")
        for rel_path in to_copy_to_dest:
            try:
                src_file = source / rel_path
                dst_file = dest / rel_path

                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                logger.info(f"Copié vers destination: {rel_path}")
            except Exception as e:
                logger.error(f"Erreur lors de la copie de {rel_path}: {e}")
                continue

        # Copier les fichiers vers la source
        logger.info("Copie des fichiers vers source...")
        for rel_path in to_copy_to_source:
            try:
                dst_file = dest / rel_path
                src_file = source / rel_path

                src_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dst_file, src_file)
                logger.info(f"Copié vers source: {rel_path}")
            except Exception as e:
                logger.error(f"Erreur lors de la copie de {rel_path}: {e}")
                continue

        total_copies = len(to_copy_to_dest) + len(to_copy_to_source)
        logger.info("=== SYNCHRONISATION TERMINÉE ===")
        logger.info(f"Total fichiers copiés: {total_copies}")

    except Exception as e:
        logger.error(f"Erreur critique lors de la synchronisation: {e}")
        raise


if __name__ == "__main__":
    try:
        print("=== SYNCHRONISATION BIDIRECTIONNELLE DE DOSSIERS ===")

        # Sélection des dossiers
        print("\nSélectionnez le premier dossier:")
        source_dir = select_folder()
        if not source_dir:
            print("Opération annulée")
            exit()

        print("\nSélectionnez le second dossier:")
        dest_dir = select_folder()
        if not dest_dir:
            print("Opération annulée")
            exit()

        # Confirmation
        print(f"\nDossiers sélectionnés:")
        print(f"1: {source_dir}")
        print(f"2: {dest_dir}")

        confirm = input("\nLancer la synchronisation ? (o/n): ").lower()
        if confirm != 'o':
            print("Opération annulée")
            exit()

        # Synchronisation
        print("\nDémarrage de la synchronisation...")
        sync_bidirectional(source_dir, dest_dir)
        print("\nSynchronisation terminée avec succès!")

    except Exception as e:
        print(f"\nErreur critique: {str(e)}")
        logger.exception("Détails de l'erreur:")
        exit(1)

    finally:
        input("\nAppuyez sur Entrée pour quitter...")
