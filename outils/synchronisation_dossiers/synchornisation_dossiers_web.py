"""
Version web de la synchronisation de dossiers utilisant Streamlit.
Permet de synchroniser deux dossiers de manière unidirectionnelle ou bidirectionnelle.
"""

import streamlit as st
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from tkinter import filedialog
import tkinter as tk
import subprocess
import json

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

logging.basicConfig(
    level=logging.DEBUG,  # Activer le niveau DEBUG pour plus de détails
    handlers=[streamlit_handler, logging.StreamHandler()])
logger = logging.getLogger(__name__)


def select_folder() -> Optional[str]:
    """Ouvre une fenêtre de sélection de dossier."""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale Tk
    folder = filedialog.askdirectory()
    root.destroy()
    return str(Path(folder).resolve()) if folder else None


# Initialisation de l'état de session si nécessaire
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.comparison_results = None
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


@dataclass
class SyncResults:
    """Résultats de la synchronisation"""
    to_create: List[str] = field(default_factory=list)
    to_update: List[str] = field(default_factory=list)
    to_delete: List[str] = field(default_factory=list)
    to_create_reverse: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def display_comparison(self, container) -> None:
        """Affiche la comparaison des dossiers"""
        if self.to_create:
            expander = container.expander("📝 Fichiers à créer", expanded=True)
            expander.info(f"{len(self.to_create)} fichiers à créer")
            for f in sorted(self.to_create):
                expander.text(f"➕ {f}")

        if self.to_update:
            expander = container.expander("🔄 Fichiers à mettre à jour",
                                          expanded=True)
            expander.warning(f"{len(self.to_update)} fichiers à mettre à jour")
            for f in sorted(self.to_update):
                expander.text(f"🔄 {f}")

        if self.to_delete:
            expander = container.expander("🗑️ Fichiers à supprimer",
                                          expanded=True)
            expander.error(f"{len(self.to_delete)} fichiers à supprimer")
            for f in sorted(self.to_delete):
                expander.text(f"🗑️ {f}")


class DossierSync:
    """Classe principale pour la synchronisation des dossiers"""

    def __init__(self):
        """Initialise l'interface de synchronisation."""
        self.script_path = Path(__file__).parent / "sync_folders.sh"
        if not self.script_path.exists():
            raise FileNotFoundError(
                f"Script shell non trouvé: {self.script_path}")

        self.script_path.chmod(0o755)
        self.root = tk.Tk()
        self.root.withdraw()

    def run_script(self, action: str, output_file: Path) -> Dict:
        """Exécute le script shell pour la comparaison ou la synchronisation."""
        try:
            cmd = [
                str(self.script_path), action,
                str(st.session_state.dossier_a),
                str(st.session_state.dossier_b), st.session_state.mode,
                str(output_file)
            ]

            if os.name == 'nt':  # Windows
                cmd = ["C:/Program Files/Git/bin/bash.exe"] + cmd

            logger.debug(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(
                    f"Erreur lors de l'exécution du script: {result.stderr}")
                raise RuntimeError(
                    f"Erreur lors de l'exécution du script: {result.stderr}")

            with open(output_file) as f:
                results = json.load(f)

            if results.get("error"):
                raise RuntimeError(results["error"])

            return results

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du script: {e}")
            raise

    def compare_folders(self) -> SyncResults:
        """Compare les dossiers en utilisant le script shell."""
        output_file = Path("comparison_results.json")
        results = self.run_script("compare", output_file)
        logger.debug(f"Comparison results: {results}")
        return SyncResults(**results)

    def synchronize(self) -> None:
        """Effectue la synchronisation en utilisant le script shell."""
        output_file = Path("sync_results.json")
        files_to_create = ','.join(st.session_state.files_to_create)
        files_to_update = ','.join(st.session_state.files_to_update)
        files_to_delete = ','.join(st.session_state.files_to_delete)
        files_to_create_reverse = ','.join(
            st.session_state.get('files_to_create_reverse', []))

        cmd = [
            str(self.script_path), "sync",
            str(st.session_state.dossier_a),
            str(st.session_state.dossier_b), files_to_create, files_to_update,
            files_to_delete, files_to_create_reverse
        ]

        if os.name == 'nt':  # Windows
            cmd = ["C:/Program Files/Git/bin/bash.exe"] + cmd

        logger.debug(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"Erreur lors de la synchronisation: {result.stderr}")

    def select_folder(self) -> str:
        """Ouvre une boîte de dialogue pour sélectionner un dossier."""
        try:
            folder = filedialog.askdirectory(parent=self.root)
            return folder if folder else None
        except Exception as e:
            logger.error(f"Erreur lors de la sélection du dossier: {e}")
            return None

    def show_ui(self):
        """Affiche l'interface utilisateur Streamlit."""
        try:
            st.title("🔄 Synchronisation de dossiers")

            if "dossier_a" not in st.session_state:
                st.session_state.dossier_a = ""
            if "dossier_b" not in st.session_state:
                st.session_state.dossier_b = ""
            if "mode" not in st.session_state:
                st.session_state.mode = "A vers B (sauvegarde)"

            cols = st.columns(2)

            source_cols = cols[0].columns([3, 1])
            st.session_state.dossier_a = source_cols[0].text_input(
                "Dossier source (A)", value=st.session_state.dossier_a)
            if source_cols[1].button("📁", key="select_a"):
                folder = self.select_folder()
                if folder:
                    st.session_state.dossier_a = folder
                    st.rerun()

            dest_cols = cols[1].columns([3, 1])
            st.session_state.dossier_b = dest_cols[0].text_input(
                "Dossier destination (B)", value=st.session_state.dossier_b)
            if dest_cols[1].button("📁", key="select_b"):
                folder = self.select_folder()
                if folder:
                    st.session_state.dossier_b = folder
                    st.rerun()

            st.session_state.mode = st.selectbox("Mode de synchronisation", [
                "A vers B (sauvegarde)", "B vers A (restauration)",
                "Bidirectionnel (miroir)"
            ])

            if st.button("🔍 Comparer", type="primary"):
                try:
                    results = self.compare_folders()
                    st.session_state.comparison_results = results
                    st.success("Comparaison effectuée")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

            if st.session_state.comparison_results:
                self._show_comparison_results()

            if st.button("🚀 Lancer la synchronisation",
                         type="primary",
                         key="launch_sync"):
                try:
                    self.synchronize()
                    st.success("✅ Synchronisation terminée avec succès!")
                    st.session_state.comparison_results = self.compare_folders(
                    )
                    st.rerun()
                except Exception as e:
                    logger.error(f"Erreur lors de la synchronisation: {e}",
                                 exc_info=True)
                    st.error(f"❌ Erreur lors de la synchronisation: {str(e)}")

        except Exception as e:
            logger.error(f"Erreur dans l'interface: {e}")
            st.error(f"❌ Erreur: {str(e)}")

    def _show_comparison_results(self):
        """Affiche les résultats de la comparaison et les options de synchronisation."""
        st.write("## 📊 Synthèse des modifications")

        results = st.session_state.comparison_results
        mode = st.session_state.mode

        if results.to_create or results.to_update:
            st.write("#### 📝 Fichiers à copier/mettre à jour")
            total_files = len(results.to_create) + len(results.to_update)
            st.write(f"**Total : {total_files} fichiers**")

            col1, col2 = st.columns(2)
            if col1.button("Tout sélectionner", key="copy_all"):
                st.session_state.files_to_create = results.to_create.copy()
                st.session_state.files_to_update = results.to_update.copy()
            if col2.button("Ne rien copier", key="copy_none"):
                st.session_state.files_to_create = []
                st.session_state.files_to_update = []

            if results.to_create:
                st.markdown("##### Nouveaux fichiers :")
                for file in sorted(results.to_create):
                    st.text(f"➕ {file}")
                st.session_state.files_to_create = st.multiselect(
                    "Sélection des nouveaux fichiers à copier",
                    options=results.to_create,
                    default=st.session_state.files_to_create)

            if results.to_update:
                st.markdown("##### Fichiers modifiés :")
                for file in sorted(results.to_update):
                    st.text(f"🔄 {file}")
                st.session_state.files_to_update = st.multiselect(
                    "Sélection des fichiers à mettre à jour",
                    options=results.to_update,
                    default=st.session_state.files_to_update)

        if mode != "Bidirectionnel (miroir)" and results.to_delete:
            st.write("#### 🗑️ Fichiers à supprimer")
            st.error(
                "⚠️ **ATTENTION : La suppression est une opération irréversible**"
            )
            st.write(f"**Total : {len(results.to_delete)} fichiers**")

            col1, col2 = st.columns(2)
            if col1.button("Tout sélectionner", key="delete_all"):
                st.session_state.files_to_delete = results.to_delete.copy()
            if col2.button("Ne rien supprimer", key="delete_none"):
                st.session_state.files_to_delete = []

            st.markdown("##### Liste des fichiers à supprimer :")
            for file in sorted(results.to_delete):
                st.text(f"❌ {file}")

            st.session_state.files_to_delete = st.multiselect(
                "Sélection des fichiers à supprimer",
                options=results.to_delete,
                default=st.session_state.files_to_delete)

    def __del__(self):
        """Nettoyage à la destruction de l'objet."""
        try:
            self.root.destroy()
        except:
            pass


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


def main():
    """Point d'entrée principal."""
    sync = DossierSync()
    sync.show_ui()


if __name__ == "__main__":
    main()
