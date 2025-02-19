#!/bin/bash

# Fonction pour convertir les chemins Windows en chemins Unix
convert_path() {
    local path="$1"

    # Si le chemin commence par S: ou s:, utiliser directement /mnt/s
    if [[ "$path" =~ ^[Ss]: ]]; then
        # Supprimer le S: initial et convertir les backslashes en slashes
        path=${path#[Ss]:}  # Supprime S: ou s: du début
        path=${path#/}      # Supprime le slash initial s'il existe
        path=${path#\\}     # Supprime le backslash initial s'il existe
        echo "/mnt/s/$path" | sed 's/\\/\//g'
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

# Fonction pour vérifier les dépendances
check_dependencies() {
    local output_file="$1"
    local missing_deps=()

    # Vérifier rsync
    if ! command -v rsync &> /dev/null; then
        missing_deps+=("rsync")
    fi

    # Vérifier jq
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "Installation des dépendances manquantes : ${missing_deps[*]}"
        if command -v apt-get &> /dev/null; then
            log "Installation via apt-get..."
            sudo apt-get update && sudo apt-get install -y "${missing_deps[@]}"
            if [ $? -eq 0 ]; then
                log "Dépendances installées avec succès"
                return 0
            else
                log "ERREUR: Impossible d'installer les dépendances"
                echo "{\"error\": \"Impossible d installer les dépendances\"}" > "$output_file"
                return 1
            fi
        else
            log "ERREUR: apt-get n'est pas disponible"
            echo "{\"error\": \"apt-get n est pas disponible pour installer les dépendances\"}" > "$output_file"
            return 1
        fi
    fi
    return 0
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

# Fonction pour nettoyer un chemin
clean_path() {
    local path="$1"
    # Supprimer ./ au début
    path="${path#./}"
    # Supprimer les slashes en fin de chemin
    path="${path%/}"
    # Supprimer les espaces au début et à la fin
    path="$(echo "$path" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    echo "$path"
}

# Fonction pour vérifier si un chemin est un sous-chemin d'un autre
is_subpath() {
    local path="$1"
    local array=("${!2}")

    for item in "${array[@]}"; do
        if [[ "$path" != "$item" && "$path" =~ ^"$item"/ ]]; then
            return 0
        fi
    done
    return 1
}

# Fonction pour ajouter un chemin à un tableau sans redondance
add_to_array() {
    local path="$1"
    local array_name="$2"
    local -n array="$array_name"  # référence au tableau

    path=$(clean_path "$path")

    # Ne pas ajouter si c'est un sous-chemin d'un élément existant
    if ! is_subpath "$path" array[@]; then
        # Supprimer les éléments qui sont des sous-chemins du nouveau chemin
        local new_array=()
        for item in "${array[@]}"; do
            if ! [[ "$item" != "$path" && "$item" =~ ^"$path"/ ]]; then
                new_array+=("$item")
            fi
        done
        array=("${new_array[@]}")

        # Ajouter le nouveau chemin s'il n'existe pas déjà
        if [[ ! " ${array[@]} " =~ " ${path} " ]]; then
            array+=("$path")
        fi
    fi
}

# Fonction pour générer un JSON d'un dossier
generate_folder_json() {
    local dir="$1"
    local temp_json=$(mktemp)
    local folders=()
    local files=()

    # Parcourir le dossier
    while IFS= read -r -d '' entry; do
        if [ -d "$entry" ]; then
            # C'est un dossier
            local folder_name=$(basename "$entry")
            local folder_date=$(date -r "$entry" +%Y%m%d%H%M%S)
            # Échapper les caractères spéciaux dans le nom du dossier
            folder_name=$(echo "$folder_name" | sed 's/"/\\"/g')
            folders+=("{\"name\":\"$folder_name\",\"date\":\"$folder_date\"}")
        elif [ -f "$entry" ]; then
            # C'est un fichier
            local file_name=$(basename "$entry")
            local file_date=$(date -r "$entry" +%Y%m%d%H%M%S)
            local file_size=$(stat -c%s "$entry")
            # Échapper les caractères spéciaux dans le nom du fichier
            file_name=$(echo "$file_name" | sed 's/"/\\"/g')
            files+=("{\"name\":\"$file_name\",\"date\":\"$file_date\",\"size\":\"$file_size\"}")
        fi
    done < <(find "$dir" -mindepth 1 -maxdepth 1 -print0)

    # Créer le JSON final avec des séparateurs de tableau corrects
    local folders_json=$(IFS=,; echo "${folders[*]}")
    local files_json=$(IFS=,; echo "${files[*]}")
    echo "{\"folders\":[$folders_json],\"files\":[$files_json]}" > "$temp_json"
    echo "$temp_json"
}

# Fonction pour comparer deux JSON et générer les listes
compare_json_folders() {
    local source_json="$1"
    local dest_json="$2"

    # Réinitialiser les compteurs et les tableaux
    declare -g nombre_to_create=0
    declare -g nombre_to_update=0
    declare -g nombre_to_delete=0
    declare -g nombre_to_bidirectionnel=0

    # Vider les tableaux globaux
    to_create=()
    to_update=()
    to_delete=()

    # Comparer les dossiers
    local source_folders=$(jq -r '.folders[].name' "$source_json")
    local dest_folders=$(jq -r '.folders[].name' "$dest_json")

    # Dossiers à créer (dans source mais pas dans dest)
    while IFS= read -r folder; do
        if [[ ! " ${dest_folders[@]} " =~ " ${folder} " ]]; then
            if [[ "$folder" =~ "Copie" ]]; then
                add_to_array "$folder" to_create
                ((nombre_to_create++))
            else
                # Vérifier que le dossier n'est pas déjà dans to_delete
                if [[ ! " ${to_delete[@]} " =~ " ${folder} " ]]; then
                    add_to_array "$folder" to_update
                    ((nombre_to_update++))
                fi
            fi
        else
            # Vérifier la date
            local source_date=$(jq -r ".folders[] | select(.name==\"$folder\") | .date" "$source_json")
            local dest_date=$(jq -r ".folders[] | select(.name==\"$folder\") | .date" "$dest_json")
            if [[ "${source_date//\"/}" != "${dest_date//\"/}" ]]; then
                if [[ "$folder" =~ "Copie" ]]; then
                    add_to_array "$folder" to_create
                    ((nombre_to_create++))
                else
                    # Vérifier que le dossier n'est pas déjà dans to_delete
                    if [[ ! " ${to_delete[@]} " =~ " ${folder} " ]]; then
                        add_to_array "$folder" to_update
                        ((nombre_to_update++))
                    fi
                fi
            fi
        fi
    done <<< "$source_folders"

    # Dossiers à supprimer (dans dest mais pas dans source)
    while IFS= read -r folder; do
        if [[ ! " ${source_folders[@]} " =~ " ${folder} " ]]; then
            # Vérifier que le dossier n'est pas déjà dans to_create ou to_update
            if [[ ! " ${to_create[@]} " =~ " ${folder} " ]] && [[ ! " ${to_update[@]} " =~ " ${folder} " ]]; then
                add_to_array "$folder" to_delete
                ((nombre_to_delete++))
            fi
        fi
    done <<< "$dest_folders"

    # Comparer les fichiers
    local source_files=$(jq -r '.files[].name' "$source_json")
    local dest_files=$(jq -r '.files[].name' "$dest_json")

    # Fichiers à créer (dans source mais pas dans dest)
    while IFS= read -r file; do
        if [[ ! " ${dest_files[@]} " =~ " ${file} " ]]; then
            # Vérifier que le fichier n'est pas déjà dans to_delete
            if [[ ! " ${to_delete[@]} " =~ " ${file} " ]]; then
                add_to_array "$file" to_create
                ((nombre_to_create++))
            fi
        else
            # Vérifier la taille et la date
            local source_size=$(jq -r ".files[] | select(.name==\"$file\") | .size" "$source_json")
            local dest_size=$(jq -r ".files[] | select(.name==\"$file\") | .size" "$dest_json")
            local source_date=$(jq -r ".files[] | select(.name==\"$file\") | .date" "$source_json")
            local dest_date=$(jq -r ".files[] | select(.name==\"$file\") | .date" "$dest_json")

            if [[ "${source_size//\"/}" != "${dest_size//\"/}" ]] || [[ "${source_date//\"/}" != "${dest_date//\"/}" ]]; then
                # Vérifier que le fichier n'est pas déjà dans to_delete
                if [[ ! " ${to_delete[@]} " =~ " ${file} " ]]; then
                    if [[ "$file" == "sync_manifest.json" ]]; then
                        add_to_array "$file" to_create
                        ((nombre_to_create++))
                    else
                        add_to_array "$file" to_update
                        ((nombre_to_update++))
                    fi
                fi
            fi
        fi
    done <<< "$source_files"

    # Fichiers à supprimer (dans dest mais pas dans source)
    while IFS= read -r file; do
        if [[ ! " ${source_files[@]} " =~ " ${file} " ]]; then
            # Vérifier que le fichier n'est pas déjà dans to_create ou to_update
            if [[ ! " ${to_create[@]} " =~ " ${file} " ]] && [[ ! " ${to_update[@]} " =~ " ${file} " ]]; then
                add_to_array "$file" to_delete
                ((nombre_to_delete++))
            fi
        fi
    done <<< "$dest_files"
}

# Fonction pour comparer les dossiers
compare_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local mode="$3"
    local output_file="$4"

    log "=== DÉBUT DE LA COMPARAISON ==="
    log "Mode: $mode"
    log "Source: $1 -> $source_dir"
    log "Destination: $2 -> $dest_dir"
    log "Fichier de sortie: $4 -> $output_file"

    # Vérification des dépendances
    check_dependencies "$output_file" || return 1

    # Vérification des dossiers
    if [ ! -e "$source_dir" ] || [ ! -e "$dest_dir" ]; then
        echo '{"error": "Un des dossiers n existe pas"}' > "$output_file"
        return 1
    fi

    # Initialisation des listes
    declare -a to_create to_update to_delete to_create_reverse

    # Fonction pour formater un tableau en JSON
    array_to_json() {
        local array=("$@")
        local result=""
        local first=true

        echo -n "["
        for item in "${array[@]}"; do
            if [ -n "$item" ]; then
                if [ "$first" = true ]; then
                    first=false
                else
                    echo -n ","
                fi
                echo -n "\"$item\""
            fi
        done
        echo "]"
    }

    case "$mode" in
        "A vers B")
            log "Mode de comparaison: A vers B (sauvegarde)"

            # Générer les JSON pour les deux dossiers
            source_json=$(generate_folder_json "$source_dir")
            dest_json=$(generate_folder_json "$dest_dir")

            # Comparer les dossiers
            compare_json_folders "$source_json" "$dest_json"

            # Créer le JSON de résultat
            {
                echo -n "{"
                echo -n "\"to_create\": $(array_to_json "${to_create[@]}"),"
                echo -n "\"to_update\": $(array_to_json "${to_update[@]}"),"
                echo -n "\"to_delete\": $(array_to_json "${to_delete[@]}"),"
                echo -n "\"to_bidirectionnel\": [],"
                echo -n "\"nombre_to_create\": $nombre_to_create,"
                echo -n "\"nombre_to_update\": $nombre_to_update,"
                echo -n "\"nombre_to_delete\": $nombre_to_delete,"
                echo -n "\"nombre_to_bidirectionnel\": 0,"
                echo "\"error\": null}"
            } > "$output_file"

            # Nettoyer les fichiers temporaires
            rm -f "$source_json" "$dest_json"
            ;;

        "B vers A")
            log "Mode de comparaison: B vers A (restauration)"

            # Utiliser rsync en mode dry-run pour comparer les fichiers
            temp_file=$(mktemp)
            rsync -ain --delete "$dest_dir/" "$source_dir/" > "$temp_file" 2>&1
            rsync_status=$?

            # Vérifier si rsync a réussi
            if [ $rsync_status -ne 0 ]; then
                log "ERREUR: rsync a échoué avec le code $rsync_status"
                log "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log "Analyse des différences..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log "Nouveau fichier/dossier à créer en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "cf"|"cd")
                        log "Fichier/dossier à mettre à jour en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "*d"|"*f")
                        log "Fichier/dossier à supprimer : $file_name"
                        add_to_array "$file_name" to_delete
                        ;;
                esac
            done < "$temp_file"

            # Supprimer le fichier temporaire
            rm "$temp_file"
            ;;

        "Bidirectionnel")
            log "Mode de comparaison: Bidirectionnel (miroir)"

            # Vérifier les changements de A vers B
            temp_file=$(mktemp)
            rsync -ain "$source_dir/" "$dest_dir/" > "$temp_file" 2>&1
            rsync_status=$?

            # Vérifier si rsync a réussi
            if [ $rsync_status -ne 0 ]; then
                log "ERREUR: rsync a échoué avec le code $rsync_status"
                log "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log "Analyse des différences A vers B..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log "Nouveau fichier/dossier à créer : $file_name"
                        add_to_array "$file_name" to_create
                        ;;
                    "cf"|"cd")
                        log "Fichier/dossier à mettre à jour : $file_name"
                        add_to_array "$file_name" to_update
                        ;;
                esac
            done < "$temp_file"

            # Supprimer le fichier temporaire
            rm "$temp_file"

            # Vérifier les changements de B vers A
            temp_file=$(mktemp)
            rsync -ain "$dest_dir/" "$source_dir/" > "$temp_file" 2>&1
            rsync_status=$?

            # Vérifier si rsync a réussi
            if [ $rsync_status -ne 0 ]; then
                log "ERREUR: rsync a échoué avec le code $rsync_status"
                log "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log "Analyse des différences B vers A..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log "Nouveau fichier/dossier à créer en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "cf"|"cd")
                        log "Fichier/dossier à mettre à jour en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                esac
            done < "$temp_file"

            # Supprimer le fichier temporaire
            rm "$temp_file"
            ;;
    esac

    # Log des résultats
    log "=== Résultats de la comparaison ==="
    log "Fichiers à créer (${#to_create[@]}):"
    for file in "${to_create[@]}"; do
        log "  - $file"
    done

    log "Fichiers à mettre à jour (${#to_update[@]}):"
    for file in "${to_update[@]}"; do
        log "  - $file"
    done

    log "Fichiers à supprimer (${#to_delete[@]}):"
    for file in "${to_delete[@]}"; do
        log "  - $file"
    done

    log "Fichiers à créer en sens inverse (${#to_create_reverse[@]}):"
    for file in "${to_create_reverse[@]}"; do
        log "  - $file"
    done

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
        "A vers B")
            log "Synchronisation A vers B"
            rsync -av --delete "$source_dir/" "$dest_dir/"
            ;;
        "B vers A")
            log "Synchronisation B vers A"
            rsync -av --delete "$dest_dir/" "$source_dir/"
            ;;
        "Bidirectionnel")
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
