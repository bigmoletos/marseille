# Documentation de l'Application de Synchronisation de Dossiers

Cette documentation couvre les différents aspects de l'application de synchronisation de dossiers, incluant les modules principaux et les scripts utilitaires.

## Table des matières

- [Introduction](#introduction)
- [Architecture du projet](#architecture-du-projet)
- [Modules principaux](#modules-principaux)
- [Scripts utilitaires](#scripts-utilitaires)
- [Guide de déploiement](#guide-de-déploiement)
- [Guide de dépannage](#guide-de-dépannage)

## Introduction

L'application de synchronisation de dossiers est conçue pour faciliter la synchronisation entre différents répertoires, avec une interface web basée sur Flask et une possibilité d'utilisation via la ligne de commande.

### Objectifs du projet

- Fournir une solution légère pour synchroniser des dossiers
- Offrir une interface web simple et intuitive
- Permettre l'exécution dans un conteneur Docker pour faciliter le déploiement
- Supporter différents modes de synchronisation (sauvegarde, restauration, bidirectionnel)

### Fonctionnalités principales

- Comparaison de dossiers pour identifier les différences
- Synchronisation unidirectionnelle ou bidirectionnelle
- Interface web intuitive pour visualiser les changements
- Compatibilité avec les chemins Windows et Linux
- Gestion des erreurs et journalisation détaillée

## Architecture du projet

L'application est structurée en plusieurs composants :

1. **Interface web (Flask)** - Fournit une interface utilisateur web
2. **Moteur de synchronisation** - Gère la logique de comparaison et synchronisation
3. **Couche d'adaptation Docker** - Permet l'exécution dans un conteneur
4. **Utilitaires** - Scripts pour le déploiement et la maintenance

## Comment générer cette documentation

Pour mettre à jour cette documentation avec les dernières modifications du code, exécutez le script `generate_docs.py` :

```bash
# Depuis le répertoire racine du projet
python generate_docs.py
```

Ce script extrait automatiquement les docstrings de tous les modules Python du projet et génère la documentation au format Markdown.