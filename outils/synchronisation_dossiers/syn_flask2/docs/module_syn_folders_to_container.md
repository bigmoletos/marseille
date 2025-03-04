# Module syn_folders_to_container

===============================================================================
SYNCHRONISATION DE DOSSIERS - OUTIL MULTIPLATEFORME
===============================================================================

Description:
-----------
Ce script permet de synchroniser des dossiers entre différents systèmes,
en gérant les caractères spéciaux et les encodages. Il supporte plusieurs
modes de synchronisation et fonctionne aussi bien sous Windows que Linux/Unix.

Fonctionnalités principales:
---------------------------
- Synchronisation unidirectionnelle (A vers B ou B vers A)
- Synchronisation bidirectionnelle (miroir)
- Gestion correcte des encodages UTF-8 et caractères spéciaux
- Support de Windows (robocopy) et Linux/Unix (rsync)
- Interface en ligne de commande et API pour intégration
- Journalisation détaillée des opérations
- Comparaison préalable des dossiers avant synchronisation

Utilisation:
-----------
1. Comparaison: python script.py compare <source_dir> <dest_dir> <mode> [output_file]
2. Synchronisation: python script.py sync <source_dir> <dest_dir> <mode> [output_file]

Modes de synchronisation:
------------------------
- "A vers B": copie de la source vers la destination
- "B vers A": copie de la destination vers la source
- "A idem B": synchronisation bidirectionnelle (miroir)

Auteur: bigmoletos
Version: 1.0.0
Date de création: 2024-02-21
Dernière modification: 2025-03-02
Licence: Propriétaire

Dépendances:
-----------
- Python >= 3.10
- rsync (pour Linux/Unix) ou robocopy (inclus dans Windows)
- Bibliothèques Python: voir section 'dependencies' ci-dessus

## Fonctions

### `add_to_array(path: str, array: List[str]) -> None`

Ajoute un chemin à un tableau sans redondance et en gérant les sous-chemins.

Args:
    path (str): Chemin à ajouter
    array (List[str]): Tableau de destination

Raises:
    ValueError: Si le chemin est invalide

**Paramètres:**

- path (str): Chemin à ajouter
- array (List[str]): Tableau de destination


### `check_dependencies() -> bool`

Vérifie la présence des dépendances système nécessaires.

Returns:
    bool: True si toutes les dépendances sont présentes, False sinon

**Retour:**

bool: True si toutes les dépendances sont présentes, False sinon


### `check_path(path: str, description: str) -> tuple[bool, str]`

Vérifie l'existence et l'accessibilité d'un chemin.

Args:
    path (str): Chemin à vérifier
    description (str): Description du chemin pour les messages d'erreur

Returns:
    tuple[bool, str]: (valide, message d'erreur)
        - valide: True si le chemin existe et est accessible
        - message d'erreur: Message explicatif si non valide, chaîne vide si valide

**Paramètres:**

- path (str): Chemin à vérifier
- description (str): Description du chemin pour les messages d'erreur

**Retour:**

tuple[bool, str]: (valide, message d'erreur)
        - valide: True si le chemin existe et est accessible
        - message d'erreur: Message explicatif si non valide, chaîne vide si valide


### `clean_path(path: str) -> str`

Nettoie le chemin en enlevant les préfixes rsync et les caractères spéciaux.
Les préfixes possibles sont '> ', '< ', '>f++++++++ ', '+++ ', 'g   ', etc.

Args:
    path (str): Chemin à nettoyer

Returns:
    str: Chemin nettoyé

**Paramètres:**

- path (str): Chemin à nettoyer

**Retour:**

str: Chemin nettoyé


### `compare_folders(source_dir: str, dest_dir: str, mode: str, output_file: str, script_path: str = None) -> None`

Compare deux dossiers selon le mode spécifié en utilisant rsync.

Cette fonction utilise rsync pour effectuer une comparaison précise des dossiers,
en tenant compte des différences de contenu, de taille et de date de modification.
Elle gère spécifiquement les problèmes d'encodage qui peuvent survenir lors de
l'utilisation de chemins contenant des caractères non ASCII ou spéciaux.

Args:
    source_dir (str): Chemin absolu du dossier source à comparer
    dest_dir (str): Chemin absolu du dossier destination à comparer
    mode (str): Mode de comparaison ('A vers B', 'B vers A', 'A idem B')
    output_file (str): Chemin du fichier JSON où stocker les résultats
    script_path (str, optional): Chemin vers un script externe (non utilisé en natif)

Raises:
    SyncError: Si une erreur se produit pendant la comparaison

Note:
    Cette fonction met à jour les variables globales to_create, to_update,
    to_delete et to_bidirectionnel avec les listes d'éléments à synchroniser.

**Paramètres:**

- source_dir (str): Chemin absolu du dossier source à comparer
- dest_dir (str): Chemin absolu du dossier destination à comparer
- mode (str): Mode de comparaison ('A vers B', 'B vers A', 'A idem B')
- output_file (str): Chemin du fichier JSON où stocker les résultats
- script_path (str, optional): Chemin vers un script externe (non utilisé en natif)


### `compare_json_folders(source_json: str, dest_json: str) -> None`

Compare les fichiers JSON des dossiers source et destination.
Remplir les variables globales to_create, to_update, to_delete.

Args:
    source_json (str): JSON du dossier source
    dest_json (str): JSON du dossier destination

**Paramètres:**

- source_json (str): JSON du dossier source
- dest_json (str): JSON du dossier destination


### `convert_path(path: str) -> str`

Convertit un chemin selon le système d'exploitation.

Args:
    path (str): Chemin à convertir

Returns:
    str: Chemin converti selon le système

Raises:
    ValueError: Si le chemin est invalide
    OSError: Si une erreur système survient lors de la conversion

**Paramètres:**

- path (str): Chemin à convertir

**Retour:**

str: Chemin converti selon le système


### `count_total_files(files_to_create: List[str], files_to_update: List[str], files_to_delete: List[str], files_to_create_reverse: List[str]) -> int`

Compte le nombre total de fichiers à traiter.

Args:
    files_to_create (List[str]): Fichiers à créer
    files_to_update (List[str]): Fichiers à mettre à jour
    files_to_delete (List[str]): Fichiers à supprimer
    files_to_create_reverse (List[str]): Fichiers à créer en sens inverse

Returns:
    int: Nombre total de fichiers

**Paramètres:**

- files_to_create (List[str]): Fichiers à créer
- files_to_update (List[str]): Fichiers à mettre à jour
- files_to_delete (List[str]): Fichiers à supprimer
- files_to_create_reverse (List[str]): Fichiers à créer en sens inverse

**Retour:**

int: Nombre total de fichiers


### `find_file(base_dir, item_path)`

Recherche un fichier dans le répertoire de base, en ignorant les préfixes.
Retourne le chemin complet s'il est trouvé, None sinon.

Args:
    base_dir (str): Répertoire de base dans lequel chercher
    item_path (str): Chemin relatif de l'élément à rechercher

Returns:
    str or None: Chemin complet du fichier s'il est trouvé, None sinon

**Paramètres:**

- base_dir (str): Répertoire de base dans lequel chercher
- item_path (str): Chemin relatif de l'élément à rechercher

**Retour:**

str or None: Chemin complet du fichier s'il est trouvé, None sinon


### `generate_folder_json(dir_path: str) -> str`

Génère une représentation JSON d'un dossier.

Args:
    dir_path (str): Chemin du dossier

Returns:
    str: Représentation JSON du dossier

Raises:
    OSError: Si le dossier n'est pas accessible
    ValueError: Si le chemin est invalide

**Paramètres:**

- dir_path (str): Chemin du dossier

**Retour:**

str: Représentation JSON du dossier


### `get_relative_path(path: str, base_path: str) -> str`

Obtient le chemin relatif par rapport à un chemin de base.

Args:
    path (str): Chemin complet
    base_path (str): Chemin de base

Returns:
    str: Chemin relatif

**Paramètres:**

- path (str): Chemin complet
- base_path (str): Chemin de base

**Retour:**

str: Chemin relatif


### `get_system_info() -> Dict[str, str]`

Détecte et retourne les informations sur le système d'exploitation.

Returns:
    Dict[str, str]: Dictionnaire contenant les informations système

**Retour:**

Dict[str, str]: Dictionnaire contenant les informations système


### `is_subpath(path: str, array: List[str]) -> bool`

Vérifie si un chemin est un sous-chemin d'un des éléments du tableau.

Args:
    path (str): Chemin à vérifier
    array (List[str]): Liste des chemins de référence

Returns:
    bool: True si le chemin est un sous-chemin, False sinon

**Paramètres:**

- path (str): Chemin à vérifier
- array (List[str]): Liste des chemins de référence

**Retour:**

bool: True si le chemin est un sous-chemin, False sinon


### `log(message: str) -> None`

Enregistre un message dans le fichier de log et l'affiche dans la console.

Args:
    message (str): Message à logger

**Paramètres:**

- message (str): Message à logger


### `log_array(array_name: str, array_content: List[str]) -> None`

Affiche le contenu d'un tableau dans les logs.

Args:
    array_name (str): Nom du tableau
    array_content (List[str]): Contenu du tableau

**Paramètres:**

- array_name (str): Nom du tableau
- array_content (List[str]): Contenu du tableau


### `normalize_path_for_json(path: str) -> str`

Normalise un chemin pour le stockage JSON selon le système d'exploitation.

Args:
    path (str): Chemin à normaliser

Returns:
    str: Chemin normalisé

**Paramètres:**

- path (str): Chemin à normaliser

**Retour:**

str: Chemin normalisé


### `prepare_path_for_rsync(path: str) -> str`

Prépare un chemin pour être utilisé avec rsync sous Windows.
Gère correctement les chemins avec lettres de lecteur et les problèmes d'encodage.

Cette fonction est essentielle pour éviter les problèmes d'encodage lors de l'utilisation
de rsync, particulièrement sous Windows où les chemins doivent être convertis
au format cygwin/msys (/cygdrive/c/...) pour être correctement interprétés.

Args:
    path (str): Chemin Windows à préparer pour rsync

Returns:
    str: Chemin compatible avec rsync, au format approprié selon l'OS

Examples:
    >>> prepare_path_for_rsync("C:\Users\Admin\Documents")
    "/cygdrive/c/Users/Admin/Documents"
    >>> prepare_path_for_rsync("/home/user/documents")
    "/home/user/documents"

**Paramètres:**

- path (str): Chemin Windows à préparer pour rsync

**Retour:**

str: Chemin compatible avec rsync, au format approprié selon l'OS

Examples:
    >>> prepare_path_for_rsync("C:\Users\Admin\Documents")
    "/cygdrive/c/Users/Admin/Documents"
    >>> prepare_path_for_rsync("/home/user/documents")
    "/home/user/documents"


### `run_subprocess_safely(cmd_args, log_prefix='Commande')`

Exécute une commande subprocess avec gestion appropriée de l'encodage pour éviter
les problèmes de caractères spéciaux dans les chemins de fichiers.

Cette fonction définit spécifiquement des variables d'environnement pour
garantir que l'encodage UTF-8 est utilisé pendant l'exécution de la commande,
ce qui résout les problèmes liés aux chemins contenant des caractères non ASCII,
notamment avec des commandes comme robocopy et rsync.

Args:
    cmd_args (List[str]): Liste des arguments de la commande à exécuter
    log_prefix (str, optional): Préfixe utilisé pour les messages de log. Par défaut "Commande".

Returns:
    subprocess.CompletedProcess: Résultat de l'exécution de la commande

Raises:
    SyncError: En cas d'erreur lors de l'exécution de la commande

Example:
    >>> result = run_subprocess_safely(["robocopy", source_dir, dest_dir, "/E"], "Robocopy")
    >>> if result.returncode < 8:  # Codes de retour spécifiques à robocopy
    >>>     logger.success("Copie réussie")

**Paramètres:**

- cmd_args (List[str]): Liste des arguments de la commande à exécuter
- log_prefix (str, optional): Préfixe utilisé pour les messages de log. Par défaut "Commande".

**Retour:**

subprocess.CompletedProcess: Résultat de l'exécution de la commande


### `setup_logging() -> None`

Configure le système de logging avec des handlers pour fichier et console.


### `show_progress(current: int, total: int, width: int = 50) -> None`

Affiche une barre de progression.

Args:
    current (int): Valeur actuelle
    total (int): Valeur totale
    width (int, optional): Largeur de la barre. Defaults to 50.

**Paramètres:**

- current (int): Valeur actuelle
- total (int): Valeur totale
- width (int, optional): Largeur de la barre. Defaults to 50.


### `success(self, message, *args, **kws)`

Méthode pour logger des messages de succès (niveau entre INFO et WARNING)


### `sync_folders(source_dir, dest_dir, mode, output_file)`

Synchronise les dossiers selon le mode spécifié en utilisant directement les commandes
du système (copy, xcopy ou robocopy sous Windows).

Args:
    source_dir (str): Chemin du dossier source
    dest_dir (str): Chemin du dossier destination
    mode (str): Mode de synchronisation ('A vers B', 'B vers A', 'A idem B')
    output_file (str): Chemin du fichier de sortie contenant les données de comparaison

**Paramètres:**

- source_dir (str): Chemin du dossier source
- dest_dir (str): Chemin du dossier destination
- mode (str): Mode de synchronisation ('A vers B', 'B vers A', 'A idem B')
- output_file (str): Chemin du fichier de sortie contenant les données de comparaison


## Classes

## Classe `SyncError`

Classe personnalisée pour les erreurs de synchronisation


