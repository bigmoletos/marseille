#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script combiné pour exécuter les tests unitaires et générer la documentation.

Ce script appelle les deux autres scripts pour simplifier le processus
de développement et de maintenance de l'application.
"""

import os
import sys
import logging
import importlib.util
import subprocess
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("build_script")


def check_script_exists(script_name):
    """
    Vérifie si un script existe dans le répertoire courant.

    Args:
        script_name (str): Nom du script à vérifier

    Returns:
        bool: True si le script existe, False sinon
    """
    script_path = Path(script_name)
    return script_path.exists()


def run_script(script_name):
    """
    Exécute un script Python.

    Args:
        script_name (str): Nom du script à exécuter

    Returns:
        bool: True si l'exécution a réussi, False sinon
    """
    logger.info(f"Exécution de {script_name}...")

    try:
        # Méthode 1: Importation et exécution du module
        try:
            # Préparation du chemin du script
            script_path = Path(script_name)
            module_name = script_path.stem

            # Chargement dynamique du module
            spec = importlib.util.spec_from_file_location(
                module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            logger.info(
                f"{script_name} a été exécuté avec succès (via import)")
            return True
        except Exception as e:
            logger.warning(
                f"Erreur lors de l'importation du module {script_name}: {str(e)}"
            )
            logger.warning("Tentative d'exécution via subprocess...")

            # Méthode 2: Exécution en tant que processus externe
            process = subprocess.run([sys.executable, script_name],
                                     capture_output=True,
                                     text=True)

            if process.returncode == 0:
                logger.info(
                    f"{script_name} a été exécuté avec succès (via subprocess)"
                )
                if process.stdout:
                    for line in process.stdout.splitlines():
                        logger.info(f"[{script_name}] {line}")
                return True
            else:
                logger.error(f"Erreur lors de l'exécution de {script_name}:")
                if process.stderr:
                    for line in process.stderr.splitlines():
                        logger.error(f"[{script_name}] {line}")
                return False

    except Exception as e:
        logger.error(
            f"Erreur inattendue lors de l'exécution de {script_name}: {str(e)}"
        )
        return False


def main():
    """
    Fonction principale qui exécute les scripts de tests et de documentation.
    """
    # Vérifier si nous sommes dans le bon répertoire
    if not (check_script_exists("run_tests.py")
            and check_script_exists("generate_docs.py")):
        logger.error(
            "Les scripts 'run_tests.py' et 'generate_docs.py' doivent être présents dans le répertoire courant."
        )
        return False

    # Exécuter les tests unitaires
    tests_success = run_script("run_tests.py")
    if not tests_success:
        logger.warning(
            "Des problèmes ont été rencontrés lors de l'exécution des tests.")

    # Générer la documentation
    docs_success = run_script("generate_docs.py")
    if not docs_success:
        logger.warning(
            "Des problèmes ont été rencontrés lors de la génération de la documentation."
        )

    # Bilan final
    if tests_success and docs_success:
        logger.info("✅ Tous les scripts ont été exécutés avec succès!")
        return True
    else:
        status = []
        if tests_success:
            status.append("✅ Tests: réussis")
        else:
            status.append("❌ Tests: échec")

        if docs_success:
            status.append("✅ Documentation: réussie")
        else:
            status.append("❌ Documentation: échec")

        logger.warning(f"Bilan: {' | '.join(status)}")
        return False


if __name__ == "__main__":
    logger.info("=== Démarrage du processus de build ===")
    success = main()
    logger.info("=== Fin du processus de build ===")
    sys.exit(0 if success else 1)
