# Module app

Application Flask pour la synchronisation de dossiers.

Cette application fournit une interface web pour synchroniser des dossiers.

Requires:
    - Python 3.6+
    - Flask
    - syn_folders_to_container.py dans le même répertoire

Auteur: bigmoletos
Version: 1.0.0-a2
Date de création: 2024-02-21
Dernière modification: 2025-03-02
Licence: Propriétaire

## Fonctions

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


### `compare_folders_route()`

Route pour comparer les dossiers.


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


### `ensure_directories()`

Crée les répertoires nécessaires s'ils n'existent pas.


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


### `index()`

Page d'accueil avec le formulaire de synchronisation.


### `internal_error(error)`

Gestion des erreurs 500.


### `is_running_in_docker()`

Vérifier si l'application s'exécute dans un conteneur Docker.


### `jsonify(*args: 't.Any', **kwargs: 't.Any') -> 'Response'`

Serialize the given arguments as JSON, and return a
:class:`~flask.Response` object with the ``application/json``
mimetype. A dict or list returned from a view will be converted to a
JSON response automatically without needing to call this.

This requires an active request or application context, and calls
:meth:`app.json.response() <flask.json.provider.JSONProvider.response>`.

In debug mode, the output is formatted with indentation to make it
easier to read. This may also be controlled by the provider.

Either positional or keyword arguments can be given, not both.
If no arguments are given, ``None`` is serialized.

:param args: A single value to serialize, or multiple values to
    treat as a list to serialize.
:param kwargs: Treat as a dict to serialize.

.. versionchanged:: 2.2
    Calls ``current_app.json.response``, allowing an app to override
    the behavior.

.. versionchanged:: 2.0.2
    :class:`decimal.Decimal` is supported by converting to a string.

.. versionchanged:: 0.11
    Added support for serializing top-level arrays. This was a
    security risk in ancient browsers. See :ref:`security-json`.

.. versionadded:: 0.2


### `map_to_docker_path(windows_path)`

Convertit un chemin Windows en chemin Docker monté.
Utilise une approche générique qui fonctionne avec n'importe quels dossiers.

Args:
    windows_path (str): Chemin Windows à convertir

Returns:
    str: Chemin Docker correspondant

**Paramètres:**

- windows_path (str): Chemin Windows à convertir

**Retour:**

str: Chemin Docker correspondant


### `not_found_error(error)`

Gestion des erreurs 404.


### `perform_sync(source_dir: str, dest_dir: str, mode: str) -> None`

Effectue la synchronisation entre les dossiers.

Args:
    source_dir (str): Dossier source
    dest_dir (str): Dossier destination
    mode (str): Mode de synchronisation

**Paramètres:**

- source_dir (str): Dossier source
- dest_dir (str): Dossier destination
- mode (str): Mode de synchronisation


### `render_template(template_name_or_list: 'str | Template | list[str | Template]', **context: 't.Any') -> 'str'`

Render a template by name with the given context.

:param template_name_or_list: The name of the template to render. If
    a list is given, the first name to exist will be rendered.
:param context: The variables to make available in the template.


### `setup_logging() -> None`

Configure le système de logging avec des handlers pour fichier et console.


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


### `sync_folders_route()`

Route pour synchroniser les dossiers.


### `validate_path(path: str, description: str) -> tuple[bool, str]`

Valide un chemin générique (Windows ou Linux).

Args:
    path (str): Chemin à valider
    description (str): Description pour les messages d'erreur

Returns:
    tuple: (succès, message d'erreur)

**Paramètres:**

- path (str): Chemin à valider
- description (str): Description pour les messages d'erreur

**Retour:**

tuple: (succès, message d'erreur)


### `validate_windows_path(path: str, description: str) -> tuple[bool, str]`

Valide un chemin Windows.

Args:
    path (str): Chemin Windows à valider
    description (str): Description pour les messages d'erreur

Returns:
    tuple: (succès, message d'erreur)

**Paramètres:**

- path (str): Chemin Windows à valider
- description (str): Description pour les messages d'erreur

**Retour:**

tuple: (succès, message d'erreur)


## Classes

