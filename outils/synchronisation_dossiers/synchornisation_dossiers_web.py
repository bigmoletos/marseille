"""
Version web de la synchronisation de dossiers utilisant Streamlit.
Permet de synchroniser deux dossiers de manière unidirectionnelle ou bidirectionnelle.
"""

import streamlit as st
import os
import shutil
import logging
from typing import Dict, List, Set, Callable, Optional, Union
import filecmp
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from tkinter import filedialog
import tkinter as tk
import threading
import fnmatch

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Synchronisation de dossiers",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Application de synchronisation de dossiers"})


# Configuration du logging avec un handler personnalisé pour Streamlit
class StreamlitLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        try:
            msg = self.format(record)
            self.logs.append({
                'level':
                record.levelname,
                'message':
                msg,
                'time':
                datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
            })
        except Exception:
            self.handleError(record)


# Configurer le logging
streamlit_handler = StreamlitLogHandler()
streamlit_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(level=logging.INFO,
                    handlers=[
                        streamlit_handler,
                        logging.StreamHandler(),
                        logging.FileHandler(os.path.join(
                            os.path.dirname(__file__), 'sync.log'),
                                            encoding='utf-8')
                    ])
logger = logging.getLogger(__name__)


def select_folder() -> Optional[str]:
    """Ouvre une fenêtre de sélection de dossier."""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale Tk
    folder = filedialog.askdirectory()
    root.destroy()
    if not folder:
        return None
    # S'assurer que le chemin est absolu et normalisé
    return str(Path(folder).resolve())


# Initialisation de l'état de session si nécessaire
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.comparison = None
    st.session_state.sync_done = False
    st.session_state.progress = 0
    st.session_state.status = ""
    st.session_state.dossier_a = ""
    st.session_state.dossier_b = ""
    st.session_state.mode = "A vers B (sauvegarde)"
    st.session_state.files_to_create = []
    st.session_state.files_to_update = []
    st.session_state.files_to_delete = []
    st.session_state.sync_results = None
    st.session_state.global_option = "Tout traiter"  # Option par défaut

# Réinitialiser les listes si la comparaison change
if 'comparison' in st.session_state and st.session_state.comparison is not None:
    if 'files_to_create' not in st.session_state:
        st.session_state.files_to_create = []
    if 'files_to_update' not in st.session_state:
        st.session_state.files_to_update = []
    if 'files_to_delete' not in st.session_state:
        st.session_state.files_to_delete = []

    # En mode A vers B, sélectionner tous les fichiers par défaut
    if st.session_state.mode == "A vers B (sauvegarde)":
        if 'to_create' in st.session_state.comparison:
            st.session_state.files_to_create = st.session_state.comparison[
                'to_create'].copy()
        if 'to_update' in st.session_state.comparison:
            st.session_state.files_to_update = st.session_state.comparison[
                'to_update'].copy()
        if 'to_delete' in st.session_state.comparison:
            st.session_state.files_to_delete = st.session_state.comparison[
                'to_delete'].copy()


@dataclass
class SyncStats:
    """Statistiques de synchronisation"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    files_created: int = 0
    files_updated: int = 0
    files_deleted: int = 0
    dirs_created: int = 0
    total_size: int = 0
    total_operations: int = 0
    current_operation: int = 0
    deleted_files: List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    updated_files: List[str] = field(default_factory=list)
    cancelled: bool = False

    def get_elapsed_time(self) -> float:
        """Retourne le temps écoulé en secondes"""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def estimate_remaining_time(self) -> float:
        """Estime le temps restant en secondes"""
        if self.current_operation == 0:
            return 0.0
        elapsed = self.get_elapsed_time()
        progress = self.current_operation / self.total_operations
        if progress == 0:
            return 0.0
        return (elapsed / progress) - elapsed

    def get_progress_percentage(self) -> float:
        """Retourne le pourcentage de progression"""
        if self.total_operations == 0:
            return 0.0
        return (self.current_operation / self.total_operations) * 100

    def format_size(self) -> str:
        """Formate la taille totale en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.total_size < 1024.0:
                return f"{self.total_size:.1f} {unit}"
            self.total_size /= 1024.0
        return f"{self.total_size:.1f} PB"


@dataclass
class SyncResults:
    """Résultats de la synchronisation"""
    before: Dict[str, List[str]]  # Résultats avant synchronisation
    after: Dict[str, List[str]] = field(
        default_factory=dict)  # Résultats après synchronisation
    stats: Optional[SyncStats] = None

    def display_comparison(self, container) -> None:
        """Affiche la comparaison des dossiers"""
        # Fichiers à créer
        if self.before.get('to_create'):
            expander = container.expander("📝 Fichiers à créer", expanded=True)
            expander.info(f"{len(self.before['to_create'])} fichiers à créer")
            for f in sorted(self.before['to_create']):
                expander.text(f"➕ {f}")

        # Fichiers à mettre à jour
        if self.before.get('to_update'):
            expander = container.expander("🔄 Fichiers à mettre à jour",
                                          expanded=True)
            expander.warning(
                f"{len(self.before['to_update'])} fichiers à mettre à jour")
            for f in sorted(self.before['to_update']):
                expander.text(f"🔄 {f}")

        # Fichiers à supprimer
        if self.before.get('to_delete'):
            expander = container.expander("🗑️ Fichiers à supprimer",
                                          expanded=True)
            expander.error(
                f"{len(self.before['to_delete'])} fichiers à supprimer")
            for f in sorted(self.before['to_delete']):
                expander.text(f"🗑️ {f}")

    def display_results(self, container) -> None:
        """Affiche les résultats de la synchronisation"""
        if not self.stats:
            return

        elapsed_time = format_time(self.stats.get_elapsed_time())
        total_size = self.stats.format_size()

        # En-tête avec les statistiques globales
        container.markdown(f"""
            <div style='background-color: rgba(45, 200, 66, 0.1); padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>✅ Synchronisation terminée</h3>
                <p><b>Durée :</b> {elapsed_time}</p>
                <p><b>Taille totale traitée :</b> {total_size}</p>
            </div>
        """,
                           unsafe_allow_html=True)

        # Détails des opérations dans des colonnes
        cols = container.columns(3)

        # Fichiers créés
        if self.stats.created_files:
            expander = cols[0].expander("📝 Fichiers créés", expanded=True)
            expander.success(f"{len(self.stats.created_files)} fichiers créés")
            for f in sorted(self.stats.created_files):
                expander.text(f"✅ {f}")

        # Fichiers mis à jour
        if self.stats.updated_files:
            expander = cols[1].expander("🔄 Fichiers mis à jour", expanded=True)
            expander.info(
                f"{len(self.stats.updated_files)} fichiers mis à jour")
            for f in sorted(self.stats.updated_files):
                expander.text(f"✅ {f}")

        # Fichiers supprimés
        if self.stats.deleted_files:
            expander = cols[2].expander("🗑️ Fichiers supprimés", expanded=True)
            expander.warning(
                f"{len(self.stats.deleted_files)} fichiers supprimés")
            for f in sorted(self.stats.deleted_files):
                expander.text(f"✅ {f}")


class DossierSync:
    """Classe principale pour la synchronisation des dossiers"""

    def __init__(self, dossier_a: Union[str, Path], dossier_b: Union[str,
                                                                     Path]):
        # Conversion en chemins absolus et normalisés
        self.dossier_a = Path(dossier_a).resolve()
        self.dossier_b = Path(dossier_b).resolve()
        logger.info(f"Initialisation avec dossier A: {self.dossier_a}")
        logger.info(f"Initialisation avec dossier B: {self.dossier_b}")
        self.ignored_patterns: Set[str] = self._load_ignore_patterns()
        self.stats = SyncStats()
        self.progress_callback: Optional[Callable] = None
        self.cancelled = False

    def _load_ignore_patterns(self) -> Set[str]:
        """Charge les patterns à ignorer."""
        try:
            # Utiliser un ensemble de patterns par défaut au lieu du fichier .fileignore
            return {
                '__pycache__', '.git', '.vscode', '.idea', '.pytest_cache',
                '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'
            }
        except Exception as e:
            logger.error(
                f"Erreur lors du chargement des patterns à ignorer: {e}")
            return set()

    def _should_ignore(self, path: Path) -> bool:
        """
        Détermine si un fichier ou dossier doit être ignoré.
        """
        try:
            # Vérifier chaque partie du chemin
            path_str = str(path)
            logger.debug(f"Vérification du chemin: {path_str}")

            # Vérifier les patterns à ignorer
            for pattern in self.ignored_patterns:
                if '*' in pattern:
                    if fnmatch.fnmatch(path_str, pattern):
                        logger.debug(
                            f"Fichier ignoré (pattern {pattern}): {path}")
                        return True
                elif pattern in path_str:
                    logger.debug(f"Fichier ignoré (pattern {pattern}): {path}")
                    return True

            logger.debug(f"Fichier accepté: {path}")
            return False

        except Exception as e:
            logger.error(
                f"Erreur lors de la vérification d'ignore pour {path}: {e}")
            return False

    def _scan_folder(self, folder: Path) -> Set[str]:
        """Scanne un dossier et retourne les fichiers non ignorés."""
        files = set()
        logger.info(f"=== SCAN {folder.absolute()} ===")
        try:
            for file_path in folder.rglob('*'):
                if file_path.is_file() and not self._should_ignore(file_path):
                    rel_path = str(file_path.relative_to(folder))
                    files.add(rel_path)
                    logger.debug(
                        f"Fichier trouvé dans {folder.name}: {rel_path}")
                else:
                    logger.debug(
                        f"Fichier ignoré dans {folder.name}: {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du scan du dossier {folder}: {e}")
            raise

        logger.info(f"Total fichiers dans {folder.absolute()}: {len(files)}")
        return files

    def compare_folders(self) -> Dict[str, List[str]]:
        """Compare les dossiers selon le mode sélectionné."""
        try:
            logger.info("=== DÉBUT COMPARAISON ===")
            mode = st.session_state.get('mode', 'Non défini')
            logger.info(f"Mode: {mode}")
            logger.info(f"Dossier source (A): {self.dossier_a.absolute()}")
            logger.info(
                f"Dossier destination (B): {self.dossier_b.absolute()}")

            files_a = self._scan_folder(self.dossier_a)
            files_b = self._scan_folder(self.dossier_b)

            # Calcul des différences selon le mode
            if mode == "A vers B (sauvegarde)":
                to_create = files_a - files_b  # Fichiers à copier de A vers B
                to_delete = files_b - files_a  # Fichiers à supprimer dans B
                to_create_reverse = []
                common = files_a & files_b

            elif mode == "B vers A (restauration)":
                to_create = files_b - files_a  # Fichiers à copier de B vers A
                to_delete = files_a - files_b  # Fichiers à supprimer dans A
                to_create_reverse = []
                common = files_a & files_b

            else:  # Mode bidirectionnel (miroir)
                to_create = files_a - files_b  # Fichiers à copier de A vers B
                to_create_reverse = files_b - files_a  # Fichiers à copier de B vers A
                to_delete = set()  # Pas de suppression en mode bidirectionnel
                common = files_a & files_b

            # Vérification des fichiers communs pour mise à jour
            to_update = []
            for file in sorted(common):
                try:
                    file_a = self.dossier_a / file
                    file_b = self.dossier_b / file

                    stats_a = file_a.stat()
                    stats_b = file_b.stat()

                    if stats_a.st_size != stats_b.st_size or stats_a.st_mtime != stats_b.st_mtime:
                        to_update.append(file)
                        continue

                except Exception as e:
                    logger.error(
                        f"Erreur lors de la comparaison de {file}: {e}")
                    continue

            result = {
                'to_create':
                sorted(list(to_create)),
                'to_update':
                sorted(to_update),
                'to_delete':
                sorted(list(to_delete)) if to_delete else [],
                'to_create_reverse':
                sorted(list(to_create_reverse)) if to_create_reverse else []
            }

            return result

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {e}")
            raise

    def safe_delete(self, path: Path) -> bool:
        """Suppression sécurisée d'un fichier ou dossier"""
        try:
            if not path.exists():
                return True

            # Si c'est un fichier
            if path.is_file():
                try:
                    # Essayer de retirer l'attribut en lecture seule
                    path.chmod(0o666)
                except:
                    pass
                try:
                    path.unlink()
                    return True
                except PermissionError:
                    logger.warning(
                        f"Permission refusée pour la suppression de: {path}")
                    return False
                except Exception as e:
                    logger.error(
                        f"Erreur lors de la suppression du fichier {path}: {e}"
                    )
                    return False

            # Si c'est un dossier
            elif path.is_dir():
                try:
                    # Supprimer d'abord le contenu du dossier
                    for item in path.glob('*'):
                        if item.is_file():
                            self.safe_delete(item)
                        elif item.is_dir():
                            self.safe_delete(item)

                    # Puis supprimer le dossier vide
                    path.rmdir()
                    return True
                except Exception as e:
                    logger.error(
                        f"Erreur lors de la suppression du dossier {path}: {e}"
                    )
                    return False

            return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {path}: {e}")
            return False

    def cancel_sync(self):
        """Annule la synchronisation en cours"""
        self.cancelled = True
        self.stats.cancelled = True
        logger.info("Annulation de la synchronisation demandée")

    def _update_progress(self, progress: float):
        """Met à jour la barre de progression."""
        if self.progress_callback:
            self.progress_callback(progress)

    def safe_copy(self, source: Path, dest: Path) -> bool:
        """Copie sécurisée d'un fichier avec gestion des erreurs"""
        try:
            # Vérifier si le fichier est en lecture seule
            if dest.exists():
                try:
                    dest.chmod(0o666)  # Donner les droits d'écriture
                except:
                    pass

            # Créer les dossiers parents si nécessaire
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copier le fichier
            shutil.copy2(source, dest)
            return True

        except PermissionError:
            logger.warning(f"Permission refusée pour: {dest}")
            return False
        except Exception as e:
            logger.error(
                f"Erreur lors de la copie de {source} vers {dest}: {e}")
            return False

    def synchronize(self) -> None:
        """Effectue la synchronisation selon le mode sélectionné."""
        try:
            mode = st.session_state.get('mode', 'Non défini')
            logger.info(f"Début de la synchronisation en mode: {mode}")

            files_to_create = st.session_state.files_to_create
            files_to_update = st.session_state.files_to_update
            files_to_delete = st.session_state.files_to_delete
            files_to_create_reverse = st.session_state.get('files_to_create_reverse', [])

            total_operations = (len(files_to_create) + len(files_to_update) +
                              len(files_to_delete) + len(files_to_create_reverse))

            if total_operations == 0:
                logger.info("Aucune opération à effectuer")
                return

            operations_done = 0

            try:
                if mode == "Bidirectionnel (miroir)":
                    # Première phase : A vers B
                    logger.info("=== Phase 1: Synchronisation A vers B ===")
                    for file in files_to_create:
                        source = self.dossier_a / file
                        dest = self.dossier_b / file
                        self.safe_copy(source, dest)
                        operations_done += 1
                        self._update_progress(operations_done / total_operations)
                        logger.info(f"Copié de A vers B: {file}")

                    # Deuxième phase : B vers A
                    logger.info("=== Phase 2: Synchronisation B vers A ===")
                    for file in files_to_create_reverse:
                        source = self.dossier_b / file
                        dest = self.dossier_a / file
                        self.safe_copy(source, dest)
                        operations_done += 1
                        self._update_progress(operations_done / total_operations)
                        logger.info(f"Copié de B vers A: {file}")

                else:  # Modes unidirectionnels
                    source = self.dossier_a if mode == "A vers B (sauvegarde)" else self.dossier_b
                    dest = self.dossier_b if mode == "A vers B (sauvegarde)" else self.dossier_a

                    # Copier les nouveaux fichiers
                    for file in files_to_create:
                        source_file = source / file
                        dest_file = dest / file
                        self.safe_copy(source_file, dest_file)
                        operations_done += 1
                        self._update_progress(operations_done / total_operations)
                        logger.info(f"Copié: {file}")

                    # Supprimer les fichiers
                    for file in files_to_delete:
                        file_to_delete = dest / file
                        self.safe_delete(file_to_delete)
                        operations_done += 1
                        self._update_progress(operations_done / total_operations)
                        logger.info(f"Supprimé: {file}")

                # Mise à jour des fichiers communs (pour tous les modes)
                logger.info("=== Mise à jour des fichiers ===")
                for file in files_to_update:
                    if mode == "Bidirectionnel (miroir)":
                        file_a = self.dossier_a / file
                        file_b = self.dossier_b / file
                        if file_a.stat().st_mtime > file_b.stat().st_mtime:
                            self.safe_copy(file_a, file_b)
                            logger.info(f"Mis à jour (A → B): {file}")
                        else:
                            self.safe_copy(file_b, file_a)
                            logger.info(f"Mis à jour (B → A): {file}")
                    else:
                        source_file = source / file
                        dest_file = dest / file
                        self.safe_copy(source_file, dest_file)
                        logger.info(f"Mis à jour: {file}")
                    operations_done += 1
                    self._update_progress(operations_done / total_operations)

                logger.info("Synchronisation terminée avec succès")
                st.session_state.sync_done = True

            except Exception as e:
                logger.error(f"Erreur pendant la synchronisation: {e}")
                raise

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {e}")
            raise

    def show_ui(self):
        """
        Affiche l'interface utilisateur
        """
        try:
            st.title("🔄 Synchronisation de dossiers")

            # Initialisation des variables de session
            if "confirm_state" not in st.session_state:
                st.session_state.confirm_state = "asking"
            if "files_to_create" not in st.session_state:
                st.session_state.files_to_create = []
            if "files_to_create_reverse" not in st.session_state:
                st.session_state.files_to_create_reverse = []
            if "files_to_update" not in st.session_state:
                st.session_state.files_to_update = []
            if "files_to_delete" not in st.session_state:
                st.session_state.files_to_delete = []
            if "comparison_results" not in st.session_state:
                st.session_state.comparison_results = None

            # Style CSS global
            st.markdown("""
                <style>
                    .stProgress > div > div > div > div {
                        height: 30px;
                    }
                    .stProgress {
                        margin-top: 20px;
                        margin-bottom: 20px;
                    }
                    .sync-status {
                        font-size: 1.2em;
                        padding: 10px;
                    }
                    .control-buttons {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        padding: 10px;
                        background-color: rgba(0, 0, 0, 0.1);
                        border-radius: 10px;
                        z-index: 1000;
                    }
                </style>
            """,
                        unsafe_allow_html=True)

            # Sélection des dossiers
            cols = st.columns(2)

            # Dossier source
            source_cols = cols[0].columns([3, 1])
            st.session_state.dossier_a = source_cols[0].text_input(
                "Dossier source (A)", value=st.session_state.dossier_a)
            if source_cols[1].button("📁", key="select_a"):
                folder = select_folder()
                if folder:
                    st.session_state.dossier_a = folder
                    st.rerun()

            # Dossier destination
            dest_cols = cols[1].columns([3, 1])
            st.session_state.dossier_b = dest_cols[0].text_input(
                "Dossier destination (B)", value=st.session_state.dossier_b)
            if dest_cols[1].button("📁", key="select_b"):
                folder = select_folder()
                if folder:
                    st.session_state.dossier_b = folder
                    st.rerun()

            # Mode de synchronisation
            st.session_state.mode = st.selectbox("Mode de synchronisation", [
                "A vers B (sauvegarde)", "B vers A (restauration)",
                "Bidirectionnel (miroir)"
            ])

            # Bouton Comparer
            if st.button("🔍 Comparer", type="primary", key="compare"):
                try:
                    # Effectuer la comparaison
                    st.session_state.comparison_results = self.compare_folders(
                    )
                    st.success("Comparaison effectuée")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la comparaison: {str(e)}")
                    logger.error(f"Erreur lors de la comparaison: {e}")
                    logger.exception("Détails de l'erreur:")

            # Affichage des résultats
            if st.session_state.comparison_results:
                st.write("## Résultats de la comparaison")

                with st.expander("⚙️ Options de synchronisation",
                                 expanded=True):
                    st.write("### 📊 Synthèse des modifications")

                    mode = st.session_state.get('mode', 'Non défini')
                    total_files = 0

                    if mode == "Bidirectionnel (miroir)":
                        # Affichage spécifique pour le mode bidirectionnel
                        st.write("#### Synchronisation A → B:")
                        files_a_to_b = len(
                            st.session_state.comparison_results['to_create'])
                        st.write(
                            f"📝 {files_a_to_b} fichiers à copier de A vers B")
                        if files_a_to_b > 0:
                            for f in sorted(st.session_state.
                                            comparison_results['to_create']):
                                st.text(f"  ➡️ {f}")

                        st.write("\n#### Synchronisation B → A:")
                        files_b_to_a = len(
                            st.session_state.
                            comparison_results['to_create_reverse'])
                        st.write(
                            f"📝 {files_b_to_a} fichiers à copier de B vers A")
                        if files_b_to_a > 0:
                            for f in sorted(
                                    st.session_state.
                                    comparison_results['to_create_reverse']):
                                st.text(f"  ⬅️ {f}")

                        if st.session_state.comparison_results['to_update']:
                            st.write("\n#### Fichiers à mettre à jour:")
                            update_files = len(st.session_state.
                                               comparison_results['to_update'])
                            st.write(
                                f"🔄 {update_files} fichiers à mettre à jour")
                            for f in sorted(st.session_state.
                                            comparison_results['to_update']):
                                st.text(f"  🔄 {f}")

                        total_files = files_a_to_b + files_b_to_a + len(
                            st.session_state.comparison_results['to_update'])

                    else:
                        # Mode unidirectionnel (A vers B ou B vers A)
                        direction = "A vers B" if mode == "A vers B (sauvegarde)" else "B vers A"
                        st.write(f"#### Synchronisation {direction}:")

                        # Fichiers à créer
                        create_files = len(
                            st.session_state.comparison_results['to_create'])
                        st.write(f"📝 {create_files} fichiers à créer")
                        if create_files > 0:
                            for f in sorted(st.session_state.
                                            comparison_results['to_create']):
                                st.text(f"  ➡️ {f}")

                        # Fichiers à mettre à jour
                        update_files = len(
                            st.session_state.comparison_results['to_update'])
                        st.write(
                            f"\n🔄 {update_files} fichiers à mettre à jour")
                        if update_files > 0:
                            for f in sorted(st.session_state.
                                            comparison_results['to_update']):
                                st.text(f"  🔄 {f}")

                        # Fichiers à supprimer
                        delete_files = len(
                            st.session_state.comparison_results['to_delete'])
                        st.write(f"\n🗑️ {delete_files} fichiers à supprimer")
                        if delete_files > 0:
                            for f in sorted(st.session_state.
                                            comparison_results['to_delete']):
                                st.text(f"  ❌ {f}")

                        total_files = create_files + update_files + delete_files

                    # Affichage du total
                    st.write(
                        f"\n**Total des modifications détectées : {total_files} fichiers**"
                    )

                    # Options globales
                    st.write("### 🎛️ Options globales")
                    global_option = st.radio("Action globale", [
                        "Tout traiter", "Ne rien traiter",
                        "Sélection par catégorie"
                    ],
                                             key="global_option")

                    if global_option == "Tout traiter":
                        st.session_state.files_to_create = st.session_state.comparison_results[
                            'to_create'].copy()
                        st.session_state.files_to_update = st.session_state.comparison_results[
                            'to_update'].copy()
                        if st.session_state.mode != "A vers B (sauvegarde)":
                            st.session_state.files_to_delete = st.session_state.comparison_results[
                                'to_delete'].copy()
                    elif global_option == "Ne rien traiter":
                        st.session_state.files_to_create = []
                        st.session_state.files_to_update = []
                        st.session_state.files_to_delete = []
                    else:
                        # Options par catégorie
                        st.write("### 🔍 Options détaillées par catégorie")

                        # Options pour les fichiers à créer
                        if st.session_state.comparison_results.get(
                                'to_create'):
                            st.write("#### Fichiers à créer")
                            create_cols = st.columns([2, 1, 1, 1])
                            create_cols[0].write(
                                f"**{len(st.session_state.comparison_results['to_create'])} fichiers**"
                            )
                            if create_cols[1].button("Tout créer",
                                                     key="create_all"):
                                st.session_state.files_to_create = st.session_state.comparison_results[
                                    'to_create'].copy()
                            if create_cols[2].button("Ne rien créer",
                                                     key="create_none"):
                                st.session_state.files_to_create = []

                            st.session_state.files_to_create = st.multiselect(
                                "Sélection manuelle des fichiers à créer",
                                st.session_state.
                                comparison_results['to_create'],
                                default=st.session_state.files_to_create)

                        # Options pour les fichiers à mettre à jour
                        if st.session_state.comparison_results.get(
                                'to_update'):
                            st.write("#### 🔄 Fichiers à mettre à jour")
                            update_cols = st.columns([2, 1, 1, 1])
                            update_cols[0].write(
                                f"**{len(st.session_state.comparison_results['to_update'])} fichiers**"
                            )
                            if update_cols[1].button("Tout mettre à jour",
                                                     key="update_all"):
                                st.session_state.files_to_update = st.session_state.comparison_results[
                                    'to_update'].copy()
                            if update_cols[2].button("Ne rien mettre à jour",
                                                     key="update_none"):
                                st.session_state.files_to_update = []

                            st.session_state.files_to_update = st.multiselect(
                                "Sélection manuelle des fichiers à mettre à jour",
                                st.session_state.
                                comparison_results['to_update'],
                                default=st.session_state.files_to_update)

                        # Options pour les fichiers à supprimer
                        if st.session_state.comparison_results.get(
                                'to_delete'):
                            st.write("#### 🗑️ Fichiers à supprimer")
                            st.error(
                                "⚠️ **ATTENTION : La suppression est une opération irréversible**"
                            )

                            # Afficher les fichiers à supprimer dans un tableau
                            files_to_delete = st.session_state.comparison_results[
                                'to_delete']
                            st.write(
                                f"**{len(files_to_delete)} fichiers seront supprimés :**"
                            )

                            # Créer une colonne pour chaque fichier avec son statut
                            for file in sorted(files_to_delete):
                                col1, col2, col3, col4 = st.columns(
                                    [3, 1, 1, 1])
                                col1.text(file)

                                # Boutons d'action pour chaque fichier
                                if col2.button("🗑️ Supprimer",
                                               key=f"delete_{file}"):
                                    confirm = st.warning(f"""
                                        ⚠️ **Confirmation de suppression**

                                        Voulez-vous vraiment supprimer le fichier : `{file}` ?

                                        Cette action est irréversible !
                                        """)
                                    col_conf1, col_conf2 = st.columns(2)
                                    if col_conf1.button("✅ Oui, supprimer",
                                                        key=f"confirm_{file}"):
                                        if file not in st.session_state.files_to_delete:
                                            st.session_state.files_to_delete.append(
                                                file)
                                        confirm.empty()
                                    if col_conf2.button("❌ Non, annuler",
                                                        key=f"cancel_{file}"):
                                        if file in st.session_state.files_to_delete:
                                            st.session_state.files_to_delete.remove(
                                                file)
                                        confirm.empty()

                                # Statut actuel du fichier
                                if file in st.session_state.files_to_delete:
                                    col3.markdown("🔴 À supprimer")
                                else:
                                    col3.markdown("🟢 À conserver")

                            # Options globales de suppression
                            st.write("---")
                            st.write("**Options globales de suppression :**")
                            col_all1, col_all2, col_all3 = st.columns(3)

                            if col_all1.button("🗑️ Tout supprimer"):
                                confirm_all = st.warning(f"""
                                    ⚠️ **Confirmation de suppression massive**

                                    Voulez-vous vraiment supprimer les {len(files_to_delete)} fichiers ?

                                    Cette action est irréversible !
                                    """)
                                col_conf_all1, col_conf_all2 = st.columns(2)
                                if col_conf_all1.button(
                                        "✅ Oui, tout supprimer"):
                                    st.session_state.files_to_delete = files_to_delete.copy(
                                    )
                                    confirm_all.empty()
                                if col_conf_all2.button("❌ Non, annuler"):
                                    confirm_all.empty()

                            if col_all2.button("✋ Ne rien supprimer"):
                                st.session_state.files_to_delete = []

                            if col_all3.button("↩️ Annuler les sélections"):
                                st.session_state.files_to_delete = []
                                st.rerun()

                            # Afficher un résumé des sélections
                            if st.session_state.files_to_delete:
                                st.warning(f"""
                                **Résumé des suppressions prévues :**
                                - {len(st.session_state.files_to_delete)} fichiers sélectionnés pour suppression
                                - {len(files_to_delete) - len(st.session_state.files_to_delete)} fichiers conservés
                                """)

                # Bouton de synchronisation
                if st.button("🚀 Lancer la synchronisation", type="primary", key="launch_sync"):
                    logger.debug("Bouton de synchronisation cliqué")

                    try:
                        with st.spinner("Synchronisation en cours..."):
                            logger.debug("Début de la synchronisation")
                            # Mettre à jour les listes de fichiers à traiter depuis comparison_results
                            st.session_state.files_to_create = st.session_state.comparison_results.get('to_create', [])
                            st.session_state.files_to_update = st.session_state.comparison_results.get('to_update', [])

                            if st.session_state.mode == "Bidirectionnel (miroir)":
                                st.session_state.files_to_create_reverse = st.session_state.comparison_results.get('to_create_reverse', [])
                                st.session_state.files_to_delete = []
                            else:
                                st.session_state.files_to_delete = st.session_state.comparison_results.get('to_delete', [])

                            # Lancer la synchronisation
                            self.synchronize()
                            logger.debug("Synchronisation terminée")

                        st.success("✅ Synchronisation terminée avec succès!")
                        # Mettre à jour la comparaison
                        st.session_state.comparison_results = self.compare_folders()
                        st.rerun()

                    except Exception as e:
                        logger.error(f"Erreur lors de la synchronisation: {e}", exc_info=True)
                        st.error(f"❌ Erreur lors de la synchronisation: {str(e)}")

            # Boutons de contrôle en bas
            st.markdown("<div class='control-buttons'>",
                        unsafe_allow_html=True)
            control_cols = st.columns([1, 1])

            if control_cols[0].button("🔄 Relancer", use_container_width=True):
                logger.info("Redémarrage de l'application")
                st.session_state.clear()
                st.rerun()

            if control_cols[1].button("❌ Annuler", use_container_width=True):
                logger.info("Annulation des modifications")
                st.session_state.comparison_results = None
                st.session_state.sync_done = False
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Espace en bas
            st.markdown("<div style='height: 100px;'></div>",
                        unsafe_allow_html=True)

        except Exception as e:
            logger.error(f"Erreur critique dans l'interface: {e}")
            st.error(str(e))


def format_time(seconds: float) -> str:
    """Formate un temps en secondes en format lisible"""
    if seconds < 60:
        return f"{seconds:.1f} secondes"
    minutes = int(seconds / 60)
    seconds = seconds % 60
    if minutes < 60:
        return f"{minutes} min {int(seconds)} sec"
    hours = int(minutes / 60)
    minutes = minutes % 60
    return f"{hours}h {minutes}min {int(seconds)}sec"


def main() -> None:
    """Point d'entrée principal de l'application."""
    try:
        # Créer une instance de DossierSync avec les chemins sélectionnés
        dossier_a = st.session_state.get('dossier_a', '')
        dossier_b = st.session_state.get('dossier_b', '')

        if dossier_a and dossier_b:
            logger.info(f"Dossier source sélectionné: {dossier_a}")
            logger.info(f"Dossier destination sélectionné: {dossier_b}")

            sync = DossierSync(dossier_a, dossier_b)
            results = sync.compare_folders()
            logger.info(f"Résultats de la comparaison: {results}")
        else:
            sync = DossierSync("", "")

        # Afficher l'interface
        sync.show_ui()

    except Exception as e:
        logger.error("Erreur critique dans l'application")
        logger.exception(e)
        st.error(f"Une erreur est survenue: {str(e)}")


if __name__ == "__main__":
    main()


def synchroniser_bidirectionnel(source: Path, destination: Path) -> None:
    """
    Synchronise les fichiers entre deux dossiers de manière bidirectionnelle.
    Ne supprime aucun fichier, effectue uniquement des copies et mises à jour.

    Args:
        source (Path): Chemin du premier dossier
        destination (Path): Chemin du second dossier

    Raises:
        ValueError: Si les chemins sont invalides
        PermissionError: Si les permissions sont insuffisantes
        OSError: Pour les autres erreurs système
    """
    try:
        logger.info(
            f"Début de la synchronisation bidirectionnelle entre {source} et {destination}"
        )

        # Vérification initiale des chemins
        if not verifier_chemins(source, destination):
            raise ValueError("Les chemins fournis sont invalides")

        # Synchronisation source -> destination
        _synchroniser_unidirectionnel(source, destination,
                                      "source -> destination")

        # Synchronisation destination -> source
        _synchroniser_unidirectionnel(destination, source,
                                      "destination -> source")

        logger.info("Synchronisation bidirectionnelle terminée avec succès")

    except Exception as e:
        logger.error(f"Erreur critique lors de la synchronisation: {str(e)}")
        raise


def _synchroniser_unidirectionnel(source: Path, destination: Path,
                                  direction: str) -> None:
    """
    Synchronise les fichiers dans une direction.
    Fonction interne utilisée par synchroniser_bidirectionnel.
    """
    logger.info(f"Démarrage synchronisation {direction}")

    for fichier_source in source.rglob('*'):
        if not fichier_source.is_file():
            continue

        try:
            chemin_relatif = fichier_source.relative_to(source)
            fichier_dest = destination / chemin_relatif

            if not fichier_dest.exists():
                _copier_fichier(fichier_source, fichier_dest, chemin_relatif,
                                direction)
            else:
                _mettre_a_jour_fichier(fichier_source, fichier_dest,
                                       chemin_relatif, direction)

        except Exception as e:
            logger.error(f"Erreur lors du traitement de {fichier_source}: {e}")
            raise


def _copier_fichier(source: Path, dest: Path, chemin_relatif: Path,
                    direction: str) -> None:
    """Copie un fichier avec gestion des erreurs."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        logger.info(f"Copié avec succès: {chemin_relatif} ({direction})")
    except PermissionError:
        logger.error(
            f"Permission refusée lors de la copie de {chemin_relatif}")
        raise
    except OSError as e:
        logger.error(
            f"Erreur système lors de la copie de {chemin_relatif}: {e}")
        raise


def _mettre_a_jour_fichier(source: Path, dest: Path, chemin_relatif: Path,
                           direction: str) -> None:
    """Met à jour un fichier si nécessaire."""
    try:
        if source.stat().st_mtime > dest.stat().st_mtime:
            shutil.copy2(source, dest)
            logger.info(
                f"Mis à jour avec succès: {chemin_relatif} ({direction})")
    except OSError as e:
        logger.error(f"Erreur lors de la mise à jour de {chemin_relatif}: {e}")
        raise


def verifier_chemins(source: Path, destination: Path) -> bool:
    """
    Vérifie la validité des chemins source et destination.

    Args:
        source (Path): Chemin du dossier source
        destination (Path): Chemin du dossier destination

    Returns:
        bool: True si les chemins sont valides, False sinon

    Raises:
        OSError: En cas d'erreur système lors de la vérification
    """
    logger.info(
        f"Vérification des chemins - Source: {source}, Destination: {destination}"
    )

    try:
        # Vérification de l'existence des dossiers
        if not source.exists():
            logger.error(f"Le dossier source n'existe pas: {source}")
            return False
        if not destination.exists():
            logger.error(f"Le dossier destination n'existe pas: {destination}")
            return False

        # Vérification que ce sont bien des dossiers
        if not source.is_dir():
            logger.error(f"Le chemin source n'est pas un dossier: {source}")
            return False
        if not destination.is_dir():
            logger.error(
                f"Le chemin destination n'est pas un dossier: {destination}")
            return False

        # Vérification que les chemins sont différents
        if source == destination:
            logger.error("Les dossiers source et destination sont identiques")
            return False

        # Vérification des permissions
        try:
            test_file = source / ".test_permission"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            logger.error(
                f"Permissions insuffisantes sur le dossier source: {source}")
            return False

        try:
            test_file = destination / ".test_permission"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            logger.error(
                f"Permissions insuffisantes sur le dossier destination: {destination}"
            )
            return False

        logger.info("Vérification des chemins réussie")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des chemins: {str(e)}")
        return False
