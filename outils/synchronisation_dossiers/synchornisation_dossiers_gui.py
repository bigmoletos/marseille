"""
Version GUI de la synchronisation de dossiers utilisant tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import logging
import filecmp
from datetime import datetime
from pathlib import Path
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('sync.log')]
)
logger = logging.getLogger(__name__)

class DossierSync:
    def __init__(self, dossier_a, dossier_b):
        self.dossier_a = Path(dossier_a)
        self.dossier_b = Path(dossier_b)
        self.ignored_patterns = self._load_ignore_patterns()
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
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def _load_ignore_patterns(self):
        ignore_file = Path(__file__).parent / '.fileignore'
        if not ignore_file.exists():
            return set()
        with open(ignore_file, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip() and not line.startswith('#')}

    def _should_ignore(self, path):
        path_str = str(path)
        return any(
            ignored in path_str or path.match(ignored)
            for ignored in self.ignored_patterns
        )

    def _get_files_list(self, directory):
        files = set()
        if directory.exists():
            for item in directory.rglob('*'):
                if item.is_file() and not self._should_ignore(item):
                    files.add(str(item.relative_to(directory)))
        return files

    def _compare_directories(self):
        comparison = {
            'identical': [],
            'different': [],
            'only_in_a': [],
            'only_in_b': []
        }

        files_a = self._get_files_list(self.dossier_a)
        files_b = self._get_files_list(self.dossier_b)
        total_files = len(files_a | files_b)
        processed = 0

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

            processed += 1
            if self.progress_callback:
                self.progress_callback(processed, total_files, f"Analyse : {file}")

        comparison['only_in_b'] = list(files_b - files_a)
        return comparison

    def sync(self, mode):
        self.stats['start_time'] = datetime.now()
        try:
            if mode == 'a_to_b':
                self._sync_direction(self.dossier_a, self.dossier_b)
            elif mode == 'b_to_a':
                self._sync_direction(self.dossier_b, self.dossier_a)
            else:  # both
                self._sync_direction(self.dossier_a, self.dossier_b)
                self._sync_direction(self.dossier_b, self.dossier_a)
            self.stats['end_time'] = datetime.now()
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            raise

    def _sync_direction(self, source, dest):
        files = list(source.rglob('*'))
        total_files = len(files)

        for i, item in enumerate(files):
            if self._should_ignore(item):
                continue

            relative_path = item.relative_to(source)
            target_path = dest / relative_path

            if self.progress_callback:
                self.progress_callback(i + 1, total_files, f"Copie : {relative_path}")

            try:
                if item.is_file():
                    if not target_path.exists():
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
                        self.stats['files_created'] += 1
                        self.stats['total_size'] += item.stat().st_size
                    elif not filecmp.cmp(item, target_path, shallow=False):
                        shutil.copy2(item, target_path)
                        self.stats['files_updated'] += 1
                        self.stats['total_size'] += item.stat().st_size
                elif item.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    self.stats['dirs_created'] += 1
            except Exception as e:
                logger.error(f"Erreur lors de la copie de {item}: {str(e)}")

    def get_stats(self):
        if self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            size_mb = self.stats['total_size'] / (1024 * 1024)
            return {
                "Durée (secondes)": f"{duration:.2f}",
                "Fichiers créés": self.stats['files_created'],
                "Fichiers mis à jour": self.stats['files_updated'],
                "Fichiers supprimés": self.stats['files_deleted'],
                "Dossiers créés": self.stats['dirs_created'],
                "Taille totale (MB)": f"{size_mb:.2f}"
            }
        return {}

class SyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Synchronisation de dossiers")
        self.root.geometry("800x600")

        # Variables
        self.dossier_a = tk.StringVar()
        self.dossier_b = tk.StringVar()
        self.sync_mode = tk.StringVar(value="a_to_b")

        # Style
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Success.TButton", background="green", foreground="white")

        self.setup_gui()

    def setup_gui(self):
        # Frame principal avec scrollbar
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Sélection des dossiers
        folder_frame = ttk.LabelFrame(self.scrollable_frame, text="Sélection des dossiers", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)

        # Dossier A
        ttk.Label(folder_frame, text="Dossier source (A):", style="Header.TLabel").pack(anchor=tk.W)
        dossier_a_frame = ttk.Frame(folder_frame)
        dossier_a_frame.pack(fill=tk.X, pady=5)

        self.entry_a = ttk.Entry(dossier_a_frame, textvariable=self.dossier_a, width=60)
        self.entry_a.pack(side=tk.LEFT, padx=5)
        ttk.Button(dossier_a_frame, text="Parcourir", command=lambda: self.browse_folder('a')).pack(side=tk.LEFT)

        # Dossier B
        ttk.Label(folder_frame, text="Dossier destination (B):", style="Header.TLabel").pack(anchor=tk.W)
        dossier_b_frame = ttk.Frame(folder_frame)
        dossier_b_frame.pack(fill=tk.X, pady=5)

        self.entry_b = ttk.Entry(dossier_b_frame, textvariable=self.dossier_b, width=60)
        self.entry_b.pack(side=tk.LEFT, padx=5)
        ttk.Button(dossier_b_frame, text="Parcourir", command=lambda: self.browse_folder('b')).pack(side=tk.LEFT)

        # Mode de synchronisation
        mode_frame = ttk.LabelFrame(self.scrollable_frame, text="Mode de synchronisation", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(
            mode_frame,
            text="A vers B (sauvegarde)",
            value="a_to_b",
            variable=self.sync_mode
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="B vers A (restauration)",
            value="b_to_a",
            variable=self.sync_mode
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="Synchronisation bidirectionnelle",
            value="both",
            variable=self.sync_mode
        ).pack(anchor=tk.W, pady=2)

        # Zone de résultats
        result_frame = ttk.LabelFrame(self.scrollable_frame, text="Résultats", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text = tk.Text(result_frame, height=15, width=70)
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Barre de progression
        progress_frame = ttk.Frame(self.scrollable_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack()

        # Boutons d'action
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Analyser",
            command=self.analyze,
            style="Success.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Synchroniser",
            command=self.synchronize
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Quitter",
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=5)

        # Configuration du scroll
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_folder(self, which):
        folder = filedialog.askdirectory()
        if folder:
            if which == 'a':
                self.dossier_a.set(folder)
            else:
                self.dossier_b.set(folder)

    def analyze(self):
        if not self.validate_folders():
            return

        sync = DossierSync(self.dossier_a.get(), self.dossier_b.get())
        comparison = sync._compare_directories()

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Résultats de l'analyse:\n\n")
        self.result_text.insert(tk.END, f"Fichiers identiques: {len(comparison['identical'])}\n")
        self.result_text.insert(tk.END, f"Fichiers différents: {len(comparison['different'])}\n")
        self.result_text.insert(tk.END, f"Uniquement dans A: {len(comparison['only_in_a'])}\n")
        self.result_text.insert(tk.END, f"Uniquement dans B: {len(comparison['only_in_b'])}\n")

    def synchronize(self):
        if not self.validate_folders():
            return

        if messagebox.askyesno("Confirmation", "Voulez-vous démarrer la synchronisation?"):
            sync = DossierSync(self.dossier_a.get(), self.dossier_b.get())

            def update_progress(current, total, message):
                progress = (current / total) * 100
                self.progress_var.set(progress)
                self.status_label.config(text=message)
                self.root.update()

            sync.set_progress_callback(update_progress)

            try:
                sync.sync(self.sync_mode.get())
                stats = sync.get_stats()

                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Synchronisation terminée!\n\n")
                for key, value in stats.items():
                    self.result_text.insert(tk.END, f"{key}: {value}\n")

                messagebox.showinfo("Succès", "Synchronisation terminée avec succès!")

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la synchronisation:\n{str(e)}")

    def validate_folders(self):
        if not self.dossier_a.get() or not self.dossier_b.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner les deux dossiers")
            return False
        return True

def main():
    root = tk.Tk()
    app = SyncGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()