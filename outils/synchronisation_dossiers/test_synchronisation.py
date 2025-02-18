"""
Script de test pour la synchronisation de dossiers.
Tests exhaustifs de tous les modes et scénarios.
"""

import os
import shutil
from pathlib import Path
import logging
import tempfile
import time
from synchornisation_dossiers_web import DossierSync
import streamlit as st
import unittest
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TestSynchronisation(unittest.TestCase):
    """Tests de la synchronisation de dossiers."""

    def setUp(self):
        """Initialisation avant chaque test."""
        # Création des dossiers de test temporaires
        self.test_dir = Path(tempfile.mkdtemp())
        self.dir_a = self.test_dir / "dossier_a"
        self.dir_b = self.test_dir / "dossier_b"
        self.dir_a.mkdir()
        self.dir_b.mkdir()

        # Initialisation de la session Streamlit
        if 'dossier_a' not in st.session_state:
            st.session_state.dossier_a = str(self.dir_a)
        if 'dossier_b' not in st.session_state:
            st.session_state.dossier_b = str(self.dir_b)
        if 'mode' not in st.session_state:
            st.session_state.mode = "A vers B (sauvegarde)"

        # Création de l'instance de test
        self.sync = DossierSync()

    def tearDown(self):
        """Nettoyage après chaque test."""
        shutil.rmtree(self.test_dir)

    def create_test_files(self, directory: Path, files: dict):
        """Crée des fichiers de test."""
        for path, content in files.items():
            file_path = directory / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def test_compare_folders_a_to_b(self):
        """Test de la comparaison A vers B."""
        # Création des fichiers de test
        files_a = {
            'file1.txt': 'content1',
            'dir/file2.txt': 'content2',
            'file3.txt': 'content3'
        }
        files_b = {'file1.txt': 'different', 'other.txt': 'other'}

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        # Test de la comparaison
        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        # Vérifications
        self.assertIn('to_create', results)
        self.assertIn('to_update', results)
        self.assertEqual(set(results['to_create']),
                         {'dir/file2.txt', 'file3.txt'})
        self.assertEqual(set(results['to_update']), {'file1.txt'})

    def test_synchronize(self):
        """Test de la synchronisation."""
        # Création des fichiers de test
        files_a = {'test.txt': 'content'}
        self.create_test_files(self.dir_a, files_a)

        # Configuration de la session
        st.session_state.files_to_create = ['test.txt']
        st.session_state.files_to_update = []
        st.session_state.files_to_delete = []
        st.session_state.mode = "A vers B (sauvegarde)"

        # Test de la synchronisation
        self.sync.synchronize()

        # Vérification
        self.assertTrue((self.dir_b / 'test.txt').exists())
        self.assertEqual((self.dir_b / 'test.txt').read_text(), 'content')

    def test_error_handling(self):
        """Test de la gestion des erreurs."""
        # Test avec un dossier inexistant
        st.session_state.dossier_a = "/chemin/inexistant"
        with self.assertRaises(Exception):
            self.sync.compare_folders()

    def print_directory_contents(self, directory: Path, name: str):
        """Affiche le contenu d'un dossier"""
        files = sorted(os.listdir(directory))
        logger.info(f"Contenu du dossier {name}: {files}")
        return files

    def test_a_vers_b_cas1(self):
        """Test du mode A vers B - Cas 1: Fichiers à copier uniquement"""
        logger.info("\n=== Test mode A vers B - Cas 1 ===")

        files_a = {
            'sync_manifest.json': 'original',
            'sync_manifest - Copie.json': 'copie1',
            'sync_manifest - Copie (2).json': 'copie2'
        }
        files_b = {'sync_manifest.json': 'original'}

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        logger.info("État initial:")
        self.print_directory_contents(self.dir_a, "A")
        self.print_directory_contents(self.dir_b, "B")

        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        assert set(results['to_create']) == {'sync_manifest - Copie.json', 'sync_manifest - Copie (2).json'}, \
            "Les fichiers à créer ne sont pas corrects"
        assert not results['to_delete'], \
            "Il ne devrait pas y avoir de fichiers à supprimer"

    def test_a_vers_b_cas2(self):
        """Test du mode A vers B - Cas 2: Fichiers à mettre à jour"""
        logger.info("\n=== Test mode A vers B - Cas 2 ===")

        files_a = {
            'sync_manifest.json': 'contenu modifié',
            'sync_manifest - Copie.json': 'copie1'
        }
        files_b = {
            'sync_manifest.json': 'ancien contenu',
            'sync_manifest - Copie.json': 'ancien contenu'
        }

        self.create_test_files(self.dir_a, files_a)
        time.sleep(1)  # Assure une différence de timestamp
        self.create_test_files(self.dir_b, files_b)

        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert not results[
            'to_delete'], "Il ne devrait pas y avoir de fichiers à supprimer"
        assert set(results['to_update']) == {'sync_manifest.json', 'sync_manifest - Copie.json'}, \
            "Les fichiers à mettre à jour ne sont pas corrects"

    def test_b_vers_a_cas1(self):
        """Test du mode B vers A - Cas 1: Fichiers à supprimer uniquement"""
        logger.info("\n=== Test mode B vers A - Cas 1 ===")

        files_a = {
            'sync_manifest.json': 'original',
            'sync_manifest - Copie.json': 'copie1',
            'sync_manifest - Copie (2).json': 'copie2'
        }
        files_b = {'sync_manifest.json': 'original'}

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        st.session_state.mode = "B vers A (restauration)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert set(results['to_delete']) == {'sync_manifest - Copie.json', 'sync_manifest - Copie (2).json'}, \
            "Les fichiers à supprimer ne sont pas corrects"

    def test_b_vers_a_cas2(self):
        """Test du mode B vers A - Cas 2: Fichiers à mettre à jour"""
        logger.info("\n=== Test mode B vers A - Cas 2 ===")

        files_a = {
            'sync_manifest.json': 'ancien contenu',
            'extra.json': 'à supprimer'
        }
        files_b = {'sync_manifest.json': 'nouveau contenu'}

        self.create_test_files(self.dir_a, files_a)
        time.sleep(1)
        self.create_test_files(self.dir_b, files_b)

        st.session_state.mode = "B vers A (restauration)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert set(results['to_delete']) == {'extra.json'}, \
            "Les fichiers à supprimer ne sont pas corrects"
        assert set(results['to_update']) == {'sync_manifest.json'}, \
            "Les fichiers à mettre à jour ne sont pas corrects"

    def test_b_vers_a_cas3(self):
        """Test du mode B vers A - Cas 3: Vérification spécifique des suppressions"""
        logger.info("\n=== Test mode B vers A - Cas 3 ===")

        # Cas spécifique avec les fichiers sync_manifest
        files_a = {
            'sync_manifest.json': 'original',
            'sync_manifest - Copie.json': 'copie1',
            'sync_manifest - Copie (2).json': 'copie2',
            'autre_fichier.txt': 'contenu'
        }
        files_b = {
            'sync_manifest.json': 'original',
            'autre_fichier.txt': 'contenu'
        }

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        logger.info("État initial:")
        self.print_directory_contents(self.dir_a, "A")
        self.print_directory_contents(self.dir_b, "B")

        st.session_state.mode = "B vers A (restauration)"
        results = self.sync.compare_folders()

        logger.info(f"Résultats complets: {results}")

        # Vérifications spécifiques
        assert not results['to_create'], \
            "Il ne devrait pas y avoir de fichiers à créer en mode B vers A"
        assert set(results['to_delete']) == {'sync_manifest - Copie.json', 'sync_manifest - Copie (2).json'}, \
            f"Les fichiers à supprimer sont incorrects. Attendu: {{'sync_manifest - Copie.json', 'sync_manifest - Copie (2).json'}}, Obtenu: {results['to_delete']}"
        assert not results['to_update'], \
            "Il ne devrait pas y avoir de fichiers à mettre à jour"

    def test_b_vers_a_cas4(self):
        """Test du mode B vers A - Cas 4: Vérification avec sous-dossiers"""
        logger.info("\n=== Test mode B vers A - Cas 4 ===")

        # Création de sous-dossiers
        subdir_a = self.dir_a / "subdir"
        subdir_b = self.dir_b / "subdir"
        subdir_a.mkdir()
        subdir_b.mkdir()

        files_a = {
            'sync_manifest.json': 'original',
            'subdir/sync_manifest - Copie.json': 'copie1',
            'subdir/sync_manifest - Copie (2).json': 'copie2'
        }
        files_b = {
            'sync_manifest.json': 'original',
            'subdir/autre.txt': 'contenu'
        }

        # Création des fichiers
        for path, content in files_a.items():
            file_path = self.dir_a / path
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(content)

        for path, content in files_b.items():
            file_path = self.dir_b / path
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(content)

        logger.info("État initial:")
        self.print_directory_contents(self.dir_a, "A")
        self.print_directory_contents(subdir_a, "A/subdir")
        self.print_directory_contents(self.dir_b, "B")
        self.print_directory_contents(subdir_b, "B/subdir")

        st.session_state.mode = "B vers A (restauration)"
        results = self.sync.compare_folders()

        logger.info(f"Résultats complets: {results}")

        # Vérifications
        expected_to_delete = {
            'subdir/sync_manifest - Copie.json',
            'subdir/sync_manifest - Copie (2).json'
        }
        assert not results['to_create'], \
            "Il ne devrait pas y avoir de fichiers à créer"
        assert set(results['to_delete']) == expected_to_delete, \
            f"Les fichiers à supprimer sont incorrects. Attendu: {expected_to_delete}, Obtenu: {set(results['to_delete'])}"

    def test_scan_folder(self):
        """Test spécifique de la méthode _scan_folder"""
        logger.info("\n=== Test de _scan_folder ===")

        # Création d'une structure de test
        files = {
            'sync_manifest.json': 'original',
            'sync_manifest - Copie.json': 'copie1',
            'sync_manifest - Copie (2).json': 'copie2',
            'subdir/test.txt': 'test',
            'subdir/deep/file.txt': 'deep'
        }

        # Création des fichiers
        for path, content in files.items():
            file_path = self.dir_a / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        # Test du scan
        results = self.sync._scan_folder(self.dir_a)

        # Conversion des chemins en relatif pour la comparaison
        expected_files = set(files.keys())
        results = set(results)

        logger.info(f"Fichiers attendus: {sorted(expected_files)}")
        logger.info(f"Fichiers scannés: {sorted(results)}")

        assert results == expected_files, \
            f"Le scan n'a pas retourné les bons fichiers.\nAttendu: {expected_files}\nObtenu: {results}"

    def test_a_vers_b_cas3(self):
        """Test du mode A vers B - Cas 3: Fichiers avec espaces et caractères spéciaux"""
        logger.info("\n=== Test mode A vers B - Cas 3 ===")

        files_a = {
            'fichier avec espaces.txt': 'contenu',
            'fichier_avec_accents_éèà.txt': 'contenu',
            'fichier (avec) [parenthèses].txt': 'contenu'
        }
        files_b = {}

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        logger.info("État initial:")
        self.print_directory_contents(self.dir_a, "A")
        self.print_directory_contents(self.dir_b, "B")

        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        assert set(results['to_create']) == set(files_a.keys()), \
            "Les fichiers avec caractères spéciaux ne sont pas correctement détectés"

    def test_a_vers_b_cas4(self):
        """Test du mode A vers B - Cas 4: Structure complexe de sous-dossiers"""
        logger.info("\n=== Test mode A vers B - Cas 4 ===")

        files_a = {
            'dossier1/fichier1.txt': 'contenu1',
            'dossier1/sous-dossier/fichier2.txt': 'contenu2',
            'dossier2/fichier3.txt': 'contenu3',
            'dossier1/sous-dossier/sous-sous-dossier/fichier4.txt': 'contenu4'
        }
        files_b = {
            'dossier1/fichier1.txt': 'ancien contenu',
            'dossier2/fichier_different.txt': 'autre contenu'
        }

        # Création des fichiers avec leurs dossiers parents
        for path, content in files_a.items():
            file_path = self.dir_a / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        for path, content in files_b.items():
            file_path = self.dir_b / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        expected_to_create = {
            'dossier1/sous-dossier/fichier2.txt',
            'dossier1/sous-dossier/sous-sous-dossier/fichier4.txt'
        }
        expected_to_update = {'dossier1/fichier1.txt'}

        assert set(results['to_create']) == expected_to_create, \
            "Les fichiers à créer dans les sous-dossiers ne sont pas correctement détectés"
        assert set(results['to_update']) == expected_to_update, \
            "Les fichiers à mettre à jour ne sont pas correctement détectés"

    def test_b_vers_a_cas5(self):
        """Test du mode B vers A - Cas 5: Dossiers vides"""
        logger.info("\n=== Test mode B vers A - Cas 5 ===")

        # Création de dossiers vides dans A
        (self.dir_a / "dossier_vide1").mkdir()
        (self.dir_a / "dossier_vide2" /
         "sous_dossier_vide").mkdir(parents=True)

        files_a = {'dossier1/fichier1.txt': 'contenu1'}
        files_b = {'dossier1/fichier1.txt': 'contenu1'}

        for path, content in files_a.items():
            file_path = self.dir_a / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        for path, content in files_b.items():
            file_path = self.dir_b / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        st.session_state.mode = "B vers A (restauration)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert not results[
            'to_update'], "Il ne devrait pas y avoir de fichiers à mettre à jour"
        assert not results[
            'to_delete'], "Les dossiers vides ne devraient pas être considérés pour la suppression"

    def test_bidirectionnel_cas3(self):
        """Test du mode bidirectionnel - Cas 3: Fichiers identiques avec timestamps différents"""
        logger.info("\n=== Test mode bidirectionnel - Cas 3 ===")

        files_a = {'fichier.txt': 'même contenu'}
        files_b = {'fichier.txt': 'même contenu'}

        # Créer d'abord dans A
        self.create_test_files(self.dir_a, files_a)
        time.sleep(2)  # Attendre pour avoir une différence de timestamp
        # Puis dans B
        self.create_test_files(self.dir_b, files_b)

        st.session_state.mode = "Bidirectionnel (miroir)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert not results[
            'to_create_reverse'], "Il ne devrait pas y avoir de fichiers à créer en reverse"
        assert not results[
            'to_update'], "Les fichiers avec le même contenu ne devraient pas être mis à jour malgré des timestamps différents"

    def test_bidirectionnel_cas4(self):
        """Test du mode bidirectionnel - Cas 4: Conflit de modifications"""
        logger.info("\n=== Test mode bidirectionnel - Cas 4 ===")

        # Créer le même fichier avec des contenus différents dans A et B
        files_a = {'conflit.txt': 'version A'}
        files_b = {'conflit.txt': 'version B'}

        self.create_test_files(self.dir_a, files_a)
        self.create_test_files(self.dir_b, files_b)

        st.session_state.mode = "Bidirectionnel (miroir)"
        results = self.sync.compare_folders()

        assert not results[
            'to_create'], "Il ne devrait pas y avoir de fichiers à créer"
        assert not results[
            'to_create_reverse'], "Il ne devrait pas y avoir de fichiers à créer en reverse"
        assert set(results['to_update']) == {'conflit.txt'}, \
            "Le fichier en conflit devrait être détecté pour mise à jour"

    def setup_test_structure(self):
        """Crée une structure de test complète et réaliste"""
        logger.info("\n=== Création de la structure de test ===")

        # Création des dossiers racine de test
        test_dir = Path("test_folders")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir()

        # Création des dossiers A et B
        dir_a = test_dir / "dossier_a"
        dir_b = test_dir / "dossier_b"
        dir_a.mkdir()
        dir_b.mkdir()

        # Structure pour le dossier A
        structure_a = {
            # Fichiers à la racine
            'fichier1.txt': 'Contenu fichier 1',
            'fichier2.txt': 'Contenu fichier 2',
            'sync_manifest.json': 'Original',
            'sync_manifest - Copie.json': 'Copie 1',
            'sync_manifest - Copie (2).json': 'Copie 2',

            # Sous-dossiers avec fichiers
            'Documents/doc1.txt': 'Document 1',
            'Documents/Projet/spec.txt': 'Spécifications',
            'Documents/Projet/données/data.csv': 'Données',
            'Documents/Archives/old.txt': 'Archive',

            # Dossiers avec caractères spéciaux
            'Été 2023/photo.jpg': 'Photo été',
            'Année (2023)/résumé.txt': 'Résumé',
            'Dossier test/fichier test.txt': 'Test'
        }

        # Structure pour le dossier B
        structure_b = {
            # Fichiers communs (certains modifiés)
            'fichier1.txt': 'Contenu modifié',
            'sync_manifest.json': 'Original',

            # Fichiers uniques à B
            'unique_b.txt': 'Unique à B',
            'autre.txt': 'Autre fichier',

            # Sous-dossiers avec fichiers
            'Documents/doc1.txt': 'Document 1 modifié',
            'Documents/Projet/nouveau.txt': 'Nouveau fichier',
            'Backups/backup.zip': 'Backup'
        }

        # Création des fichiers dans A
        logger.info("Création des fichiers dans le dossier A:")
        for path, content in structure_a.items():
            file_path = dir_a / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"  Créé: {path}")

        # Création des fichiers dans B
        logger.info("Création des fichiers dans le dossier B:")
        for path, content in structure_b.items():
            file_path = dir_b / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"  Créé: {path}")

        # Création de dossiers vides
        (dir_a / "Dossier_Vide").mkdir(exist_ok=True)
        (dir_a / "Documents/Vide").mkdir(parents=True, exist_ok=True)
        (dir_b / "Vide").mkdir(exist_ok=True)

        return dir_a, dir_b, structure_a, structure_b

    def test_real_sync(self):
        """Test complet avec une structure réelle"""
        logger.info("\n=== Test de synchronisation réelle ===")

        # Création de la structure de test
        dir_a, dir_b, structure_a, structure_b = self.setup_test_structure()

        # Test du mode A vers B
        logger.info("\n--- Test mode A vers B ---")
        st.session_state.mode = "A vers B (sauvegarde)"
        results = self.sync.compare_folders()

        # Vérifications détaillées
        logger.info("\nContenu des dossiers:")
        logger.info(f"Dossier A: {sorted(os.listdir(dir_a))}")
        logger.info(f"Dossier B: {sorted(os.listdir(dir_b))}")

        logger.info("\nRésultats de la comparaison:")
        logger.info(f"Fichiers à créer: {results['to_create']}")
        logger.info(f"Fichiers à mettre à jour: {results['to_update']}")
        logger.info(f"Fichiers à supprimer: {results['to_delete']}")

        # Vérifications A vers B
        expected_to_create = set(structure_a.keys()) - set(structure_b.keys())
        expected_to_update = {'fichier1.txt', 'Documents/doc1.txt'}

        assert set(results['to_create']) == expected_to_create, \
            f"Les fichiers à créer ne correspondent pas.\nAttendu: {sorted(expected_to_create)}\nObtenu: {sorted(results['to_create'])}"
        assert set(results['to_update']) == expected_to_update, \
            f"Les fichiers à mettre à jour ne correspondent pas.\nAttendu: {sorted(expected_to_update)}\nObtenu: {sorted(results['to_update'])}"


def main():
    """Exécute tous les tests"""
    test = TestSynchronisation()
    try:
        test.test_a_vers_b_cas1()
        test.test_a_vers_b_cas2()
        test.test_b_vers_a_cas1()
        test.test_b_vers_a_cas2()
        test.test_b_vers_a_cas3()
        test.test_b_vers_a_cas4()
        test.test_b_vers_a_cas5()
        test.test_bidirectionnel_cas3()
        test.test_bidirectionnel_cas4()
        test.test_scan_folder()
        test.test_real_sync()
        logger.info("\n✅ Tous les tests ont réussi!")
    except AssertionError as e:
        logger.error(f"\n❌ Échec des tests: {e}")
    finally:
        test.tearDown()


if __name__ == "__main__":
    main()
