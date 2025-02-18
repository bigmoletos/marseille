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
        echo "$path" | sed 's/\\/\//g' | sed 's/^\([A-Za-z]\):/\/mnt\/\L\1/'
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
    if [ ! -e "$source_dir" ] || [ ! -e "$dest_dir" ]; then
        echo '{"error": "Un des dossiers n existe pas"}' > "$output_file"
        return 1
    fi

    # Initialisation des listes
    declare -a to_create to_update to_delete to_create_reverse

    case "$mode" in
        "A vers B (sauvegarde)")
            log "Mode de comparaison: A vers B (sauvegarde)"
            # Utiliser rsync en mode dry-run pour voir ce qui serait copié/supprimé
            rsync_output=$(rsync -ain --delete "$source_dir/" "$dest_dir/" 2>&1)

            # Analyser la sortie de rsync
            while IFS= read -r line; do
                # Utiliser des expressions régulières plus robustes
                if [[ "$line" =~ ^\>f.* ]]; then
                    # Nouveau fichier à créer
                    file=${line:12}
                    to_create+=("$file")
                elif [[ "$line" =~ ^cf.* ]]; then
                    # Fichier à mettre à jour
                    file=${line:12}
                    to_update+=("$file")
                elif [[ "$line" =~ ^\*deleting.* ]]; then
                    # Fichier à supprimer
                    file=${line:10}
                    to_delete+=("$file")
                fi
            done <<< "$rsync_output"
            ;;

        "B vers A (restauration)")
            log "Mode de comparaison: B vers A (restauration)"
            # Utiliser rsync en mode dry-run pour voir ce qui serait copié/supprimé
            rsync_output=$(rsync -ain --delete "$dest_dir/" "$source_dir/" 2>&1)

            # Analyser la sortie de rsync
            while IFS= read -r line; do
                if [[ "$line" =~ ^\>f.* ]]; then
                    # Nouveau fichier à créer dans A
                    file=${line:12}
                    to_create_reverse+=("$file")
                elif [[ "$line" =~ ^cf.* ]]; then
                    # Fichier à mettre à jour dans A
                    file=${line:12}
                    to_create_reverse+=("$file")
                elif [[ "$line" =~ ^\*deleting.* ]]; then
                    # Fichier à supprimer dans A
                    file=${line:10}
                    to_delete+=("$file")
                fi
            done <<< "$rsync_output"
            ;;

        "Bidirectionnel (miroir)")
            log "Mode de comparaison: Bidirectionnel (miroir)"
            # Vérifier les changements de A vers B
            rsync_output_ab=$(rsync -ain "$source_dir/" "$dest_dir/" 2>&1)

            # Analyser la sortie de rsync pour A vers B
            while IFS= read -r line; do
                if [[ "$line" =~ ^\>f.* ]]; then
                    # Nouveau fichier à créer dans B
                    file=${line:12}
                    to_create+=("$file")
                elif [[ "$line" =~ ^cf.* ]]; then
                    # Fichier à mettre à jour dans B
                    file=${line:12}
                    to_update+=("$file")
                fi
            done <<< "$rsync_output_ab"

            # Vérifier les changements de B vers A
            rsync_output_ba=$(rsync -ain "$dest_dir/" "$source_dir/" 2>&1)

            # Analyser la sortie de rsync pour B vers A
            while IFS= read -r line; do
                if [[ "$line" =~ ^\>f.* ]]; then
                    # Nouveau fichier à créer dans A
                    file=${line:12}
                    to_create_reverse+=("$file")
                elif [[ "$line" =~ ^cf.* ]]; then
                    # Fichier à mettre à jour dans A
                    file=${line:12}
                    to_create_reverse+=("$file")
                fi
            done <<< "$rsync_output_ba"
            ;;
    esac

    # Log des résultats
    log "=== Résultats de la comparaison ==="
    log "Fichiers à créer: ${to_create[*]}"
    log "Fichiers à mettre à jour: ${to_update[*]}"
    log "Fichiers à supprimer: ${to_delete[*]}"
    log "Fichiers à créer en sens inverse: ${to_create_reverse[*]}"

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

    return 0
}

# Fonction pour synchroniser les dossiers
sync_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local mode="$3"

    log "=== DÉBUT DE LA SYNCHRONISATION ==="
    log "Mode: $mode"
    log "Source: $1 -> $source_dir"
    log "Destination: $2 -> $dest_dir"

    case "$mode" in
        "A vers B (sauvegarde)")
            log "Synchronisation A vers B"
            rsync -av --delete "$source_dir/" "$dest_dir/"
            ;;
        "B vers A (restauration)")
            log "Synchronisation B vers A"
            rsync -av --delete "$dest_dir/" "$source_dir/"
            ;;
        "Bidirectionnel (miroir)")
            log "Synchronisation bidirectionnelle"
            # Synchroniser A vers B sans suppression
            rsync -av "$source_dir/" "$dest_dir/"
            # Synchroniser B vers A sans suppression
            rsync -av "$dest_dir/" "$source_dir/"
            ;;
    esac

    log "=== SYNCHRONISATION TERMINÉE ==="
    return 0
}

# Point d'entrée principal
case "$1" in
    "compare")
        compare_folders "$2" "$3" "$4" "$5"
        ;;
    "sync")
        sync_folders "$2" "$3" "$4"
        ;;
    *)
        echo "Usage: $0 {compare|sync} [arguments]"
        exit 1
        ;;
esac
