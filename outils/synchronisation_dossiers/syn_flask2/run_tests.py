#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour exécuter tous les tests unitaires du projet.

Ce script découvre automatiquement et exécute tous les tests unitaires
présents dans le répertoire 'tests' du projet.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("run_tests")


def run_all_tests():
    """
    Découvre et exécute tous les tests unitaires du projet.

    Returns:
        bool: True si tous les tests ont réussi, False sinon
    """
    # Créer le répertoire de tests s'il n'existe pas
    Path("tests").mkdir(exist_ok=True)

    # Créer un fichier __init__.py dans le répertoire tests s'il n'existe pas
    init_file = Path("tests/__init__.py")
    if not init_file.exists():
        init_file.touch()
        logger.info("Fichier tests/__init__.py créé.")

    # Découvrir les tests
    logger.info("Recherche des tests unitaires...")

    # Ajouter le répertoire courant au chemin de recherche des modules
    sys.path.insert(0, os.path.abspath('.'))

    # Découvrir et exécuter les tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    # Exécuter les tests avec sortie détaillée
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Afficher un résumé
    logger.info(f"Tests exécutés: {result.testsRun}")
    if result.wasSuccessful():
        logger.info("Tous les tests ont réussi!")
        return True
    else:
        logger.error(
            f"Échecs: {len(result.failures)}, Erreurs: {len(result.errors)}")
        return False


def create_sample_test():
    """
    Crée un exemple de test unitaire si aucun test n'existe.
    """
    test_file = Path("tests/test_sample.py")

    if not list(Path("tests").glob("test_*.py")):
        logger.info(
            "Aucun fichier de test trouvé. Création d'un exemple de test...")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Module contenant des tests unitaires d'exemple.
\"\"\"

import unittest
import os
import sys

# Ajouter le répertoire parent au chemin de recherche
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestSample(unittest.TestCase):
    \"\"\"Classe de test d'exemple.\"\"\"

    def setUp(self):
        \"\"\"Prépare l'environnement de test.\"\"\"
        pass

    def tearDown(self):
        \"\"\"Nettoie l'environnement après le test.\"\"\"
        pass

    def test_sample(self):
        \"\"\"Test de démonstration qui réussit toujours.\"\"\"
        self.assertTrue(True)

    def test_import_modules(self):
        \"\"\"Vérifie que les modules principaux peuvent être importés.\"\"\"
        try:
            import app
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Impossible d'importer le module app: {e}")

        try:
            import syn_folders_to_container
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Impossible d'importer le module syn_folders_to_container: {e}")

if __name__ == '__main__':
    unittest.main()
""")
        logger.info(f"Exemple de test créé: {test_file}")


if __name__ == "__main__":
    logger.info("Démarrage de l'exécution des tests unitaires...")
    create_sample_test()

    if run_all_tests():
        sys.exit(0)
    else:
        logger.error("Certains tests ont échoué.")
        sys.exit(1)
