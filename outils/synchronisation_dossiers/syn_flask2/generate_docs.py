#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer la documentation à partir des docstrings du projet.

Ce script utilise pydoc-markdown pour générer une documentation en Markdown
à partir des docstrings des modules Python du projet.
"""

import os
import subprocess
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("generate_docs")


def check_requirements():
    """
    Vérifie si pydoc-markdown est installé et l'installe si nécessaire.

    Returns:
        bool: True si pydoc-markdown est disponible, False sinon
    """
    try:
        import pydoc_markdown
        logger.info("pydoc-markdown est déjà installé.")
        return True
    except ImportError:
        logger.warning(
            "pydoc-markdown n'est pas installé. Tentative d'installation...")
        try:
            subprocess.run(["pip", "install", "pydoc-markdown"],
                           check=True,
                           capture_output=True)
            logger.info("pydoc-markdown a été installé avec succès.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Erreur lors de l'installation de pydoc-markdown: {e.stderr.decode()}"
            )
            return False


def create_docs_directory():
    """
    Crée le répertoire docs s'il n'existe pas.
    """
    Path("docs").mkdir(exist_ok=True)
    logger.info("Répertoire 'docs' vérifié.")


def generate_module_documentation(module_name, output_file):
    """
    Génère la documentation pour un module spécifique.

    Args:
        module_name (str): Nom du module à documenter
        output_file (str): Chemin du fichier de sortie

    Returns:
        bool: True si la génération a réussi, False sinon
    """
    try:
        cmd = [
            "pydoc-markdown", "-I", ".", "-m", module_name, "--render-toc",
            "-O", output_file
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(
            f"Documentation générée pour le module '{module_name}' dans '{output_file}'"
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Erreur lors de la génération de la documentation pour '{module_name}': {e.stderr.decode()}"
        )
        return False


def generate_all_documentation():
    """
    Génère la documentation pour tous les modules Python du projet.
    """
    # Liste des modules à documenter
    modules = [
        "app",
        "syn_folders_to_container",
    ]

    # Créer le répertoire de documentation
    create_docs_directory()

    # Vérifier et installer les dépendances
    if not check_requirements():
        logger.error("Impossible de continuer sans pydoc-markdown.")
        return False

    # Générer la documentation pour chaque module
    for module in modules:
        output_file = f"docs/{module}.md"
        generate_module_documentation(module, output_file)

    # Générer un index pour tous les modules
    with open("docs/index.md", "w", encoding="utf-8") as index_file:
        index_file.write(
            "# Documentation de l'Application de Synchronisation de Dossiers\n\n"
        )
        index_file.write("## Modules disponibles\n\n")

        for module in modules:
            index_file.write(f"- [{module}]({module}.md)\n")

        index_file.write("\n\n## Comment utiliser cette documentation\n\n")
        index_file.write(
            "Cliquez sur les liens ci-dessus pour accéder à la documentation détaillée de chaque module.\n"
        )

    logger.info("Index de documentation généré dans 'docs/index.md'")
    return True


if __name__ == "__main__":
    logger.info("Démarrage de la génération de la documentation...")
    if generate_all_documentation():
        logger.info(
            "Documentation générée avec succès dans le répertoire 'docs/'")
    else:
        logger.error(
            "Des erreurs se sont produites lors de la génération de la documentation."
        )
