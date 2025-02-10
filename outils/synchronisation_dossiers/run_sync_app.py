"""
Script de lancement de l'application de synchronisation
"""
import subprocess
import sys
import os
from pathlib import Path
import locale
import codecs

# Configuration de l'encodage pour la sortie standard
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
# Configuration de l'encodage pour l'entrée standard
sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Pour les sorties logging
import logging

logging.basicConfig(encoding='utf-8')


def main() -> None:
    """Fonction principale de lancement de l'application."""
    try:
        # Obtenir le chemin absolu du répertoire contenant ce script
        current_dir = Path(__file__).parent.absolute()

        # Chemin vers le script Streamlit
        streamlit_script = current_dir / "synchornisation_dossiers_web.py"

        if not streamlit_script.exists():
            print(f"Erreur: Le script {streamlit_script} n'existe pas")
            sys.exit(1)

        # Préparer la commande
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(streamlit_script), "--server.address=localhost",
            "--server.headless=true", "--browser.gatherUsageStats=false"
        ]

        # Lancer l'application
        print("Lancement de l'application...")
        process = subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        print(f"Code de sortie: {e.returncode}")
        if e.output:
            print(f"Sortie: {e.output.decode('utf-8')}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nArrêt de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
