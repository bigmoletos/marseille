#!/bin/bash

#####################################################################
# Script de synchronisation de dossiers pour WSL et Linux
#####################################################################
# Description:
#   Ce script permet de comparer et synchroniser deux dossiers en utilisant
#   différents modes de synchronisation. Il gère la conversion des chemins
#   Windows en chemins Unix et fournit des résultats détaillés au format JSON.
#
# Usage:
#   ./sync_folders.sh <mode> <chemin_source> <chemin_destination> <description> <nom_fichier_sortie>
#
# Modes disponibles:
#   - compare : Compare les dossiers et génère un rapport JSON
#   - sync : Synchronise les dossiers selon le mode spécifié
#
# Modes de synchronisation:
#   - "A vers B" : Copie de la source vers la destination (sauvegarde)
#   - "B vers A" : Copie de la destination vers la source (restauration)
#   - "A idem B" : Synchronisation bidirectionnelle (miroir)
#
# Exemple d'utilisation:
#   bash -c 'bash ./sync_folders.sh compare "S:/sauve_dossier2" "S:/sauve_dossier3" "A vers B" "./output.json"'
#
# Dépendances:
#   - rsync : Pour la synchronisation des fichiers
#   - jq : Pour le traitement JSON
#
# Fonctions principales:
#   - convert_path : Convertit les chemins Windows en chemins Unix
#   - compare_folders : Compare deux dossiers et génère un rapport
#   - sync_folders : Synchronise les dossiers selon le mode choisi
#   - check_dependencies : Vérifie et installe les dépendances
#
# Fichiers générés:
#   - sync.log : Journal des opérations
#   - output.json : Résultat de la comparaison
#
# Notes:
#   - Le script nécessite WSL ou Linux pour fonctionner
#   - Les chemins Windows doivent être au format S:/chemin ou lettre:/chemin
#   - Les permissions sudo peuvent être nécessaires pour l'installation des dépendances
#
# Auteur: bigmoletos
# Date: 2024-02-21
# Version: 1.0
#####################################################################

# Définition des codes couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonctions de logging avec couleurs
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a sync.log
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCÈS: $1${NC}" | tee -a sync.log
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ATTENTION: $1${NC}" | tee -a sync.log
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR: $1${NC}" | tee -a sync.log
}

log_status() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] STATUS: $1${NC}" | tee -a sync.log
}

# Fonction de logging générique (pour compatibilité)
log() {
    log_info "$1"
}

# ce fichier peut fonctionne seul en mode terminal sous wsl ou linux
# Pour lancer le script, il faut se placer dans le dossier syn_flask et lancer le script avec la commande :
# ./sync_folders.sh <mode> <chemin_source> <chemin_destination> <description> <nom_fichier_sortie>
# exemple : bash -c 'bash ./sync_folders.sh compare "S:/sauve_dossier2" "S:/sauve_dossier3" "A vers B" "./output.json"'
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
    log_status "=== VÉRIFICATION DES DÉPENDANCES ==="

    # Détection du système
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "Système détecté: $NAME version $VERSION_ID"
    fi

    # Vérifier si sudo est disponible
    local has_sudo=false
    if command -v sudo >/dev/null 2>&1; then
        has_sudo=true
        log_success "sudo est disponible"
    else
        log_warning "sudo n'est pas installé, tentative d'utilisation de su"
    fi

    # Vérifier rsync
    if ! command -v rsync &> /dev/null; then
        log_error "rsync non trouvé"
        missing_deps+=("rsync")
    else
        # Vérifier la version de rsync
        local rsync_version=$(rsync --version | head -n1 | cut -d' ' -f3)
        log_success "rsync trouvé (version $rsync_version)"

        # Vérifier les options essentielles de rsync
        if ! rsync --help | grep -q -- "--delete"; then
            log_warning "L'option --delete n'est pas disponible dans cette version de rsync"
        fi
        if ! rsync --help | grep -q -- "--archive"; then
            log_warning "L'option --archive n'est pas disponible dans cette version de rsync"
        fi
    fi

    # Vérifier jq
    if ! command -v jq &> /dev/null; then
        log_error "jq non trouvé"
        missing_deps+=("jq")
    else
        local jq_version=$(jq --version 2>&1)
        log_success "jq trouvé (version $jq_version)"
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "Installation des dépendances manquantes : ${missing_deps[*]}"

        # Vérifier si on est sur Debian ou Ubuntu
        if [ -f /etc/debian_version ]; then
            log_info "Système Debian/Ubuntu détecté"

            # Mettre à jour uniquement les index des paquets nécessaires
            log_info "Mise à jour des index des paquets..."
            if ! sudo apt-get update -qq 2>/dev/null; then
                log_warning "Impossible de mettre à jour les index, tentative d'installation directe"
            fi

            # Installer chaque dépendance séparément
            for dep in "${missing_deps[@]}"; do
                log_info "Installation de $dep..."
                if sudo apt-get install -y "$dep"; then
                    log_success "$dep installé avec succès"
                else
                    log_error "Échec de l'installation de $dep"
                    echo "{\"error\": \"Impossible d installer $dep\"}" > "$output_file"
                    return 1
                fi
            done

            log_success "Toutes les dépendances ont été installées"
            return 0
        else
            log_error "Système non supporté (ni Debian ni Ubuntu)"
            echo "{\"error\": \"Système non supporté\"}" > "$output_file"
            return 1
        fi
    fi

    log_success "Toutes les dépendances sont satisfaites"
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
    log_info "Début de la comparaison des fichiers JSON"

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
    log_info "Nombre de fichiers trouvés - Source: $(echo "$source_files" | wc -l), Destination: $(echo "$dest_files" | wc -l)"

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

    log_status "=== DÉBUT DE LA COMPARAISON ==="
    log_info "Mode: $mode"
    log_info "Source: $1 -> $source_dir"
    log_info "Destination: $2 -> $dest_dir"
    log_info "Fichier de sortie: $4 -> $output_file"

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
            log_info "Mode de comparaison: A vers B (sauvegarde)"

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
            log_info "Mode de comparaison: B vers A (restauration)"

            # Utiliser rsync en mode dry-run pour comparer les fichiers
            temp_file=$(mktemp)
            rsync -ain --delete "$dest_dir/" "$source_dir/" > "$temp_file" 2>&1
            rsync_status=$?

            # Vérifier si rsync a réussi
            if [ $rsync_status -ne 0 ]; then
                log_error "ERREUR: rsync a échoué avec le code $rsync_status"
                log_error "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log_info "Analyse des différences..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log_info "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log_info "Nouveau fichier/dossier à créer en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "cf"|"cd")
                        log_info "Fichier/dossier à mettre à jour en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "*d"|"*f")
                        log_info "Fichier/dossier à supprimer : $file_name"
                        add_to_array "$file_name" to_delete
                        ;;
                esac
            done < "$temp_file"

            # Supprimer le fichier temporaire
            rm "$temp_file"
            ;;

        "Bidirectionnel")
            log_info "Mode de comparaison: Bidirectionnel (miroir)"

            # Vérifier les changements de A vers B
            temp_file=$(mktemp)
            rsync -ain "$source_dir/" "$dest_dir/" > "$temp_file" 2>&1
            rsync_status=$?

            # Vérifier si rsync a réussi
            if [ $rsync_status -ne 0 ]; then
                log_error "ERREUR: rsync a échoué avec le code $rsync_status"
                log_error "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log_info "Analyse des différences A vers B..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log_info "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log_info "Nouveau fichier/dossier à créer : $file_name"
                        add_to_array "$file_name" to_create
                        ;;
                    "cf"|"cd")
                        log_info "Fichier/dossier à mettre à jour : $file_name"
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
                log_error "ERREUR: rsync a échoué avec le code $rsync_status"
                log_error "Sortie d'erreur: $(cat "$temp_file")"
                rm "$temp_file"
                echo '{"error": "rsync a échoué"}' > "$output_file"
                return 1
            fi

            log_info "Analyse des différences B vers A..."

            while IFS= read -r line; do
                [[ -z "$line" ]] && continue
                [[ "$line" =~ ^building ]] && continue
                [[ "$line" =~ ^sending ]] && continue
                [[ "$line" =~ ^sent ]] && continue
                [[ "$line" =~ ^total ]] && continue

                # Extraire le type de changement et le nom du fichier
                change_type=${line:0:2}
                file_name=$(echo "$line" | sed 's/^[^ ]* *//')

                log_info "Ligne analysée: [$change_type] [$file_name]"

                case "$change_type" in
                    ">f"|">d"|".d")
                        log_info "Nouveau fichier/dossier à créer en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                    "cf"|"cd")
                        log_info "Fichier/dossier à mettre à jour en sens inverse : $file_name"
                        add_to_array "$file_name" to_create_reverse
                        ;;
                esac
            done < "$temp_file"

            # Supprimer le fichier temporaire
            rm "$temp_file"
            ;;
    esac

    # Log des résultats
    log_info "=== Résultats de la comparaison ==="
    log_info "Fichiers à créer (${#to_create[@]}):"
    for file in "${to_create[@]}"; do
        log_info "  - $file"
    done

    log_info "Fichiers à mettre à jour (${#to_update[@]}):"
    for file in "${to_update[@]}"; do
        log_info "  - $file"
    done

    log_info "Fichiers à supprimer (${#to_delete[@]}):"
    for file in "${to_delete[@]}"; do
        log_info "  - $file"
    done

    log_info "Fichiers à créer en sens inverse (${#to_create_reverse[@]}):"
    for file in "${to_create_reverse[@]}"; do
        log_info "  - $file"
    done

    return 0
}

# Fonction pour synchroniser les dossiers
sync_folders() {
    local source_dir=$(convert_path "$1")
    local dest_dir=$(convert_path "$2")
    local mode="$3"

    log_status "=== DÉBUT DE LA SYNCHRONISATION ==="
    log_info "Mode: $mode"
    log_info "Source: $1 -> $source_dir"
    log_info "Destination: $2 -> $dest_dir"
    log_warning "Vérification des permissions d'accès aux dossiers..."

    # Vérifier les permissions avant la synchronisation
    if [ ! -r "$source_dir" ]; then
        log_error "Pas de permission de lecture sur le dossier source"
        return 1
    fi
    if [ ! -w "$dest_dir" ]; then
        log_error "Pas de permission d'écriture sur le dossier destination"
        return 1
    fi

    # Options de base pour rsync
    local rsync_opts="-rtlv --progress"

    case "$mode" in
        "A vers B")
            log_info "Démarrage de la synchronisation A vers B"
            if ! rsync $rsync_opts --delete "$source_dir/" "$dest_dir/"; then
                log_error "Erreur lors de la synchronisation A vers B"
                return 1
            fi
            ;;
        "B vers A")
            log_info "Démarrage de la synchronisation B vers A"
            if ! rsync $rsync_opts --delete "$dest_dir/" "$source_dir/"; then
                log_error "Erreur lors de la synchronisation B vers A"
                return 1
            fi
            ;;
        "Bidirectionnel")
            log_info "Démarrage de la synchronisation bidirectionnelle"
            if ! rsync $rsync_opts "$source_dir/" "$dest_dir/"; then
                log_error "Erreur lors de la synchronisation A vers B"
                return 1
            fi
            if ! rsync $rsync_opts "$dest_dir/" "$source_dir/"; then
                log_error "Erreur lors de la synchronisation B vers A"
                return 1
            fi
            ;;
    esac

    log_success "=== SYNCHRONISATION TERMINÉE ==="
    return 0
}

# Point d'entrée principal
case "$1" in
    "compare")
        log_info "Lancement de la comparaison des dossiers"
        compare_folders "$2" "$3" "$4" "$5"
        ;;
    "sync")
        log_info "Lancement de la synchronisation des dossiers"
        sync_folders "$2" "$3" "$4"
        ;;
    *)
        log_error "Usage: $0 {compare|sync} [arguments]"
        exit 1
        ;;
esac
