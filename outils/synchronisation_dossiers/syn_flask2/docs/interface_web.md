# Guide d'utilisation de l'interface web

Ce document détaille les fonctionnalités de l'interface web de l'application de synchronisation de dossiers et explique comment l'utiliser efficacement.

## Table des matières

- [Accès à l'interface](#accès-à-linterface)
- [Page d'accueil](#page-daccueil)
- [Comparaison de dossiers](#comparaison-de-dossiers)
- [Synchronisation](#synchronisation)
- [Résultats et historique](#résultats-et-historique)
- [Fonctionnalités avancées](#fonctionnalités-avancées)

## Accès à l'interface

Une fois l'application démarrée (via Docker ou directement), vous pouvez accéder à l'interface web en ouvrant un navigateur et en vous rendant à l'adresse:

```
http://localhost:5000
```

## Page d'accueil

La page d'accueil présente un formulaire avec les champs suivants:

![Interface d'accueil](../static/images/interface_accueil.png)

### Éléments principaux

1. **Dossier source** - Le chemin vers le dossier source (exemple: `S:/sauve_dossier2`)
2. **Dossier destination** - Le chemin vers le dossier destination (exemple: `S:/sauve_dossier4`)
3. **Mode de synchronisation** - Menu déroulant avec trois options:
   - **A vers B (sauvegarde)** - Copie unidirectionnelle de la source vers la destination
   - **B vers A (restauration)** - Copie unidirectionnelle de la destination vers la source
   - **Bidirectionnel (miroir)** - Synchronisation dans les deux sens
4. **Bouton "Comparer les dossiers"** - Lance la comparaison sans effectuer de modifications

## Comparaison de dossiers

Après avoir cliqué sur "Comparer les dossiers", l'application affiche un rapport détaillé des différences trouvées:

### Résultats de la comparaison

Les résultats sont organisés en plusieurs sections:

1. **Fichiers à créer** - Fichiers présents dans la source mais absents de la destination
2. **Fichiers à mettre à jour** - Fichiers présents dans les deux dossiers mais avec des différences
3. **Fichiers à supprimer** - Fichiers présents dans la destination mais absents de la source (en mode A vers B seulement)

### Navigation dans les résultats

Chaque section peut être développée/réduite:

- Cliquez sur les en-têtes de section pour afficher/masquer le contenu
- Utilisez les boutons "Tout développer" et "Tout réduire" pour gérer l'affichage
- Les dossiers peuvent être développés individuellement pour explorer la structure

### Exemple d'utilisation

1. Entrez les chemins des dossiers source et destination
2. Sélectionnez le mode "A vers B (sauvegarde)"
3. Cliquez sur "Comparer les dossiers"
4. Examinez les fichiers qui seraient créés/mis à jour/supprimés
5. Si le résultat correspond à vos attentes, continuez avec la synchronisation

## Synchronisation

Une fois la comparaison effectuée, vous pouvez lancer la synchronisation proprement dite:

### Lancement de la synchronisation

1. Vérifiez que les résultats de la comparaison correspondent à ce que vous attendez
2. Cliquez sur le bouton "Lancer la synchronisation" en bas des résultats
3. Une barre de progression s'affiche pendant le processus
4. Attendez que l'opération se termine

### Modes de synchronisation expliqués

- **A vers B (sauvegarde)**
  - Copie les fichiers nouveaux ou modifiés de la source vers la destination
  - Supprime les fichiers dans la destination qui n'existent pas dans la source
  - Préserve la structure exacte de la source

- **B vers A (restauration)**
  - Copie les fichiers nouveaux ou modifiés de la destination vers la source
  - Ne supprime aucun fichier dans la source
  - Utile pour restaurer des données

- **Bidirectionnel (miroir)**
  - Synchronise les deux dossiers pour qu'ils aient le même contenu
  - Copie les fichiers nouveaux ou modifiés dans les deux directions
  - Ne supprime aucun fichier
  - Les fichiers plus récents remplacent les plus anciens

## Résultats et historique

Après la synchronisation, un rapport détaillé est affiché:

### Informations du rapport

- **Récapitulatif** - Nombre total de fichiers créés, mis à jour et supprimés
- **Détails** - Liste complète des fichiers traités, organisée par catégorie
- **Format JSON** - Option pour afficher les résultats au format JSON (utile pour le débogage)

### Conservation des résultats

Les résultats de synchronisation sont conservés dans le dossier `data` de l'application et peuvent être consultés ultérieurement.

## Fonctionnalités avancées

### Validation des chemins

L'application vérifie automatiquement la validité des chemins saisis:

- Les chemins doivent exister et être accessibles
- Les chemins source et destination doivent être différents
- Les formats Windows et Linux sont supportés

### Gestion des erreurs

En cas d'erreur pendant la synchronisation:

1. Un message d'erreur détaillé s'affiche
2. Les journaux sont enregistrés dans le dossier `logs`
3. L'application suggère des solutions possibles

### Journalisation

Tous les événements sont enregistrés dans les fichiers journaux:

- Consultez le fichier `logs/app.log` pour les détails des opérations
- En cas de problème, ces journaux sont précieux pour le dépannage