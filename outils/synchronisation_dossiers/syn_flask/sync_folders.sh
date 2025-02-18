#!/bin/bash

# Fonction pour convertir les chemins Windows en chemins Unix
convert_path() {
    local path="$1"

    # Si le chemin commence par S: ou s:, utiliser directement /mnt/s
    if [[ "$path" =~ ^[Ss]: ]]; then
        # Supprimer le S: initial et convertir les backslashes en slashes
        echo "/mnt/s/${path:2}" | sed 's/\\/\//g'
    else
        # Pour les autres chemins, conversion standard
        echo "$path" | sed 's/\\/\//g' | sed 's/^\([A-Za-z]\):/\/\1/'
    fi
}

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> sync.log
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Fonction pour afficher une barre de progression
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local progress=$((current * width / total))
    local percentage=$((current * 100 / total))

    # Création de la barre de progression
    local bar="["
    for ((i=0; i<width; i++)); do
        if [ $i -lt $progress ]; then
            bar+="="
        else
            bar+=" "
        fi
    done
    bar+="] $percentage%"

    # Affichage de la progression
    local message="$bar ($current/$total)"
    log "$message"
}

# Fonction pour compter le nombre total de fichiers à traiter
count_total_files() {
    local files_to_create="$1"
    local files_to_update="$2"
    local files_to_delete="$3"
    local files_to_create_reverse="$4"

    local count=0

    # Compter les fichiers à créer
    IFS=',' read -ra create_array <<< "$files_to_create"
    count=$((count + ${#create_array[@]}))

    # Compter les fichiers à mettre à jour
    IFS=',' read -ra update_array <<< "$files_to_update"
    count=$((count + ${#update_array[@]}))

    # Compter les fichiers à supprimer
    IFS=',' read -ra delete_array <<< "$files_to_delete"
    count=$((count + ${#delete_array[@]}))

    # Compter les fichiers à créer en sens inverse
    IFS=',' read -ra create_reverse_array <<< "$files_to_create_reverse"
    count=$((count + ${#create_reverse_array[@]}))

    echo $count
}

# Vérification de la présence de rsync
check_rsync() {
    if command -v rsync &> /dev/null; then
        log "Utilisation de rsync système"
        return 0
    else
        log "ERREUR: rsync n'est pas trouvé"
        cat > "$1" << EOF
{
    "error": "rsync n'est pas trouvé dans le conteneur."
}
EOF
        return 1
    fi
}

# Fonction pour afficher le contenu d'un tableau
log_array() {
    local array_name=$1
    local array_content=("${!2}")
    log "Contenu du tableau $array_name :"
    for item in "${array_content[@]}"; do
        log "  - $item"
    done
}

# Fonction pour vérifier l'existence d'un chemin
check_path() {
    local path="$1"
    local description="$2"

    if [ ! -e "$path" ]; then
        log "ERREUR: $description n'existe pas: $path"
        return 1
    fi
    return 0
}

# Fonction pour comparer les dossiers
compare_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local mode="$3"
    local output_file=$(convert_path "$4")

    log "=== DÉBUT DE LA COMPARAISON ==="
    log "Mode: $mode"
    log "Source: $1 -> $source_dir"
    log "Destination: $2 -> $dest_dir"
    log "Fichier de sortie: $4 -> $output_file"

    # Vérification des dossiers
    if ! check_path "$source_dir" "Dossier source" || ! check_path "$dest_dir" "Dossier destination"; then
        echo '{"error": "Un des dossiers n existe pas"}' > "$output_file"
        return 1
    fi

    # Initialisation des listes
    declare -a to_create to_update to_delete to_create_reverse

    # Fonction pour filtrer et ajouter les fichiers non vides à un tableau
    add_to_array() {
        local file="$1"
        local array_name="$2"
        if [ ! -z "$file" ] && [ "$file" != " " ]; then
            log "Ajout du fichier au tableau $array_name: '$file'"
            eval "$array_name+=(\"$file\")"
        else
            log "Fichier vide ignoré"
        fi
    }

    # Fonction pour exécuter rsync et logger les détails
    run_rsync() {
        local src="$1"
        local dst="$2"
        local description="$3"

        log "=== Exécution de rsync ($description) ==="
        log "Source: $src"
        log "Destination: $dst"

        # Exécute rsync avec plus de verbosité
        local rsync_cmd="rsync -n -av --delete --itemize-changes \"$src/\" \"$dst\""
        log "Commande rsync: $rsync_cmd"

        local output
        output=$(eval $rsync_cmd 2>&1)
        log "Sortie complète de rsync:"
        log "$output"

        echo "$output"
    }

    # Comparaison selon le mode
    case "$mode" in
        "A vers B (sauvegarde)")
            log "Mode de comparaison: A vers B (sauvegarde)"

            # Capture la sortie de rsync
            local rsync_output
            rsync_output=$(run_rsync "$source_dir" "$dest_dir" "A vers B")

            # Traitement des fichiers à créer
            log "Analyse des fichiers à créer..."
            while IFS= read -r file; do
                add_to_array "$file" "to_create"
            done < <(echo "$rsync_output" | awk '$1 ~ /^>/ {print $2}' | grep -v '^$')

            # Traitement des fichiers à mettre à jour
            log "Analyse des fichiers à mettre à jour..."
            while IFS= read -r file; do
                add_to_array "$file" "to_update"
            done < <(echo "$rsync_output" | awk '$1 ~ /^.*t......$/ {print $2}' | grep -v '^$')
            ;;

        "B vers A (restauration)")
            log "Mode de comparaison: B vers A (restauration)"

            # Capture la sortie de rsync
            local rsync_output
            rsync_output=$(run_rsync "$dest_dir" "$source_dir" "B vers A")

            # Traitement des fichiers à supprimer
            log "Analyse des fichiers à supprimer..."
            while IFS= read -r file; do
                add_to_array "$file" "to_delete"
            done < <(echo "$rsync_output" | awk '$1 ~ /^>/ {print $2}' | grep -v '^$')
            ;;

        "Bidirectionnel (miroir)")
            log "Mode de comparaison: Bidirectionnel (miroir)"

            # Capture la sortie de rsync pour A vers B
            local rsync_output_ab
            rsync_output_ab=$(run_rsync "$source_dir" "$dest_dir" "A vers B (miroir)")

            # Traitement des fichiers à créer dans B
            log "Analyse des fichiers à créer dans B..."
            while IFS= read -r file; do
                add_to_array "$file" "to_create"
            done < <(echo "$rsync_output_ab" | awk '$1 ~ /^>/ {print $2}' | grep -v '^$')

            # Traitement des fichiers à mettre à jour
            log "Analyse des fichiers à mettre à jour..."
            while IFS= read -r file; do
                add_to_array "$file" "to_update"
            done < <(echo "$rsync_output_ab" | awk '$1 ~ /^.*t......$/ {print $2}' | grep -v '^$')

            # Capture la sortie de rsync pour B vers A
            local rsync_output_ba
            rsync_output_ba=$(run_rsync "$dest_dir" "$source_dir" "B vers A (miroir)")

            # Traitement des fichiers à créer dans A
            log "Analyse des fichiers à créer dans A..."
            while IFS= read -r file; do
                add_to_array "$file" "to_create_reverse"
            done < <(echo "$rsync_output_ba" | awk '$1 ~ /^>/ {print $2}' | grep -v '^$')
            ;;
    esac

    # Log des résultats avant création du JSON
    log "=== Résultats de la comparaison ==="
    log "Nombre de fichiers à créer: ${#to_create[@]}"
    log "Nombre de fichiers à mettre à jour: ${#to_update[@]}"
    log "Nombre de fichiers à supprimer: ${#to_delete[@]}"
    log "Nombre de fichiers à créer en sens inverse: ${#to_create_reverse[@]}"

    log_array "to_create" "to_create[@]"
    log_array "to_update" "to_update[@]"
    log_array "to_delete" "to_delete[@]"
    log_array "to_create_reverse" "to_create_reverse[@]"

    # Création du JSON de résultat
    log "Création du fichier JSON de résultat: $output_file"

    # Fonction pour formater un tableau en JSON
    format_array_json() {
        local array_name=$1
        local array_content=("${!2}")
        local result=""

        for item in "${array_content[@]}"; do
            if [ ! -z "$item" ]; then
                result+="\"$item\","
            fi
        done
        result=${result%,}  # Supprime la dernière virgule
        echo "[$result]"
    }

    {
        echo "{"
        echo "  \"to_create\": $(format_array_json "to_create" "to_create[@]"), "
        echo "  \"to_update\": $(format_array_json "to_update" "to_update[@]"), "
        echo "  \"to_delete\": $(format_array_json "to_delete" "to_delete[@]"), "
        echo "  \"to_create_reverse\": $(format_array_json "to_create_reverse" "to_create_reverse[@]"), "
        echo "  \"error\": null"
        echo "}"
    } > "$output_file"

    log "=== Fin de la comparaison des dossiers ==="
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

    log "=== DÉBUT DE LA SYNCHRONISATION ==="
    log "Source: $1 -> $source_dir"
    log "Destination: $2 -> $dest_dir"

    # Vérification des dossiers
    if ! check_path "$source_dir" "Dossier source" || ! check_path "$dest_dir" "Dossier destination"; then
        log "ERREUR: Impossible de continuer la synchronisation - dossiers manquants"
        return 1
    fi

    # Calculer le nombre total de fichiers à traiter
    local total_files=$(count_total_files "$files_to_create" "$files_to_update" "$files_to_delete" "$files_to_create_reverse")
    local current_file=0

    log "Nombre total de fichiers à traiter : $total_files"
    show_progress $current_file $total_files

    # Création/Mise à jour des fichiers
    log "=== CRÉATION DES FICHIERS ==="
    IFS=',' read -ra create_array <<< "$files_to_create"
    for file in "${create_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        local dest_path="$dest_dir/$file"
        local source_path="$source_dir/$file"

        log "Création: $file"
        log "De: $source_path"
        log "Vers: $dest_path"

        mkdir -p "$(dirname "$dest_path")"
        if cp -p "$source_path" "$dest_path"; then
            log "✓ Créé avec succès"
        else
            log "✗ Erreur lors de la création"
        fi
        current_file=$((current_file + 1))
        show_progress $current_file $total_files
    done

    log "=== MISE À JOUR DES FICHIERS ==="
    IFS=',' read -ra update_array <<< "$files_to_update"
    for file in "${update_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        local dest_path="$dest_dir/$file"
        local source_path="$source_dir/$file"

        log "Mise à jour: $file"
        log "De: $source_path"
        log "Vers: $dest_path"

        if cp -p "$source_path" "$dest_path"; then
            log "✓ Mis à jour avec succès"
        else
            log "✗ Erreur lors de la mise à jour"
        fi
        current_file=$((current_file + 1))
        show_progress $current_file $total_files
    done

    log "=== SUPPRESSION DES FICHIERS ==="
    IFS=',' read -ra delete_array <<< "$files_to_delete"
    for file in "${delete_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        local source_path="$source_dir/$file"

        log "Suppression: $file"
        log "Chemin: $source_path"

        if rm -f "$source_path"; then
            log "✓ Supprimé avec succès"
        else
            log "✗ Erreur lors de la suppression"
        fi
        current_file=$((current_file + 1))
        show_progress $current_file $total_files
    done

    log "=== CRÉATION DES FICHIERS EN SENS INVERSE ==="
    IFS=',' read -ra create_reverse_array <<< "$files_to_create_reverse"
    for file in "${create_reverse_array[@]}"; do
        file=$(echo "$file" | tr -d '"')
        local dest_path="$dest_dir/$file"
        local source_path="$source_dir/$file"

        log "Création inverse: $file"
        log "De: $dest_path"
        log "Vers: $source_path"

        mkdir -p "$(dirname "$source_path")"
        if cp -p "$dest_path" "$source_path"; then
            log "✓ Créé avec succès"
        else
            log "✗ Erreur lors de la création"
        fi
        current_file=$((current_file + 1))
        show_progress $current_file $total_files
    done

    log "=== SYNCHRONISATION TERMINÉE ==="
    show_progress $total_files $total_files
    return 0
}

# Point d'entrée principal
case "$1" in
    "compare")
        # Vérifier rsync avant de continuer
        check_rsync "$5" || exit 1
        compare_folders "$2" "$3" "$4" "$5"
        ;;
    "sync")
        # Vérifier rsync avant de continuer
        check_rsync "$5" || exit 1
        sync_folders "$2" "$3" "$4" "$5" "$6" "$7"
        ;;
    *)
        echo "Usage: $0 {compare|sync} [arguments]"
        exit 1
        ;;
esac
