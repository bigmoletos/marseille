#!/bin/sh
set -e

echo "=== Initialisation de l'application de synchronisation ==="

# Création des répertoires de synchronisation s'ils n'existent pas déjà
echo "Création/vérification des répertoires..."
mkdir -p /sync/source
mkdir -p /sync/dest
mkdir -p /app/data
mkdir -p /app/logs

# Vérification des outils requis
echo "Vérification des dépendances..."
if command -v rsync >/dev/null 2>&1; then
    echo "✓ rsync est installé"
else
    echo "⨯ rsync n'est pas installé"
    exit 1
fi

if command -v jq >/dev/null 2>&1; then
    echo "✓ jq est installé"
else
    echo "⨯ jq n'est pas installé"
    exit 1
fi

# Nettoyage des fichiers temporaires et anciens logs au besoin
echo "Nettoyage des fichiers temporaires..."
find /app/data -name "temp_*.json" -mtime +1 -delete 2>/dev/null || true
find /app/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Définir les permissions uniquement pour les répertoires que nous contrôlons
if [ "$(id -u)" = "0" ]; then
    echo "Configuration des permissions (en tant que root)..."
    # Ne pas toucher aux dossiers /sync qui sont des volumes montés
    chmod -R 777 /app/data /app/logs
    echo "✓ Permissions configurées pour les dossiers de l'application"

    # Vérifier les permissions des dossiers de synchronisation
    echo "Vérification des permissions des dossiers de synchronisation..."
    if [ -w "/sync/source" ]; then
        echo "✓ Dossier source accessible en écriture"
    else
        echo "⚠️ Le dossier source est en lecture seule"
    fi

    if [ -w "/sync/dest" ]; then
        echo "✓ Dossier destination accessible en écriture"
    else
        echo "⚠️ Le dossier destination est en lecture seule"
    fi
else
    echo "⚠️ Exécution en tant qu'utilisateur non-privilégié"
fi

echo "=== Démarrage de l'application ==="
echo "Accédez à l'application sur http://localhost:5000"
exec "$@"