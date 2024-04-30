# Gestion des Listes et Dictionnaires en Python

## Méthodes pour les Listes

1. **append(element)** - Ajoute un élément à la fin de la liste.
2. **extend([element1, element2])** - Étend la liste en y ajoutant tous les éléments de l'itérable fourni.
3. **insert(index, element)** - Insère un élément à la position indiquée.
4. **remove(element)** - Supprime le premier élément correspondant dans la liste.
5. **pop(index=-1)** - Supprime et retourne l'élément à l'index donné (par défaut, le dernier).
6. **del statement** - Supprime un ou plusieurs éléments de la liste (`del ma_liste[index]`).

## Méthodes pour les Dictionnaires

1. **get(key, default=None)** - Retourne la valeur pour une clé, ou `default` si la clé n'est pas dans le dictionnaire.
2. **keys()** - Retourne une vue des clés du dictionnaire.
3. **values()** - Retourne une vue des valeurs du dictionnaire.
4. **items()** - Retourne une vue des paires clé/valeur du dictionnaire.
5. **update([other])** - Met à jour le dictionnaire avec les paires clé/valeur de `other`.
6. **pop(key[, default])** - Supprime la clé et retourne la valeur correspondante. Si la clé n'est pas trouvée, retourne `default` (erreur si non spécifié).
7. **popitem()** - Supprime et retourne une paire (clé, valeur) arbitraire.
8. **del statement** - Supprime une clé spécifique (`del mon_dico['clé']`).

## Classes et Modules Utiles

- **collections.defaultdict** - Classe de dictionnaire qui appelle une fonction factory pour fournir des valeurs manquantes.
- **collections.OrderedDict** - Classe de dictionnaire qui se souvient de l'ordre dans lequel ses clés ont été insérées pour la première fois.
- **list** - Le type de données liste intégré pour stocker des collections d'objets.

```python
ma_liste.pop(1)  # Supprime l'élément à l'index 1
ma_liste.pop()   # Supprime le dernier élément

del ma_liste[1]  # Supprime l'élément à l'index 1
del ma_liste     # Supprime toute la liste

mon_dico.pop('clé')  # Supprime l'élément avec la clé 'clé'

mon_dico.popitem()
del mon_dico['clé']
```

