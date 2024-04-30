import os
from pathlib import Path
import logging
import sys

logger = logging.getLogger('colorlog_example')


def trouver_nom_workspace(fichier_marqueur: str = '.git') -> str:
    """
    Trouve le nom du workspace en montant dans l'arborescence des dossiers
    à partir du répertoire courant jusqu'à trouver un dossier contenant
    un fichier ou dossier marqueur spécifique.

    Args:
        fichier_marqueur (str): Le nom du fichier ou dossier marqueur à chercher.
                                Par défaut, '.git'.
    Returns:
        str: Le nom du dossier considéré comme workspace.

    Raises:
        ValueError: Si aucun dossier contenant le fichier marqueur n'est trouvé.
    """
    logger.debug(f"\n fichier_marqueur:\n{fichier_marqueur} \n")
    chemin_courant = Path().resolve()
    logger.debug(f"\n chemin_courant:\n{chemin_courant} \n")

    for chemin in [chemin_courant] + list(chemin_courant.parents):
        logger.debug(f"\nlist(chemin_courant.parents) :\n    {list(chemin_courant.parents)} \n")
        logger.debug(f"\nchemin :\n{chemin} \n")
        logger.debug(
            f"\nchemin / fichier_marqueur :\n{chemin / fichier_marqueur} \n")
        if (chemin / fichier_marqueur).exists():
            return chemin.name, chemin

    raise ValueError(f"Aucun dossier contenant le fichier marqueur:'{                     fichier_marqueur}' n'a été trouvé.")

# Exemple d'utilisation
# logger.debug(f"Le nom du workspace en cours est : {trouver_nom_workspace('.vscode')}")


def trouver_chemin_element_depuis_workspace(nom_element: str, est_un_dossier: bool = True) -> Path:
    """
    Recherche dans le workspace donné pour trouver un dossier ou le fichier le plus récent par son nom.
    Parcourt tous les sous-dossiers du workspace spécifié pour trouver l'élément cible.

    Args:
        nom_dossier_workspace (str): Le nom du dossier workspace dans lequel chercher.
        nom_element (str): Le nom du dossier ou fichier cible à trouver.
        est_un_dossier (bool): True si on cherche un dossier, False si on cherche un fichier.

    Returns:
        Path: Le chemin absolu vers le dossier ou fichier trouvé.

    Raises:
        ValueError: Si l'élément spécifié n'est pas trouvé dans le workspace.
    """
    nom_dossier_workspace, chemin_workspace = trouver_nom_workspace('.vscode')
    logger.debug(f"\n nom_dossier_workspace:\n{nom_dossier_workspace} \n")
    logger.debug(f"\n chemin_workspace:\n{chemin_workspace} \n")
    elements_trouves = []
    # Recherche de l'élément spécifié dans tous les sous-dossiers du workspace
    for chemin in chemin_workspace.rglob(nom_element):
        if est_un_dossier and chemin.is_dir():
            #  ajout du chemin dans le path afin de l'importer
            logger.debug(f"\n sys.path :\n{sys.path} \n")
            logger.debug(f"\n chemin:\n{chemin} \n")
            if str(chemin) not in sys.path:
                # ajoute le chemin au PATH
                sys.path.append(str(chemin))
            return chemin
        elif not est_un_dossier and chemin.is_file():

            elements_trouves.append(chemin)

    if not est_un_dossier and elements_trouves:
        # Trier les fichiers trouvés par date de modification et retourner le plus récent
        chemin_fichier = max(elements_trouves, key=os.path.getmtime)
        if str(chemin_fichier) not in sys.path:
            sys.path.append(str(chemin_fichier))

        return chemin_fichier

    raise ValueError(f"{'Dossier' if est_un_dossier else 'Fichier'} '{ nom_element}' non trouvé dans le workspace '{nom_dossier_workspace}'.")


# # Exemple d'utilisation
# try:
#     # Pour trouver un dossier
#     chemin_dossier = trouver_chemin_element_depuis_workspace(
#         "outils", est_un_dossier=True)
#     logger.debug(f"Chemin du dossier 'outils' trouvé : {chemin_dossier}")

#     # Pour trouver le fichier le plus récent
#     chemin_fichier = trouver_chemin_element_depuis_workspace(
#         "fichier.log", est_un_dossier=False)
#     logger.debug(f"Chemin du fichier 'fichier.log' le plus récent trouvé : {          chemin_fichier}")
# except ValueError as e:
#     logger.debug(e)
