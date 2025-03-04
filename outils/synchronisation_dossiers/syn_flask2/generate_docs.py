#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer la documentation à partir des docstrings du projet.

Ce script utilise le module inspect de Python pour générer une documentation en Markdown
à partir des docstrings des modules Python du projet.
"""

import os
import logging
import inspect
import importlib
import sys
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("generate_docs")


def create_docs_directory():
    """
    Crée le répertoire docs s'il n'existe pas.
    """
    Path("docs").mkdir(exist_ok=True)
    logger.info("Répertoire 'docs' vérifié.")


def format_docstring(doc):
    """
    Formate un docstring pour l'affichage Markdown.

    Args:
        doc (str): Docstring à formater

    Returns:
        str: Docstring formaté
    """
    if not doc:
        return "*Pas de documentation disponible*"

    # Nettoyer le docstring
    lines = doc.strip().split('\n')
    if len(lines) > 0:
        # Supprimer l'indentation
        indent = len(lines[0]) - len(lines[0].lstrip())
        lines = [
            line[indent:] if line.startswith(' ' * indent) else line
            for line in lines
        ]

    return '\n'.join(lines)


def inspect_function(func):
    """
    Génère la documentation pour une fonction.

    Args:
        func: Fonction à documenter

    Returns:
        str: Documentation au format Markdown
    """
    doc = inspect.getdoc(func) or ""

    # Récupérer la signature
    try:
        signature = inspect.signature(func)
        sig_str = f"{func.__name__}{signature}"
    except (ValueError, TypeError):
        sig_str = f"{func.__name__}(*args, **kwargs)"

    # Analyser les paramètres et la valeur de retour depuis le docstring
    params_docs = []
    return_doc = ""

    if "Args:" in doc:
        # Extraction simple des arguments
        args_section = doc.split("Args:")[1]
        if "Returns:" in args_section:
            args_section = args_section.split("Returns:")[0]
        elif "Raises:" in args_section:
            args_section = args_section.split("Raises:")[0]

        for line in args_section.strip().split('\n'):
            if line.strip() and ':' in line:
                params_docs.append(f"- {line.strip()}")

    if "Returns:" in doc:
        # Extraction simple du retour
        returns_section = doc.split("Returns:")[1]
        if "Raises:" in returns_section:
            returns_section = returns_section.split("Raises:")[0]
        return_doc = returns_section.strip()

    # Créer la documentation de la fonction
    markdown = f"### `{sig_str}`\n\n"
    markdown += f"{format_docstring(doc)}\n\n"

    if params_docs:
        markdown += "**Paramètres:**\n\n"
        markdown += '\n'.join(params_docs) + "\n\n"

    if return_doc:
        markdown += f"**Retour:**\n\n{return_doc}\n\n"

    return markdown


def inspect_class(cls):
    """
    Génère la documentation pour une classe.

    Args:
        cls: Classe à documenter

    Returns:
        str: Documentation au format Markdown
    """
    doc = inspect.getdoc(cls) or ""

    # Créer la documentation de la classe
    markdown = f"## Classe `{cls.__name__}`\n\n"
    markdown += f"{format_docstring(doc)}\n\n"

    # Documenter les méthodes
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    if methods:
        markdown += "### Méthodes\n\n"
        for name, method in methods:
            if not name.startswith('_') or name == '__init__':
                markdown += inspect_function(method) + "\n"

    return markdown


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
        # Assurez-vous que le répertoire courant est dans sys.path
        if '.' not in sys.path:
            sys.path.insert(0, '.')

        # Importer le module
        module = importlib.import_module(module_name)

        # Créer le contenu Markdown
        content = f"# Module {module_name}\n\n"

        # Docstring du module
        if module.__doc__:
            content += f"{format_docstring(module.__doc__)}\n\n"

        # Fonctions du module
        functions = inspect.getmembers(module, predicate=inspect.isfunction)
        if functions:
            content += "## Fonctions\n\n"
            for name, func in functions:
                if not name.startswith('_'):
                    content += inspect_function(func) + "\n"

        # Classes du module
        classes = inspect.getmembers(module, predicate=inspect.isclass)
        if classes:
            content += "## Classes\n\n"
            for name, cls in classes:
                if not name.startswith('_') and cls.__module__ == module_name:
                    content += inspect_class(cls) + "\n"

        # Écrire dans le fichier
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(
            f"Documentation générée pour le module '{module_name}' dans '{output_file}'"
        )
        return True
    except Exception as e:
        logger.error(
            f"Erreur lors de la génération de la documentation pour '{module_name}': {str(e)}"
        )
        return False


def generate_all_documentation():
    """
    Génère la documentation pour tous les modules Python du projet.
    """
    # Liste des modules à documenter
    modules = ["app", "syn_folders_to_container"]

    # Créer le répertoire de documentation
    create_docs_directory()

    # Générer la documentation pour chaque module
    success = True
    for module in modules:
        output_file = f"docs/module_{module}.md"
        if not generate_module_documentation(module, output_file):
            success = False

    # Préserver notre index.md existant s'il existe, ou en créer un nouveau simple
    index_path = Path("docs/index.md")
    if not index_path.exists():
        # Générer un index pour tous les modules
        with open(index_path, "w", encoding="utf-8") as index_file:
            index_file.write(
                "# Documentation de l'Application de Synchronisation de Dossiers\n\n"
            )
            index_file.write("## Modules disponibles\n\n")

            for module in modules:
                index_file.write(f"- [{module}](module_{module}.md)\n")

        logger.info("Index de documentation généré dans 'docs/index.md'")
    else:
        logger.info("Index de documentation existant préservé")

    return success


if __name__ == "__main__":
    logger.info("Démarrage de la génération de la documentation...")
    if generate_all_documentation():
        logger.info(
            "Documentation générée avec succès dans le répertoire 'docs/'")
    else:
        logger.error(
            "Des erreurs se sont produites lors de la génération de la documentation."
        )
