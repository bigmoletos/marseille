@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo Utilitaire de copie pour volumes Docker
echo ====================================================
echo.

REM Vérification si Docker est en cours d'exécution
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker ne semble pas en cours d'exécution.
    echo Veuillez démarrer Docker Desktop et réessayer.
    exit /b 1
)

:menu
echo Que souhaitez-vous faire?
echo 1. Copier des fichiers VERS le volume source
echo 2. Copier des fichiers VERS le volume destination
echo 3. Extraire des fichiers DEPUIS le volume source
echo 4. Extraire des fichiers DEPUIS le volume destination
echo 5. Quitter
echo.

set /p choix="Votre choix (1-5): "

if "%choix%"=="1" goto copy_to_source
if "%choix%"=="2" goto copy_to_dest
if "%choix%"=="3" goto extract_from_source
if "%choix%"=="4" goto extract_from_dest
if "%choix%"=="5" goto end

echo Choix invalide. Veuillez réessayer.
goto menu

:copy_to_source
echo.
echo == Copie vers le volume source ==
set /p chemin="Entrez le chemin du dossier à copier: "
echo Copie en cours...
docker run --rm -v sync-folders-source:/destination -v "%chemin%:/source" alpine sh -c "cp -r /source/* /destination/"
if %errorlevel% equ 0 (
    echo [SUCCÈS] Fichiers copiés vers le volume source.
) else (
    echo [ERREUR] La copie a échoué. Vérifiez le chemin et les permissions.
)
goto menu

:copy_to_dest
echo.
echo == Copie vers le volume destination ==
set /p chemin="Entrez le chemin du dossier à copier: "
echo Copie en cours...
docker run --rm -v sync-folders-dest:/destination -v "%chemin%:/source" alpine sh -c "cp -r /source/* /destination/"
if %errorlevel% equ 0 (
    echo [SUCCÈS] Fichiers copiés vers le volume destination.
) else (
    echo [ERREUR] La copie a échoué. Vérifiez le chemin et les permissions.
)
goto menu

:extract_from_source
echo.
echo == Extraction depuis le volume source ==
set /p chemin="Entrez le chemin où extraire les fichiers: "
echo Extraction en cours...
docker run --rm -v sync-folders-source:/source -v "%chemin%:/destination" alpine sh -c "cp -r /source/* /destination/"
if %errorlevel% equ 0 (
    echo [SUCCÈS] Fichiers extraits depuis le volume source.
) else (
    echo [ERREUR] L'extraction a échoué. Vérifiez le chemin et les permissions.
)
goto menu

:extract_from_dest
echo.
echo == Extraction depuis le volume destination ==
set /p chemin="Entrez le chemin où extraire les fichiers: "
echo Extraction en cours...
docker run --rm -v sync-folders-dest:/source -v "%chemin%:/destination" alpine sh -c "cp -r /source/* /destination/"
if %errorlevel% equ 0 (
    echo [SUCCÈS] Fichiers extraits depuis le volume destination.
) else (
    echo [ERREUR] L'extraction a échoué. Vérifiez le chemin et les permissions.
)
goto menu

:end
echo Au revoir!
exit /b 0