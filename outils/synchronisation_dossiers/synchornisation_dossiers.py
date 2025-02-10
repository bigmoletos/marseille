"""
Module de synchronisation bidirectionnelle de dossiers.

Ce module permet de synchroniser deux dossiers selon différents modes :
- A vers B (sauvegarde)
- B vers A (restauration)
- Synchronisation bidirectionnelle

Le module utilise un fichier .fileignore pour exclure certains fichiers/dossiers.
"""

import os
import shutil
import logging
import filecmp
from datetime import datetime
from pathlib import Path
import sys
import hashlib
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sync.log')
    ]
)
logger = logging.getLogger(__name__)

class DossierSync:
    """Classe gérant la synchronisation entre deux dossiers."""

    def __init__(self, dossier_a, dossier_b):
        """
        Initialise la synchronisation.

        Args:
            dossier_a (str): Chemin du dossier source
            dossier_b (str): Chemin du dossier destination
        """
        self.dossier_a = Path(dossier_a)
        self.dossier_b = Path(dossier_b)
        self.ignored_patterns = self._load_ignore_patterns()
        self.manifest = {}
        # Statistiques de synchronisation
        self.stats = {
            'start_time': None,
            'end_time': None,
            'files_created': 0,
            'files_updated': 0,
            'files_deleted': 0,
            'dirs_created': 0,
            'total_size': 0,
            'deleted_files': []
        }
        self.skip_all_deletions = False
        self.confirm_all_deletions = False
        self.progress_var = None
        self.progress_label = None
        self.total_files = 0
        self.processed_files = 0

    def _load_ignore_patterns(self):
        """
        Charge les patterns à ignorer depuis .fileignore.

        Returns:
            set: Ensemble des patterns à ignorer
        """
        ignore_file = Path(__file__).parent / '.fileignore'
        if not ignore_file.exists():
            # Création du .fileignore par défaut
            default_ignores = """
# Fichiers système
.DS_Store
Thumbs.db
desktop.ini

# Environnements virtuels Python
venv/
env/
.env/
.venv/

# Fichiers Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Git
.git/
.gitignore
.gitattributes

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Logs
*.log

# Fichiers temporaires
tmp/
temp/
*.tmp
*.bak
"""
            with open(ignore_file, 'w', encoding='utf-8') as f:
                f.write(default_ignores.strip())

        with open(ignore_file, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip() and not line.startswith('#')}

    def _should_ignore(self, path):
        """
        Vérifie si un chemin doit être ignoré.

        Args:
            path (Path): Chemin à vérifier

        Returns:
            bool: True si le chemin doit être ignoré
        """
        path_str = str(path)
        return any(
            ignored in path_str or
            path.match(ignored)
            for ignored in self.ignored_patterns
        )

    def _calculate_file_hash(self, file_path):
        """
        Calcule le hash SHA-256 d'un fichier.

        Args:
            file_path (Path): Chemin du fichier

        Returns:
            str: Hash SHA-256 du fichier
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _create_manifest(self, source_dir):
        """
        Crée un manifest des fichiers avec leurs hashes.

        Args:
            source_dir (Path): Dossier source

        Returns:
            dict: Manifest avec les chemins relatifs et leurs hashes
        """
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'source_dir': str(source_dir),
            'files': {}
        }

        for item in source_dir.rglob('*'):
            if item.is_file() and not self._should_ignore(item):
                relative_path = str(item.relative_to(source_dir))
                manifest['files'][relative_path] = {
                    'hash': self._calculate_file_hash(item),
                    'size': item.stat().st_size,
                    'mtime': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }

        return manifest

    def _save_manifest(self, manifest, dest_dir):
        """
        Sauvegarde le manifest dans le dossier de destination.

        Args:
            manifest (dict): Manifest à sauvegarder
            dest_dir (Path): Dossier de destination
        """
        manifest_path = dest_dir / 'sync_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
        logger.info(f"Manifest sauvegardé: {manifest_path}")

    def _verify_sync(self, source_dir, dest_dir, manifest):
        """
        Vérifie l'intégrité de la synchronisation.

        Args:
            source_dir (Path): Dossier source
            dest_dir (Path): Dossier destination
            manifest (dict): Manifest de référence

        Returns:
            tuple: (succès, liste des erreurs)
        """
        errors = []
        success = True

        for rel_path, info in manifest['files'].items():
            source_file = source_dir / rel_path
            dest_file = dest_dir / rel_path

            if not dest_file.exists():
                errors.append(f"Fichier manquant: {rel_path}")
                success = False
                continue

            dest_hash = self._calculate_file_hash(dest_file)
            if dest_hash != info['hash']:
                errors.append(f"Hash incorrect pour {rel_path}")
                success = False

        return success, errors

    def _get_files_list(self, directory):
        """
        Obtient la liste des fichiers d'un répertoire.

        Returns:
            set: Ensemble des chemins relatifs des fichiers
        """
        files = set()
        if directory.exists():
            for item in directory.rglob('*'):
                if item.is_file() and not self._should_ignore(item):
                    files.add(str(item.relative_to(directory)))
        return files

    def _compare_directories(self):
        """Compare les deux dossiers et retourne les différences."""
        comparison = {
            'identical': [],
            'different': [],
            'only_in_a': [],
            'only_in_b': []
        }

        files_a = self._get_files_list(self.dossier_a)
        files_b = self._get_files_list(self.dossier_b)

        for file in files_a:
            path_a = self.dossier_a / file
            path_b = self.dossier_b / file

            if file in files_b:
                if filecmp.cmp(path_a, path_b, shallow=False):
                    comparison['identical'].append(file)
                else:
                    comparison['different'].append(file)
            else:
                comparison['only_in_a'].append(file)

        comparison['only_in_b'] = list(files_b - files_a)
        return comparison

    def show_comparison_dialog(self):
        """Affiche la fenêtre de comparaison des dossiers."""
        dialog = tk.Toplevel()
        dialog.title("Comparaison des dossiers")
        dialog.geometry("800x600")

        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # En-tête avec les chemins complets
        tk.Label(
            main_frame,
            text=f"Dossier A:\n{self.dossier_a.absolute()}",
            wraplength=700,
            justify='left',
            font=("Arial", 10, "bold")
        ).pack(anchor='w')

        tk.Label(
            main_frame,
            text=f"Dossier B:\n{self.dossier_b.absolute()}",
            wraplength=700,
            justify='left',
            font=("Arial", 10, "bold")
        ).pack(anchor='w', pady=(5, 15))

        # Obtenir la comparaison
        comparison = self._compare_directories()

        # Frame pour les sections
        sections_frame = tk.Frame(main_frame)
        sections_frame.pack(fill='both', expand=True)

        def create_section(title, files, row):
            """Crée une section expansible pour une catégorie de fichiers."""
            frame = tk.Frame(sections_frame)
            frame.grid(row=row, column=0, sticky='ew', pady=5)
            sections_frame.grid_columnconfigure(0, weight=1)

            content_visible = tk.BooleanVar(value=False)

            def toggle_content():
                if content_visible.get():
                    content.pack(fill='both', expand=True, pady=5)
                    toggle_btn.config(text="➖")
                else:
                    content.pack_forget()
                    toggle_btn.config(text="➕")

            # En-tête avec bouton et nombre
            header = tk.Frame(frame)
            header.pack(fill='x')

            toggle_btn = tk.Button(
                header,
                text="➕",
                command=lambda: [content_visible.set(not content_visible.get()), toggle_content()],
                width=2,
                font=("Arial", 10)
            )
            toggle_btn.pack(side='left', padx=(0, 5))

            tk.Label(
                header,
                text=f"{title} ({len(files)})",
                font=("Arial", 10, "bold")
            ).pack(side='left')

            # Contenu (initialement caché)
            content = tk.Frame(frame)
            if files:
                text = tk.Text(content, height=6, wrap='none')
                scrollbar = ttk.Scrollbar(content, orient='vertical', command=text.yview)
                text.configure(yscrollcommand=scrollbar.set)

                text.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')

                for file in sorted(files):
                    text.insert('end', f"{file}\n")
                text.configure(state='disabled')

        create_section("Fichiers identiques", comparison['identical'], 0)
        create_section("Fichiers différents", comparison['different'], 1)
        create_section("Fichiers uniquement dans A", comparison['only_in_a'], 2)
        create_section("Fichiers uniquement dans B", comparison['only_in_b'], 3)

        # Boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Continuer",
            command=dialog.destroy,
            width=15,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Annuler",
            command=lambda: [dialog.quit(), dialog.destroy(), sys.exit(0)],
            width=15
        ).pack(side='left', padx=5)

        dialog.mainloop()

    def _confirm_deletion(self, file_path):
        """Boîte de dialogue de confirmation de suppression améliorée."""
        if self.skip_all_deletions:
            return 'no'
        if self.confirm_all_deletions:
            return 'yes'

        dialog = tk.Toplevel()
        dialog.title("Confirmation de suppression")
        dialog.geometry("600x300")

        result = tk.StringVar()

        def set_result(value):
            result.set(value)
            dialog.quit()
            dialog.destroy()

        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Chemin complet du fichier
        tk.Label(
            main_frame,
            text="Fichier à supprimer :",
            font=("Arial", 10, "bold")
        ).pack(anchor='w')

        tk.Label(
            main_frame,
            text=str(self.dossier_b / file_path),
            wraplength=550,
            justify='left'
        ).pack(anchor='w', pady=(0, 15))

        # Message d'avertissement
        tk.Label(
            main_frame,
            text="Cette action est irréversible. Voulez-vous continuer ?",
            font=("Arial", 10, "bold"),
            fg="red"
        ).pack(pady=10)

        # Boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        buttons = [
            ("Oui", "yes", None),
            ("Oui pour tous", "all", None),
            ("Non", "no", None),
            ("Non pour tous", "skip_all", None),
            ("Annuler la synchronisation", "cancel", "red")
        ]

        for text, value, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda v=value: set_result(v),
                width=20
            )
            if color:
                btn.configure(fg=color)
            btn.pack(pady=2)

        # Centrer la fenêtre
        dialog.update_idletasks()
        dialog.geometry(f"+{dialog.winfo_screenwidth()//2-300}+{dialog.winfo_screenheight()//2-150}")

        dialog.mainloop()

        if result.get() == "cancel":
            sys.exit(0)

        return result.get()

    def _check_deleted_files(self, source, dest):
        """Identifie les fichiers supprimés dans la destination."""
        source_files = self._get_files_list(source)
        dest_files = self._get_files_list(dest)

        deleted_files = dest_files - source_files
        for file in deleted_files:
            dest_file = dest / file

            # Demander confirmation
            response = self._confirm_deletion(file)

            if response == 'all':
                self.confirm_all_deletions = True
            elif response == 'skip_all':
                self.skip_all_deletions = True
                break

            if response in ('yes', 'all'):
                try:
                    dest_file.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['deleted_files'].append(file)
                    logger.warning(f"Fichier supprimé: {file}")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {file}: {str(e)}")

    def set_progress_widgets(self, progress_var, progress_label):
        """Configure les widgets de progression."""
        self.progress_var = progress_var
        self.progress_label = progress_label

    def _count_files(self, directory):
        """Compte le nombre total de fichiers à traiter."""
        count = 0
        if directory.exists():
            for item in directory.rglob('*'):
                if item.is_file() and not self._should_ignore(item):
                    count += 1
        return count

    def _update_progress(self, message=""):
        """Met à jour la barre de progression."""
        if self.progress_var and self.progress_label:
            progress = (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
            self.progress_var.set(progress)
            self.progress_label.config(text=message)
            self.progress_label.update()

    def _sync_files(self, source, dest):
        """Synchronise les fichiers avec barre de progression."""
        try:
            self.stats['start_time'] = datetime.now()

            # Compter les fichiers à traiter
            self.total_files = self._count_files(source)
            self.processed_files = 0
            self._update_progress("Démarrage de la synchronisation...")

            # Vérification des fichiers supprimés
            self._check_deleted_files(source, dest)

            # Vérification et création du dossier source si nécessaire
            if not source.exists():
                logger.warning(f"Le dossier source {source} n'existe pas")
                source.mkdir(parents=True)
                logger.info(f"Création du dossier source {source}")
                self.stats['dirs_created'] += 1
                return

            # Vérification et création du dossier destination
            if not dest.exists():
                dest.mkdir(parents=True)
                logger.info(f"Création du dossier destination {dest}")
                self.stats['dirs_created'] += 1

            # Synchronisation des fichiers
            for item in source.rglob('*'):
                if self._should_ignore(item):
                    continue

                try:
                    relative_path = item.relative_to(source)
                    target_path = dest / relative_path

                    if item.is_file():
                        # Création du dossier parent si nécessaire
                        if not target_path.parent.exists():
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            self.stats['dirs_created'] += 1

                        if not target_path.exists():
                            # Nouveau fichier
                            shutil.copy2(item, target_path)
                            self.stats['files_created'] += 1
                            self.stats['total_size'] += item.stat().st_size
                            logger.info(f"Copié: {relative_path}")
                        elif not filecmp.cmp(item, target_path, shallow=False):
                            # Fichier modifié
                            self.stats['files_updated'] += 1
                            self.stats['total_size'] += item.stat().st_size
                            shutil.copy2(item, target_path)
                            logger.info(f"Mis à jour: {relative_path}")

                    elif item.is_dir() and not target_path.exists():
                        target_path.mkdir(parents=True, exist_ok=True)
                        self.stats['dirs_created'] += 1
                        logger.info(f"Créé dossier: {relative_path}")

                    self.processed_files += 1
                    self._update_progress(f"Traitement : {relative_path}")

                except Exception as e:
                    logger.error(f"Erreur lors de la copie de {item}: {str(e)}")
                    continue

            # Création et vérification du manifest
            manifest = self._create_manifest(source)
            self._save_manifest(manifest, dest)
            success, errors = self._verify_sync(source, dest, manifest)

            # Finalisation des statistiques
            self.stats['end_time'] = datetime.now()
            self._print_sync_summary()

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            raise

    def _print_sync_summary(self):
        """
        Affiche un résumé de la synchronisation.
        """
        duration = self.stats['end_time'] - self.stats['start_time']
        size_mb = self.stats['total_size'] / (1024 * 1024)  # Conversion en MB

        summary = f"""
=== Résumé de la synchronisation ===
Durée: {duration.total_seconds():.2f} secondes
Fichiers:
  - Créés: {self.stats['files_created']}
  - Mis à jour: {self.stats['files_updated']}
  - Supprimés: {self.stats['files_deleted']}
Dossiers créés: {self.stats['dirs_created']}
Taille totale transférée: {size_mb:.2f} MB
"""
        if self.stats['deleted_files']:
            summary += "\nFichiers supprimés:\n"
            for file in self.stats['deleted_files']:
                summary += f"  - {file}\n"

        logger.info(summary)

    def show_sync_summary(self):
        """Affiche le résumé avec options de continuation."""
        dialog = tk.Toplevel()
        dialog.title("Résumé de la synchronisation")
        dialog.geometry("600x500")  # Hauteur augmentée pour les boutons

        # Frame principal
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Titre
        tk.Label(
            main_frame,
            text="Résumé de la synchronisation",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Statistiques
        duration = self.stats['end_time'] - self.stats['start_time']
        size_mb = self.stats['total_size'] / (1024 * 1024)

        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=10)

        stats_text = f"""
Durée: {duration.total_seconds():.2f} secondes

Fichiers:
  • Créés: {self.stats['files_created']}
  • Mis à jour: {self.stats['files_updated']}
  • Supprimés: {self.stats['files_deleted']}

Dossiers créés: {self.stats['dirs_created']}
Taille totale transférée: {size_mb:.2f} MB
"""

        tk.Label(
            stats_frame,
            text=stats_text,
            justify='left',
            font=("Consolas", 10)
        ).pack(anchor='w')

        # Liste des fichiers supprimés
        if self.stats['deleted_files']:
            tk.Label(
                main_frame,
                text="Fichiers supprimés:",
                font=("Arial", 10, "bold")
            ).pack(anchor='w', pady=(10, 5))

            # Scrollable text widget pour les fichiers supprimés
            deleted_frame = tk.Frame(main_frame)
            deleted_frame.pack(fill='both', expand=True)

            scrollbar = tk.Scrollbar(deleted_frame)
            scrollbar.pack(side='right', fill='y')

            deleted_text = tk.Text(
                deleted_frame,
                height=10,
                yscrollcommand=scrollbar.set,
                font=("Consolas", 9)
            )
            deleted_text.pack(side='left', fill='both', expand=True)

            scrollbar.config(command=deleted_text.yview)

            for file in self.stats['deleted_files']:
                deleted_text.insert('end', f"  • {file}\n")
            deleted_text.config(state='disabled')

        # Frame pour les boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side='bottom', pady=20)

        def new_sync():
            dialog.destroy()
            main()  # Relance une nouvelle synchronisation

        def quit_app():
            dialog.quit()
            dialog.destroy()
            sys.exit(0)

        tk.Button(
            button_frame,
            text="Nouvelle synchronisation",
            command=new_sync,
            width=20,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Quitter",
            command=quit_app,
            width=10
        ).pack(side='left', padx=5)

        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        dialog.mainloop()

    def sync(self, mode='both'):
        """
        Synchronise les dossiers avec statistiques globales.
        """
        total_stats = {
            'start_time': datetime.now(),
            'files_created': 0,
            'files_updated': 0,
            'files_deleted': 0,
            'dirs_created': 0,
            'total_size': 0
        }

        try:
            if mode in ('a_to_b', 'both'):
                logger.info("Synchronisation A → B")
                self._sync_files(self.dossier_a, self.dossier_b)
                # Accumulation des statistiques
                for key in total_stats:
                    if key != 'start_time':
                        total_stats[key] += self.stats[key]

            if mode in ('b_to_a', 'both'):
                logger.info("Synchronisation B → A")
                # Réinitialisation des stats pour B → A
                self.stats = {key: 0 for key in self.stats if key not in ['start_time', 'end_time']}
                self.stats['deleted_files'] = []
                self._sync_files(self.dossier_b, self.dossier_a)
                # Accumulation des statistiques
                for key in total_stats:
                    if key != 'start_time':
                        total_stats[key] += self.stats[key]

            # Affichage du résumé global
            duration = datetime.now() - total_stats['start_time']
            size_mb = total_stats['total_size'] / (1024 * 1024)

            logger.info(f"""
=== Résumé global de la synchronisation ({mode}) ===
Durée totale: {duration.total_seconds():.2f} secondes
Total fichiers:
  - Créés: {total_stats['files_created']}
  - Mis à jour: {total_stats['files_updated']}
  - Supprimés: {total_stats['files_deleted']}
Total dossiers créés: {total_stats['dirs_created']}
Taille totale transférée: {size_mb:.2f} MB
""")

            # Remplacer le message de confirmation par l'affichage du résumé
            self.show_sync_summary()

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            raise

def select_directory(message):
    """
    Ouvre une boîte de dialogue pour sélectionner un dossier.

    Args:
        message (str): Message à afficher dans la boîte de dialogue

    Returns:
        str: Chemin du dossier sélectionné ou None si annulé
    """
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale

    directory = filedialog.askdirectory(
        title=message,
        mustexist=False  # Permet de créer un nouveau dossier
    )

    if not directory:
        return None

    return directory

def main():
    """Point d'entrée principal avec barre de progression."""
    try:
        print("\n=== Synchronisation de dossiers ===")

        # Sélection du dossier source (A)
        dossier_a = select_directory("Sélectionnez le dossier source (A)")
        if not dossier_a:
            print("Opération annulée")
            return

        # Sélection du dossier destination (B)
        dossier_b = select_directory("Sélectionnez le dossier destination (B)")
        if not dossier_b:
            print("Opération annulée")
            return

        # Création de la fenêtre de choix du mode
        root = tk.Tk()
        root.title("Mode de synchronisation")
        root.geometry("400x300")  # Hauteur augmentée pour les boutons

        selected_mode = tk.StringVar(value="a_to_b")
        operation_cancelled = tk.BooleanVar(value=False)

        def on_cancel():
            operation_cancelled.set(True)
            root.quit()
            root.destroy()

        def on_submit():
            root.quit()
            root.destroy()

        # Frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Label titre
        tk.Label(
            main_frame,
            text="Choisissez le mode de synchronisation",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Options de synchronisation
        tk.Radiobutton(
            main_frame,
            text="A vers B (sauvegarde)",
            variable=selected_mode,
            value="a_to_b"
        ).pack(anchor='w', pady=5)

        tk.Radiobutton(
            main_frame,
            text="B vers A (restauration)",
            variable=selected_mode,
            value="b_to_a"
        ).pack(anchor='w', pady=5)

        tk.Radiobutton(
            main_frame,
            text="Synchronisation bidirectionnelle",
            variable=selected_mode,
            value="both"
        ).pack(anchor='w', pady=5)

        # Affichage des chemins sélectionnés
        tk.Label(
            main_frame,
            text=f"Dossier A: {dossier_a}",
            wraplength=350
        ).pack(anchor='w', pady=(10, 0))
        tk.Label(
            main_frame,
            text=f"Dossier B: {dossier_b}",
            wraplength=350
        ).pack(anchor='w', pady=(5, 10))

        # Frame pour les boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side='bottom', pady=10)

        # Boutons OK et Annuler
        tk.Button(
            button_frame,
            text="OK",
            command=on_submit,
            width=10,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Annuler",
            command=on_cancel,
            width=10
        ).pack(side='left', padx=5)

        # Centrer la fenêtre
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        root.mainloop()

        # Vérifier si l'opération a été annulée
        if operation_cancelled.get():
            print("Opération annulée")
            return

        # Récupération du mode sélectionné
        mode = selected_mode.get()

        # Conversion du mode en format attendu
        modes = {
            'a_to_b': 'a_to_b',
            'b_to_a': 'b_to_a',
            'both': 'both'
        }

        # Création de la fenêtre de progression
        progress_window = tk.Toplevel()
        progress_window.title("Progression de la synchronisation")
        progress_window.geometry("400x150")

        # Frame principal
        progress_frame = tk.Frame(progress_window, padx=20, pady=20)
        progress_frame.pack(expand=True, fill='both')

        # Label de progression
        progress_label = tk.Label(
            progress_frame,
            text="Initialisation...",
            font=("Arial", 10)
        )
        progress_label.pack(pady=(0, 10))

        # Barre de progression
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_frame,
            variable=progress_var,
            maximum=100,
            mode='determinate',
            length=300
        )
        progress_bar.pack(pady=10)

        # Centrer la fenêtre
        progress_window.update_idletasks()
        width = progress_window.winfo_width()
        height = progress_window.winfo_height()
        x = (progress_window.winfo_screenwidth() // 2) - (width // 2)
        y = (progress_window.winfo_screenheight() // 2) - (height // 2)
        progress_window.geometry(f'{width}x{height}+{x}+{y}')

        # Configuration de la synchronisation
        sync = DossierSync(dossier_a, dossier_b)
        sync.set_progress_widgets(progress_var, progress_label)

        # Afficher la comparaison avant de commencer
        sync.show_comparison_dialog()

        # Exécution de la synchronisation
        sync.sync(modes[mode])

        # Fermeture de la fenêtre de progression
        progress_window.destroy()

        # Affichage du résumé
        sync.show_sync_summary()

    except Exception as e:
        if 'progress_window' in locals():
            progress_window.destroy()
        messagebox.showerror(
            "Erreur",
            f"Une erreur est survenue:\n{str(e)}"
        )
        logger.error(f"Erreur lors de l'exécution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
