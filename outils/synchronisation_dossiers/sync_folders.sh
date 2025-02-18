#!/bin/bash

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> sync.log
}

# Fonction pour convertir les chemins Windows en chemins Unix
convert_path() {
    echo "$1" | sed 's/\\/\//g' | sed 's/^\([A-Za-z]\):/\/\1/'
}

# Fonction pour comparer les dossiers
compare_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local mode="$3"
    local output_file=$(convert_path "$4")

    log "Début de la comparaison - Mode: $mode"
    log "Source: $source_dir"
    log "Destination: $dest_dir"

    # Vérification des dossiers
    if [ ! -d "$source_dir" ] || [ ! -d "$dest_dir" ]; then
        log "ERREUR: Un des dossiers n'existe pas"
        echo '{"error": "Un des dossiers n existe pas"}' > "$output_file"
        return 1
    fi

    # Initialisation des listes
    declare -a to_create to_update to_delete to_create_reverse

    # Comparaison selon le mode
    case "$mode" in
        "A vers B (sauvegarde)")
            log "Comparaison A vers B"
            rsync -n -av --delete "$source_dir/" "$dest_dir" --out-format="%i %n" | awk '$1 ~ /^>/ {print $2}' | while read -r file; do
                log "À créer: $file"
                to_create+=("$file")
            done
            rsync -n -av --delete "$source_dir/" "$dest_dir" --out-format="%i %n" | awk '$1 ~ /^.*t......$/ {print $2}' | while read -r file; do
                log "À mettre à jour: $file"
                to_update+=("$file")
            done
            ;;

        "B vers A (restauration)")
            log "Comparaison B vers A"
            rsync -n -av --delete "$dest_dir/" "$source_dir" --out-format="%i %n" | awk '$1 ~ /^>/ {print $2}' | while read -r file; do
                log "À supprimer: $file"
                to_delete+=("$file")
            done
            ;;

        "Bidirectionnel (miroir)")
            log "Comparaison Bidirectionnel"
            rsync -n -av --delete "$source_dir/" "$dest_dir" --out-format="%i %n" | awk '$1 ~ /^>/ {print $2}' | while read -r file; do
                log "À créer dans B: $file"
                to_create+=("$file")
            done
            rsync -n -av --delete "$source_dir/" "$dest_dir" --out-format="%i %n" | awk '$1 ~ /^.*t......$/ {print $2}' | while read -r file; do
                log "À mettre à jour: $file"
                to_update+=("$file")
            done

            rsync -n -av --delete "$dest_dir/" "$source_dir" --out-format="%i %n" | awk '$1 ~ /^>/ {print $2}' | while read -r file; do
                log "À créer dans A: $file"
                to_create_reverse+=("$file")
            done
            ;;
    esac

    # Création du JSON de résultat
    {
        echo "{"
        echo "  \"to_create\": [$(printf '"%s",' "${to_create[@]}" | sed 's/,$//')], "
        echo "  \"to_update\": [$(printf '"%s",' "${to_update[@]}" | sed 's/,$//')], "
        echo "  \"to_delete\": [$(printf '"%s",' "${to_delete[@]}" | sed 's/,$//')], "
        echo "  \"to_create_reverse\": [$(printf '"%s",' "${to_create_reverse[@]}" | sed 's/,$//')], "
        echo "  \"error\": null"
        echo "}"
    } > "$output_file"

    log "Comparaison terminée"
    return 0
}

# Fonction pour synchroniser les dossiers
sync_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local files_to_create="$3"
    local files_to_update="$4"
    local files_to_delete="$5"
    local files_to_create_reverse="$6"

    log "Début de la synchronisation"

    # Création/Mise à jour des fichiers
    IFS=',' read -ra create_array <<< "$files_to_create"
    for file in "${create_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        mkdir -p "$(dirname "$dest_dir/$file")"
        cp -p "$source_dir/$file" "$dest_dir/$file"
        log "Créé: $file"
    done

    IFS=',' read -ra update_array <<< "$files_to_update"
    for file in "${update_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        cp -p "$source_dir/$file" "$dest_dir/$file"
        log "Mis à jour: $file"
    done

    # Suppression des fichiers
    IFS=',' read -ra delete_array <<< "$files_to_delete"
    for file in "${delete_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        rm -f "$source_dir/$file"
        log "Supprimé: $file"
    done

    # Création des fichiers en sens inverse en parallèle
    IFS=',' read -ra create_reverse_array <<< "$files_to_create_reverse"
    for file in "${create_reverse_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        mkdir -p "$(dirname "$source_dir/$file")"
        cp -p "$dest_dir/$file" "$source_dir/$file"
        log "Créé en sens inverse: $file"
    done

    log "Synchronisation terminée"
    return 0
}

# Point d'entrée principal
case "$1" in
    "compare")
        compare_folders "$2" "$3" "$4" "$5"
        ;;
    "sync")
        sync_folders "$2" "$3" "$4" "$5" "$6" "$7"
        ;;
    *)
        echo "Usage: $0 {compare|sync} [arguments]"
        exit 1
        ;;
esac
