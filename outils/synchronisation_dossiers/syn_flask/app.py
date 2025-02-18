# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "flask",
#     "pandas",
#     "numpy",
#     "urllib3",
# ]
# ///

import logging
import sys
import traceback
import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for

# Configuration du logging avancé
logging.basicConfig(
    filename='flask_app.log',
    level=logging.DEBUG,
    format=
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Ajouter aussi le logging vers la console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Pour les messages flash

# Obtenir le chemin absolu du répertoire de l'application
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger.debug(f"Répertoire de l'application : {SCRIPT_DIR}")


def debug_list_host_directory():
    """Liste le contenu des répertoires montés pour le débogage."""
    try:
        logger.info("=== Vérification des lecteurs Windows ===")
        # Utilisation de dir pour lister les lecteurs sous Windows
        cmd = [
            'cmd', '/c', 'wmic', 'logicaldisk', 'get', 'caption,description'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Lecteurs disponibles :")
            logger.info(result.stdout)
        else:
            logger.error(
                f"Erreur lors de la lecture des lecteurs : {result.stderr}")

        # Pour chaque lecteur, vérifier son existence et son contenu
        for drive_letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                logger.info(f"=== Contenu du lecteur {drive_path} ===")
                try:
                    # Utiliser dir pour lister le contenu
                    cmd = ['cmd', '/c', 'dir', drive_path]
                    result = subprocess.run(cmd,
                                            capture_output=True,
                                            text=True)
                    if result.returncode == 0:
                        logger.info(result.stdout)
                    else:
                        logger.error(
                            f"Erreur lors du listage de {drive_path} : {result.stderr}"
                        )
                except Exception as e:
                    logger.error(
                        f"Erreur lors de l'accès au lecteur {drive_path} : {str(e)}"
                    )

    except Exception as e:
        logger.error(f"Erreur lors du listage des répertoires : {str(e)}")
        logger.error(traceback.format_exc())


def convert_path_to_container(windows_path):
    """
    Convertit un chemin Windows en format compatible avec le système de fichiers local.

    Args:
        windows_path (str): Chemin au format Windows

    Returns:
        str: Chemin au format local
    """
    logger.debug(f"Conversion du chemin : {windows_path}")
    if not windows_path:
        logger.warning("Chemin vide reçu pour la conversion")
        return ""

    try:
        # Normalisation du chemin
        path = os.path.normpath(windows_path)
        path = path.replace('\\', '/')

        # Gestion des chemins avec lettre de lecteur (ex: C:\...)
        if len(path) > 1 and path[1] == ':':
            # Pour Windows, on garde le format original
            logger.info(
                f"Utilisation du chemin Windows original : {windows_path}")
            return windows_path

        # Gestion des chemins UNC (ex: \\server\share\...)
        if path.startswith('//') or path.startswith('\\\\'):
            # Pour Windows, on garde le format UNC original
            logger.info(f"Utilisation du chemin UNC original : {windows_path}")
            return windows_path

        # Si le chemin est déjà au format approprié, le retourner tel quel
        logger.info(f"Utilisation du chemin tel quel : {windows_path}")
        return windows_path

    except Exception as e:
        logger.error(f"Erreur lors de la conversion du chemin : {str(e)}")
        logger.error(traceback.format_exc())
        return windows_path


@app.route('/')
def index():
    """Page d'accueil de l'application."""
    logger.debug("Accès à la page d'accueil")
    return render_template('index.html')


@app.route('/compare_folders', methods=['POST'])
def compare_folders():
    """
    Compare les dossiers et affiche les différences.
    """
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']
        output_file = os.path.join(SCRIPT_DIR, 'comparison_output.json')

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA COMPARAISON DES DOSSIERS")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Debug : lister le contenu des répertoires
        debug_list_host_directory()

        # Vérification des chemins
        if not os.path.exists(source_dir):
            error_msg = f"Dossier source introuvable : {source_dir}"
            logger.error("ERREUR DE VÉRIFICATION :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)

        if not os.path.exists(dest_dir):
            error_msg = f"Dossier destination introuvable : {dest_dir}"
            logger.error("ERREUR DE VÉRIFICATION :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)

        logger.info("VÉRIFICATION DES RÉPERTOIRES :")
        # Utiliser dir pour Windows
        logger.info("Contenu du répertoire source :")
        cmd_check_source = ['cmd', '/c', 'dir', '/a', source_dir]
        source_ls = subprocess.run(cmd_check_source,
                                   capture_output=True,
                                   text=True)
        if source_ls.returncode == 0:
            logger.info(source_ls.stdout)
        else:
            logger.error(
                f"Erreur lors de la lecture du répertoire source : {source_ls.stderr}"
            )

        logger.info("Contenu du répertoire destination :")
        cmd_check_dest = ['cmd', '/c', 'dir', '/a', dest_dir]
        dest_ls = subprocess.run(cmd_check_dest,
                                 capture_output=True,
                                 text=True)
        if dest_ls.returncode == 0:
            logger.info(dest_ls.stdout)
        else:
            logger.error(
                f"Erreur lors de la lecture du répertoire destination : {dest_ls.stderr}"
            )
        logger.info("-" * 80)

        # Création d'un script PowerShell temporaire pour la comparaison
        ps_script = os.path.join(SCRIPT_DIR, 'compare_folders.ps1')
        with open(ps_script, 'w', encoding='utf-8') as f:
            f.write(f"""
$ErrorActionPreference = "Stop"
$source = "{source_dir}"
$dest = "{dest_dir}"
$comparison = @{{
    "to_create" = @()
    "to_update" = @()
    "to_delete" = @()
    "to_create_reverse" = @()
    "to_create_dirs" = @()
    "to_delete_dirs" = @()
    "to_create_dirs_reverse" = @()
}}

# Fonction pour obtenir le chemin relatif
function Get-RelativePath($path, $basePath) {{
    return $path.Substring($basePath.Length).TrimStart('\/')
}}

# Obtenir tous les fichiers et dossiers source et destination
$sourceItems = Get-ChildItem -Path $source -Recurse
$destItems = Get-ChildItem -Path $dest -Recurse

# Créer des tables de hachage pour une recherche plus rapide
$sourceDirs = @{{}}
$sourceFiles = @{{}}
$destDirs = @{{}}
$destFiles = @{{}}

# Remplir les tables de hachage source
foreach ($item in $sourceItems) {{
    $relativePath = Get-RelativePath $item.FullName $source
    if ($item.PSIsContainer) {{
        $sourceDirs[$relativePath] = $item
    }} else {{
        $sourceFiles[$relativePath] = $item
    }}
}}

# Remplir les tables de hachage destination
foreach ($item in $destItems) {{
    $relativePath = Get-RelativePath $item.FullName $dest
    if ($item.PSIsContainer) {{
        $destDirs[$relativePath] = $item
    }} else {{
        $destFiles[$relativePath] = $item
    }}
}}

switch ("{mode}") {{
    "A vers B (sauvegarde)" {{
        # Fichiers et dossiers à créer ou mettre à jour dans B
        foreach ($relativePath in $sourceFiles.Keys) {{
            $sourceFile = $sourceFiles[$relativePath]
            if ($destFiles.ContainsKey($relativePath)) {{
                $destFile = $destFiles[$relativePath]
                if ($sourceFile.LastWriteTime -gt $destFile.LastWriteTime) {{
                    $comparison.to_update += $relativePath
                }}
            }} else {{
                $comparison.to_create += $relativePath
            }}
        }}

        # Dossiers à créer dans B
        foreach ($relativePath in $sourceDirs.Keys) {{
            if (-not $destDirs.ContainsKey($relativePath)) {{
                $comparison.to_create_dirs += $relativePath
            }}
        }}

        # Fichiers et dossiers à supprimer dans B
        foreach ($relativePath in $destFiles.Keys) {{
            if (-not $sourceFiles.ContainsKey($relativePath)) {{
                $comparison.to_delete += $relativePath
            }}
        }}
        foreach ($relativePath in $destDirs.Keys) {{
            if (-not $sourceDirs.ContainsKey($relativePath)) {{
                $comparison.to_delete_dirs += $relativePath
            }}
        }}
    }}
    "B vers A (restauration)" {{
        # Fichiers et dossiers à créer ou mettre à jour dans A
        foreach ($relativePath in $destFiles.Keys) {{
            $destFile = $destFiles[$relativePath]
            if ($sourceFiles.ContainsKey($relativePath)) {{
                $sourceFile = $sourceFiles[$relativePath]
                if ($destFile.LastWriteTime -gt $sourceFile.LastWriteTime) {{
                    $comparison.to_create_reverse += $relativePath
                }}
            }} else {{
                $comparison.to_create_reverse += $relativePath
            }}
        }}

        # Dossiers à créer dans A
        foreach ($relativePath in $destDirs.Keys) {{
            if (-not $sourceDirs.ContainsKey($relativePath)) {{
                $comparison.to_create_dirs_reverse += $relativePath
            }}
        }}

        # Fichiers et dossiers à supprimer dans A
        foreach ($relativePath in $sourceFiles.Keys) {{
            if (-not $destFiles.ContainsKey($relativePath)) {{
                $comparison.to_delete += $relativePath
            }}
        }}
        foreach ($relativePath in $sourceDirs.Keys) {{
            if (-not $destDirs.ContainsKey($relativePath)) {{
                $comparison.to_delete_dirs += $relativePath
            }}
        }}
    }}
    "Bidirectionnel (miroir)" {{
        # Fichiers à créer ou mettre à jour dans B
        foreach ($relativePath in $sourceFiles.Keys) {{
            $sourceFile = $sourceFiles[$relativePath]
            if ($destFiles.ContainsKey($relativePath)) {{
                $destFile = $destFiles[$relativePath]
                if ($sourceFile.LastWriteTime -gt $destFile.LastWriteTime) {{
                    $comparison.to_update += $relativePath
                }}
            }} else {{
                $comparison.to_create += $relativePath
            }}
        }}

        # Dossiers à créer dans B
        foreach ($relativePath in $sourceDirs.Keys) {{
            if (-not $destDirs.ContainsKey($relativePath)) {{
                $comparison.to_create_dirs += $relativePath
            }}
        }}

        # Fichiers à créer ou mettre à jour dans A
        foreach ($relativePath in $destFiles.Keys) {{
            $destFile = $destFiles[$relativePath]
            if ($sourceFiles.ContainsKey($relativePath)) {{
                $sourceFile = $sourceFiles[$relativePath]
                if ($destFile.LastWriteTime -gt $sourceFile.LastWriteTime) {{
                    $comparison.to_create_reverse += $relativePath
                }}
            }} else {{
                $comparison.to_create_reverse += $relativePath
            }}
        }}

        # Dossiers à créer dans A
        foreach ($relativePath in $destDirs.Keys) {{
            if (-not $sourceDirs.ContainsKey($relativePath)) {{
                $comparison.to_create_dirs_reverse += $relativePath
            }}
        }}
    }}
}}

# Sauvegarder les résultats
$comparison | ConvertTo-Json | Set-Content -Path "{output_file}"
""")

        # Exécuter le script PowerShell
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as file:
                    comparison_result = json.load(file)

                # Nettoyage du script temporaire
                os.remove(ps_script)

                # Création de la synthèse
                logger.info("SYNTHÈSE DE LA COMPARAISON :")
                logger.info(
                    f"Nombre de fichiers à créer : {len(comparison_result.get('to_create', []))}"
                )
                if comparison_result.get('to_create'):
                    logger.info("Fichiers à créer :")
                    for file in comparison_result['to_create']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à mettre à jour : {len(comparison_result.get('to_update', []))}"
                )
                if comparison_result.get('to_update'):
                    logger.info("Fichiers à mettre à jour :")
                    for file in comparison_result['to_update']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à supprimer : {len(comparison_result.get('to_delete', []))}"
                )
                if comparison_result.get('to_delete'):
                    logger.info("Fichiers à supprimer :")
                    for file in comparison_result['to_delete']:
                        logger.info(f"  - {file}")

                logger.info(
                    f"Nombre de fichiers à créer en sens inverse : {len(comparison_result.get('to_create_reverse', []))}"
                )
                if comparison_result.get('to_create_reverse'):
                    logger.info("Fichiers à créer en sens inverse :")
                    for file in comparison_result['to_create_reverse']:
                        logger.info(f"  - {file}")

                logger.info("=" * 80)
                logger.info("COMPARAISON TERMINÉE AVEC SUCCÈS")
                logger.info("=" * 80)

                return render_template(
                    'index.html',
                    comparison_result=comparison_result,
                    source_dir=source_dir,
                    dest_dir=dest_dir,
                    mode=mode,
                    success="Comparaison effectuée avec succès")
            except json.JSONDecodeError as e:
                logger.error("ERREUR DE LECTURE DES RÉSULTATS :")
                logger.error(
                    f"Erreur lors de la lecture du fichier JSON : {str(e)}")
                logger.error("-" * 80)
                return render_template(
                    'index.html',
                    error="Erreur lors de la lecture des résultats",
                    source_dir=source_dir,
                    dest_dir=dest_dir,
                    mode=mode)
        else:
            error_msg = result.stderr or "Erreur inconnue lors de la comparaison"
            logger.error("ERREUR DE COMPARAISON :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error("ERREUR INATTENDUE :")
        logger.error(f"Erreur lors de la comparaison : {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("-" * 80)
        return render_template(
            'index.html',
            error=str(e),
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


@app.route('/sync_folders', methods=['POST'])
def sync_folders():
    """
    Synchronise les dossiers selon les différences trouvées.
    """
    try:
        source_dir = request.form['source_dir']
        dest_dir = request.form['dest_dir']
        mode = request.form['mode']
        files_to_create = request.form.get('files_to_create', '')
        files_to_update = request.form.get('files_to_update', '')
        files_to_delete = request.form.get('files_to_delete', '')
        files_to_create_reverse = request.form.get('files_to_create_reverse',
                                                   '')
        dirs_to_create = request.form.get('to_create_dirs', '')
        dirs_to_delete = request.form.get('to_delete_dirs', '')
        dirs_to_create_reverse = request.form.get('to_create_dirs_reverse', '')

        logger.info("=" * 80)
        logger.info("DÉBUT DE LA SYNCHRONISATION")
        logger.info("=" * 80)
        logger.info(f"Source      : {source_dir}")
        logger.info(f"Destination : {dest_dir}")
        logger.info(f"Mode        : {mode}")
        logger.info("-" * 80)

        # Conversion des listes
        files_to_create_list = files_to_create.split(
            ',') if files_to_create else []
        files_to_update_list = files_to_update.split(
            ',') if files_to_update else []
        files_to_delete_list = files_to_delete.split(
            ',') if files_to_delete else []
        files_to_create_reverse_list = files_to_create_reverse.split(
            ',') if files_to_create_reverse else []
        dirs_to_create_list = dirs_to_create.split(
            ',') if dirs_to_create else []
        dirs_to_delete_list = dirs_to_delete.split(
            ',') if dirs_to_delete else []
        dirs_to_create_reverse_list = dirs_to_create_reverse.split(
            ',') if dirs_to_create_reverse else []

        # Affichage de la synthèse
        logger.info("ACTIONS À EFFECTUER :")

        if dirs_to_create_list:
            logger.info(f"Dossiers à créer ({len(dirs_to_create_list)}) :")
            for dir_path in dirs_to_create_list:
                logger.info(f"  - {dir_path}")

        if files_to_create_list:
            logger.info(f"Fichiers à créer ({len(files_to_create_list)}) :")
            for file in files_to_create_list:
                logger.info(f"  - {file}")

        if files_to_update_list:
            logger.info(
                f"Fichiers à mettre à jour ({len(files_to_update_list)}) :")
            for file in files_to_update_list:
                logger.info(f"  - {file}")

        if dirs_to_delete_list:
            logger.info(f"Dossiers à supprimer ({len(dirs_to_delete_list)}) :")
            for dir_path in dirs_to_delete_list:
                logger.info(f"  - {dir_path}")

        if files_to_delete_list:
            logger.info(
                f"Fichiers à supprimer ({len(files_to_delete_list)}) :")
            for file in files_to_delete_list:
                logger.info(f"  - {file}")

        if dirs_to_create_reverse_list:
            logger.info(
                f"Dossiers à créer en sens inverse ({len(dirs_to_create_reverse_list)}) :"
            )
            for dir_path in dirs_to_create_reverse_list:
                logger.info(f"  - {dir_path}")

        if files_to_create_reverse_list:
            logger.info(
                f"Fichiers à créer en sens inverse ({len(files_to_create_reverse_list)}) :"
            )
            for file in files_to_create_reverse_list:
                logger.info(f"  - {file}")

        logger.info("-" * 80)

        # Création d'un script PowerShell temporaire pour la synchronisation
        ps_script = os.path.join(SCRIPT_DIR, 'sync_folders.ps1')
        with open(ps_script, 'w', encoding='utf-8') as f:
            f.write(f"""
$ErrorActionPreference = "Stop"
$source = "{source_dir}"
$dest = "{dest_dir}"

# Fonction pour créer les dossiers parents si nécessaire
function EnsureParentDirectory($path) {{
    $parent = Split-Path -Parent $path
    if (-not (Test-Path $parent)) {{
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }}
}}

# Créer les nouveaux dossiers
$dirsToCreate = @({','.join([f'"{d}"' for d in dirs_to_create_list])})
foreach ($dir in $dirsToCreate) {{
    $destPath = Join-Path $dest $dir
    if (-not (Test-Path $destPath)) {{
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        Write-Host "Dossier créé: $dir"
    }}
}}

# Créer les nouveaux fichiers
$filesToCreate = @({','.join([f'"{f}"' for f in files_to_create_list])})
foreach ($file in $filesToCreate) {{
    $sourcePath = Join-Path $source $file
    $destPath = Join-Path $dest $file
    EnsureParentDirectory $destPath
    Copy-Item -Path $sourcePath -Destination $destPath -Force
    Write-Host "Fichier créé: $file"
}}

# Mettre à jour les fichiers existants
$filesToUpdate = @({','.join([f'"{f}"' for f in files_to_update_list])})
foreach ($file in $filesToUpdate) {{
    $sourcePath = Join-Path $source $file
    $destPath = Join-Path $dest $file
    Copy-Item -Path $sourcePath -Destination $destPath -Force
    Write-Host "Fichier mis à jour: $file"
}}

# Supprimer les fichiers
$filesToDelete = @({','.join([f'"{f}"' for f in files_to_delete_list])})
foreach ($file in $filesToDelete) {{
    $path = Join-Path $dest $file
    if (Test-Path $path) {{
        Remove-Item -Path $path -Force
        Write-Host "Fichier supprimé: $file"
    }}
}}

# Supprimer les dossiers (dans l'ordre inverse pour gérer les sous-dossiers)
$dirsToDelete = @({','.join([f'"{d}"' for d in dirs_to_delete_list])}) | Sort-Object -Descending
foreach ($dir in $dirsToDelete) {{
    $path = Join-Path $dest $dir
    if (Test-Path $path) {{
        Remove-Item -Path $path -Force -Recurse
        Write-Host "Dossier supprimé: $dir"
    }}
}}

# Créer les dossiers en sens inverse
$dirsToCreateReverse = @({','.join([f'"{d}"' for d in dirs_to_create_reverse_list])})
foreach ($dir in $dirsToCreateReverse) {{
    $sourcePath = Join-Path $dest $dir
    $destPath = Join-Path $source $dir
    if (-not (Test-Path $destPath)) {{
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        Write-Host "Dossier créé en sens inverse: $dir"
    }}
}}

# Créer les fichiers en sens inverse
$filesToCreateReverse = @({','.join([f'"{f}"' for f in files_to_create_reverse_list])})
foreach ($file in $filesToCreateReverse) {{
    $sourcePath = Join-Path $dest $file
    $destPath = Join-Path $source $file
    EnsureParentDirectory $destPath
    Copy-Item -Path $sourcePath -Destination $destPath -Force
    Write-Host "Fichier créé en sens inverse: $file"
}}
""")

        # Exécuter le script PowerShell
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script]
        logger.info("EXÉCUTION DE LA SYNCHRONISATION :")
        logger.info(f"Commande : {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Nettoyage du script temporaire
            os.remove(ps_script)

            logger.info("=" * 80)
            logger.info("SYNCHRONISATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 80)
            return redirect(url_for('compare_folders'),
                            code=307)  # Réutilise les données POST
        else:
            error_msg = result.stderr or "Erreur inconnue lors de la synchronisation"
            logger.error("ERREUR DE SYNCHRONISATION :")
            logger.error(error_msg)
            logger.error("-" * 80)
            return render_template('index.html',
                                   error=error_msg,
                                   source_dir=source_dir,
                                   dest_dir=dest_dir,
                                   mode=mode)
    except Exception as e:
        logger.error("ERREUR INATTENDUE :")
        logger.error(f"Erreur lors de la synchronisation : {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("-" * 80)
        return render_template(
            'index.html',
            error=str(e),
            source_dir=source_dir if 'source_dir' in locals() else '',
            dest_dir=dest_dir if 'dest_dir' in locals() else '',
            mode=mode if 'mode' in locals() else '')


if __name__ == '__main__':
    try:
        app.run(debug=True, port=5001)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application : {str(e)}")
