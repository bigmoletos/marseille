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
    """Ouvre une fenêtre de sélection de dossier"""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale Tk
    root.wm_attributes('-topmost', 1)  # Met la fenêtre au premier plan
    folder = filedialog.askdirectory()
    root.destroy()
    return folder if folder else None


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
        self.dossier_a = Path(dossier_a)
        self.dossier_b = Path(dossier_b)
        self.ignored_patterns: Set[str] = self._load_ignore_patterns()
        self.stats = SyncStats()
        self.progress_callback: Optional[Callable] = None
        self.cancelled = False

    def _load_ignore_patterns(self) -> Set[str]:
        """Charge les patterns à ignorer depuis .fileignore"""
        try:
            ignore_file = Path(__file__).parent / '.fileignore'
            if not ignore_file.exists():
                return set()
            with open(ignore_file, 'r', encoding='utf-8') as f:
                return {
                    line.strip()
                    for line in f if line.strip() and not line.startswith('#')
                }
        except Exception as e:
            logger.error(
                f"Erreur lors du chargement des patterns à ignorer: {e}")
            return set()

    def _should_ignore(self, path: Path) -> bool:
        """Vérifie si un chemin doit être ignoré"""
        # Vérifier le nom du fichier et tous les dossiers parents
        parts = path.parts
        for part in parts:
            if any(pattern in part for pattern in self.ignored_patterns):
                return True
            # Ignorer explicitement les dossiers .git
            if '.git' in part:
                return True
        return False

    def _get_relative_files(self, base_path: Path) -> Set[str]:
        """Obtient la liste des fichiers et dossiers relatifs"""
        logger.info(f"Lecture des fichiers du dossier: {base_path}")
        items = set()
        try:
            for root, dirs, filenames in os.walk(base_path):
                logger.debug(f"Analyse du dossier: {root}")
                # Chemin relatif du dossier courant
                rel_root = os.path.relpath(root, base_path)
                logger.debug(f"Chemin relatif: {rel_root}")

                # Ajouter les dossiers
                for dir_name in dirs:
                    if not self._should_ignore(Path(dir_name)):
                        dir_path = os.path.join(rel_root, dir_name)
                        if rel_root == ".":
                            dir_path = dir_name
                        items.add(dir_path + "/")
                        logger.debug(f"Dossier ajouté: {dir_path}/")
                    else:
                        logger.debug(f"Dossier ignoré: {dir_name}")

                # Ajouter les fichiers
                for filename in filenames:
                    file_path = Path(os.path.join(rel_root, filename))
                    if not self._should_ignore(file_path):
                        rel_path = str(file_path).replace("\\", "/")
                        if rel_root == ".":
                            rel_path = filename
                        items.add(rel_path)
                        logger.debug(f"Fichier ajouté: {rel_path}")
                    else:
                        logger.debug(f"Fichier ignoré: {filename}")

            logger.info(
                f"Total éléments trouvés dans {base_path}: {len(items)}")
            return items

        except Exception as e:
            logger.error(
                f"Erreur lors de la lecture des fichiers dans {base_path}: {e}"
            )
            logger.exception("Détails de l'erreur:")
            raise

    def compare_folders(self) -> Dict[str, List[str]]:
        """Compare les dossiers selon le mode sélectionné."""
        try:
            logger.info("=== DÉBUT COMPARAISON ===")

            # Vérification des dossiers
            if not self.dossier_a or not self.dossier_b:
                logger.error(
                    f"Dossiers non spécifiés - A: {self.dossier_a}, B: {self.dossier_b}"
                )
                raise ValueError(
                    "Les dossiers source et destination doivent être spécifiés"
                )

            dossier_a = Path(self.dossier_a)
            dossier_b = Path(self.dossier_b)

            if not dossier_a.exists() or not dossier_b.exists():
                logger.error(
                    f"Dossiers inexistants - A: {dossier_a}, B: {dossier_b}")
                raise ValueError(
                    "Les dossiers source et destination doivent exister")

            logger.info(f"Mode de synchronisation: {st.session_state.mode}")
            logger.info(f"Dossier A: {dossier_a}")
            logger.info(f"Dossier B: {dossier_b}")

            # Récupération des fichiers (avec chemins relatifs)
            files_a = set()
            files_b = set()

            # Parcours dossier A
            for file_path in dossier_a.rglob('*'):
                if file_path.is_file() and not self._should_ignore(file_path):
                    try:
                        rel_path = str(
                            file_path.relative_to(dossier_a)).replace(
                                '\\', '/')
                        files_a.add(rel_path)
                        logger.debug(f"Fichier trouvé dans A: {rel_path}")
                    except Exception as e:
                        logger.error(
                            f"Erreur lors du traitement du fichier {file_path}: {e}"
                        )

            # Parcours dossier B
            for file_path in dossier_b.rglob('*'):
                if file_path.is_file() and not self._should_ignore(file_path):
                    try:
                        rel_path = str(
                            file_path.relative_to(dossier_b)).replace(
                                '\\', '/')
                        files_b.add(rel_path)
                        logger.debug(f"Fichier trouvé dans B: {rel_path}")
                    except Exception as e:
                        logger.error(
                            f"Erreur lors du traitement du fichier {file_path}: {e}"
                        )

            logger.info(
                f"Fichiers trouvés - A: {len(files_a)}, B: {len(files_b)}")

            # Inversion des ensembles si mode restauration
            if st.session_state.mode == "B vers A (restauration)":
                logger.info(
                    "Mode restauration: inversion des ensembles A et B")
                files_a, files_b = files_b, files_a

            # Calcul des différences
            to_create = files_a - files_b
            to_delete = files_b - files_a
            common = files_a & files_b

            logger.info(f"Fichiers à créer: {len(to_create)}")
            logger.info(f"Fichiers à supprimer: {len(to_delete)}")
            logger.info(f"Fichiers communs: {len(common)}")

            # Vérification des fichiers communs
            to_update = []
            for file in sorted(common):
                try:
                    file_a = dossier_a / file
                    file_b = dossier_b / file

                    # Comparaison des tailles
                    size_a = file_a.stat().st_size
                    size_b = file_b.stat().st_size

                    if size_a != size_b:
                        logger.debug(
                            f"Tailles différentes pour {file} - A: {size_a}, B: {size_b}"
                        )
                        to_update.append(file)
                        continue

                    # Comparaison du contenu si tailles identiques
                    if not filecmp.cmp(str(file_a), str(file_b),
                                       shallow=False):
                        logger.debug(f"Contenus différents pour {file}")
                        to_update.append(file)

                except Exception as e:
                    logger.error(
                        f"Erreur lors de la comparaison de {file}: {e}")
                    continue

            # Préparation du résultat
            result = {
                'to_create':
                sorted(list(to_create)),
                'to_update':
                sorted(to_update),
                'to_delete':
                sorted(list(to_delete))
                if st.session_state.mode != "Bidirectionnel (miroir)" else [],
                'to_create_reverse':
                sorted(list(to_delete))
                if st.session_state.mode == "Bidirectionnel (miroir)" else []
            }

            # Log des résultats
            logger.info("=== RÉSULTATS DE LA COMPARAISON ===")
            logger.info(f"Fichiers à créer: {len(result['to_create'])}")
            logger.info(
                f"Fichiers à mettre à jour: {len(result['to_update'])}")
            logger.info(f"Fichiers à supprimer: {len(result['to_delete'])}")
            if result['to_create_reverse']:
                logger.info(
                    f"Fichiers à créer en sens inverse: {len(result['to_create_reverse'])}"
                )

            return result

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {e}")
            logger.exception("Détails de l'erreur:")
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

    def _update_progress(self):
        """Met à jour la progression et les estimations"""
        if self.progress_callback:
            self.progress_callback({
                'progress':
                self.stats.get_progress_percentage() / 100,
                'current':
                self.stats.current_operation,
                'total':
                self.stats.total_operations,
                'elapsed':
                self.stats.get_elapsed_time(),
                'remaining':
                self.stats.estimate_remaining_time()
            })

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

    def synchronize(self,
                    mode: str,
                    files_to_create: Optional[List[str]] = None,
                    files_to_create_reverse: Optional[List[str]] = None,
                    files_to_update: Optional[List[str]] = None,
                    files_to_delete: Optional[List[str]] = None) -> None:
        """Synchronise les dossiers selon le mode choisi."""
        try:
            self.cancelled = False
            self.stats.start_time = datetime.now()
            logger.info(f"Début de la synchronisation en mode {mode}")

            if mode == "Bidirectionnel (miroir)":
                logger.info("Mode bidirectionnel activé")

                # Récupérer les fichiers à copier dans chaque direction
                files_a_to_b = files_to_create or []
                files_b_to_a = files_to_create_reverse or [
                ]  # Utiliser directement le paramètre

                logger.info(f"Fichiers à copier A->B: {len(files_a_to_b)}")
                logger.info(f"Fichiers à copier B->A: {len(files_b_to_a)}")

                # 1. Copier les fichiers de A vers B
                for file in files_a_to_b:
                    if self.cancelled:
                        raise InterruptedError("Synchronisation annulée")

                    source = self.dossier_a / file
                    dest = self.dossier_b / file

                    try:
                        if source.is_file():
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, dest)
                            self.stats.files_created += 1
                            logger.info(f"Copié A->B: {file}")
                        elif source.is_dir():
                            dest.mkdir(parents=True, exist_ok=True)
                            self.stats.dirs_created += 1
                            logger.info(f"Dossier créé A->B: {file}")
                    except Exception as e:
                        logger.error(
                            f"Erreur lors de la copie A->B de {file}: {e}")
                        raise

                # 2. Copier les fichiers de B vers A
                for file in files_b_to_a:
                    if self.cancelled:
                        raise InterruptedError("Synchronisation annulée")

                        source = self.dossier_b / file
                        dest = self.dossier_a / file

                    try:
                        if source.is_file():
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, dest)
                            self.stats.files_created += 1
                            logger.info(f"Copié B->A: {file}")
                        elif source.is_dir():
                            dest.mkdir(parents=True, exist_ok=True)
                            self.stats.dirs_created += 1
                            logger.info(f"Dossier créé B->A: {file}")
                    except Exception as e:
                        logger.error(
                            f"Erreur lors de la copie B->A de {file}: {e}")
                        raise

                # 3. Mettre à jour les fichiers communs
                for file in (files_to_update or []):
                    if self.cancelled:
                        raise InterruptedError("Synchronisation annulée")

                    file_a = self.dossier_a / file
                    file_b = self.dossier_b / file

                    try:
                        # Copier le plus récent vers le plus ancien
                        if file_a.stat().st_mtime > file_b.stat().st_mtime:
                            shutil.copy2(file_a, file_b)
                            self.stats.files_updated += 1
                            logger.info(f"Mis à jour A->B: {file}")
                        else:
                            shutil.copy2(file_b, file_a)
                            self.stats.files_updated += 1
                            logger.info(f"Mis à jour B->A: {file}")
                    except Exception as e:
                        logger.error(
                            f"Erreur lors de la mise à jour de {file}: {e}")
                        raise

                logger.info(
                    "Synchronisation bidirectionnelle terminée avec succès")
                return

            # Code existant pour les autres modes...

            # Créer les nouveaux fichiers
            for file in files_to_create:
                if self.cancelled:
                    raise InterruptedError("Synchronisation annulée")

                source = self.dossier_a / file
                dest = self.dossier_b / file

                logger.info(f"Création de {file}")
                if source.is_dir():
                    # Créer le dossier
                    dest.mkdir(parents=True, exist_ok=True)
                    self.stats.dirs_created += 1
                    self.stats.created_files.append(file)
                else:
                    # Copier le fichier
                    if self.safe_copy(source, dest):
                        self.stats.files_created += 1
                        self.stats.created_files.append(file)
                        self.stats.total_size += source.stat().st_size
                        logger.info(f"Fichier créé : {file}")
                    else:
                        logger.warning(f"Échec de la création de {file}")

            # Mettre à jour les fichiers
            for file in files_to_update:
                if self.cancelled:
                    raise InterruptedError("Synchronisation annulée")

                source = self.dossier_a / file
                dest = self.dossier_b / file

                logger.info(f"Mise à jour de {file}")
                if self.safe_copy(source, dest):
                    self.stats.files_updated += 1
                    self.stats.updated_files.append(file)
                    self.stats.total_size += source.stat().st_size
                    logger.info(f"Fichier mis à jour : {file}")
                else:
                    logger.warning(f"Échec de la mise à jour de {file}")

            # Supprimer les fichiers
            if files_to_delete:
                # Trier les fichiers et dossiers
                files = [
                    f for f in files_to_delete
                    if (self.dossier_b / f).is_file()
                ]
                dirs = [
                    d for d in files_to_delete
                    if (self.dossier_b / d).is_dir()
                ]
                dirs.sort(key=lambda x: len(Path(x).parts), reverse=True)

                # Supprimer les fichiers
                for file in files:
                    if self.cancelled:
                        raise InterruptedError("Synchronisation annulée")

                    file_path = self.dossier_b / file
                    logger.info(f"Suppression du fichier {file}")

                    if self.safe_delete(file_path):
                        self.stats.files_deleted += 1
                        self.stats.deleted_files.append(file)
                        logger.info(f"Fichier supprimé : {file}")
                    else:
                        logger.warning(f"Échec de la suppression de {file}")

            self.stats.end_time = datetime.now()
            logger.info("Synchronisation terminée")
            logger.info(f"Fichiers créés : {len(self.stats.created_files)}")
            logger.info(
                f"Fichiers mis à jour : {len(self.stats.updated_files)}")
            logger.info(
                f"Fichiers supprimés : {len(self.stats.deleted_files)}")

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation : {str(e)}")
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
            if dest_cols[1].button("��", key="select_b"):
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
                st.subheader("Résultats de la comparaison")

                # Options de synchronisation
                with st.expander("⚙️ Options de synchronisation",
                                 expanded=True):
                    # Synthèse globale
                    st.write("### 📊 Synthèse des modifications")
                    total_files = (
                        len(st.session_state.comparison_results['to_create']) +
                        len(st.session_state.comparison_results['to_update']) +
                        len(st.session_state.comparison_results['to_delete']))
                    st.info(f"""
                    **Total des modifications détectées : {total_files} fichiers**
                    - 📝 {len(st.session_state.comparison_results['to_create'])} fichiers à créer
                    - 🔄 {len(st.session_state.comparison_results['to_update'])} fichiers à mettre à jour
                    - 🗑️ {len(st.session_state.comparison_results['to_delete'])} fichiers à supprimer
                    """)

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
                            st.write("#### �� Fichiers à créer")
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

                # Détails des modifications
                with st.expander("📋 Détails des modifications", expanded=True):
                    # Fichiers à créer
                    if st.session_state.comparison_results.get('to_create'):
                        st.write("#### 📝 Fichiers à créer")
                        st.info(
                            f"{len(st.session_state.files_to_create)} fichiers sélectionnés sur {len(st.session_state.comparison_results['to_create'])}"
                        )
                        for f in sorted(st.session_state.
                                        comparison_results['to_create']):
                            prefix = "➕" if f in st.session_state.files_to_create else "⏸️"
                            st.text(f"{prefix} {f}")

                    # Fichiers à mettre à jour
                    if st.session_state.comparison_results.get('to_update'):
                        st.write("#### 🔄 Fichiers à mettre à jour")
                        st.warning(
                            f"{len(st.session_state.files_to_update)} fichiers sélectionnés sur {len(st.session_state.comparison_results['to_update'])}"
                        )
                        for f in sorted(st.session_state.
                                        comparison_results['to_update']):
                            prefix = "🔄" if f in st.session_state.files_to_update else "⏸️"
                            st.text(f"{prefix} {f}")

                    # Fichiers à supprimer
                    if st.session_state.comparison_results.get('to_delete'):
                        st.write("#### 🗑️ Fichiers à supprimer")
                        st.error(
                            f"{len(st.session_state.files_to_delete)} fichiers sélectionnés sur {len(st.session_state.comparison_results['to_delete'])}"
                        )
                        for f in sorted(st.session_state.
                                        comparison_results['to_delete']):
                            prefix = "🗑️" if f in st.session_state.files_to_delete else "⏸️"
                            st.text(f"{prefix} {f}")

                    # Gestion de la synchronisation
                    if st.button("🚀 Lancer la synchronisation",
                                 type="primary",
                                 key="launch_sync"):
                        # Afficher la confirmation
                        if "confirm_state" not in st.session_state:
                            st.session_state.confirm_state = "asking"

                        if st.session_state.confirm_state == "asking":
                            st.write("### Confirmation")
                            st.warning(
                                "Voulez-vous vraiment lancer la synchronisation ?"
                            )

                            col1, col2 = st.columns(2)

                            if col1.button("✅ Oui, synchroniser",
                                           key="yes_sync"):
                                st.session_state.confirm_state = "confirmed"
                                st.rerun()

                            if col2.button("❌ Non, annuler", key="no_sync"):
                                st.session_state.confirm_state = "cancelled"
                                st.rerun()

                        elif st.session_state.confirm_state == "confirmed":
                            try:
                                # Lancer la synchronisation
                                self.synchronize(
                                    mode=st.session_state.mode,
                                    files_to_create=st.session_state.
                                    files_to_create,
                                    files_to_create_reverse=st.session_state.
                                    files_to_create_reverse,
                                    files_to_update=st.session_state.
                                    files_to_update,
                                    files_to_delete=st.session_state.
                                    files_to_delete)

                                # Afficher le succès
                                st.success(
                                    "✅ Synchronisation terminée avec succès!")
                                logger.info(
                                    "Synchronisation terminée avec succès")

                                # Mettre à jour la comparaison
                                st.session_state.comparison_results = self.compare_folders(
                                )

                                # Réinitialiser l'état de confirmation
                                st.session_state.confirm_state = "asking"
                                st.rerun()

                            except Exception as e:
                                st.error(
                                    f"❌ Erreur lors de la synchronisation: {str(e)}"
                                )
                                logger.error(
                                    f"Erreur lors de la synchronisation: {e}")
                                logger.exception("Détails de l'erreur:")
                                st.session_state.confirm_state = "asking"

                        elif st.session_state.confirm_state == "cancelled":
                            st.info("Synchronisation annulée")
                            st.session_state.confirm_state = "asking"
                            st.rerun()

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
    """Point d'entrée principal de l'application"""
    try:
        # Créer une instance de DossierSync avec des chemins par défaut
        sync = DossierSync("", "")

        # Appeler show_ui avec l'instance
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
