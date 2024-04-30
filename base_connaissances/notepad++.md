## Ajouter des retour ligne dans un fichier

faire "remplacer"
CTRL+H
choisir la sequence où l'on souhaite faire et un retour ligne et rajouter \r\n

ex:
```Python
message  {mon log:...}
# remplacé par :
message  \r\n{mon log:...}
```

## Recherche et instertion de retour ligne automatiquement avec remplace et  regex dans notepad ++

CTRL+H puis
```Python
RMSE:\s(1\.3[0-9]\d*)\(km/h\)
# remplacer par
\r\n$0
```

## Recherche par regex dans notepad ++




- pour selectionner les fichiers contentant RMSE: x,xxxx(km/h)  dont le rmse est inférieur à 1.5

```Python
RMSE:\s(0\.\d+|1\.[0-4]\d*)\(km/h\).*R2:\s9[5-9]\.\d+%
```
- pour selectionner les fichiers contentant RMSE: x,xxxx(km/h) et R2: xx,x% dont le rmse est inférieur à 1.5 et le R2 supérieur à 95%

```Python
RMSE:\s(0\.\d+|1\.[0-4]\d*)\(km/h\).*R2:\s9[5-9]\.\d+%
```
RMSE Partie:

RMSE: : Correspond exactement à la chaîne "RMSE:".
\s : Correspond à un espace blanc.
(0\.\d+|1\.[0-4]\d*) : Un groupe qui correspond à:
0\.\d+ : Un '0' suivi d'un point décimal et d'un ou plusieurs chiffres.
1\.[0-4]\d* : Un '1' suivi d'un point décimal, puis un chiffre entre 0 et 4, et n'importe quel nombre de chiffres supplémentaires, couvrant les nombres de 1.0 à 1.4999.
\(km/h\) : Correspond à la chaîne "(km/h)" avec les parenthèses échappées.
Partie Entre les Deux:

.* : Correspond à n'importe quel nombre de caractères, ce qui permet de passer à la partie suivante du texte. Cela suppose que la chaîne "R2:" se trouve quelque part après "RMSE:".
R2 Partie:

R2: : Correspond exactement à la chaîne "R2:".
\s : Correspond à un espace blanc.
9[5-9]\.\d+% : Correspond à '95' à '99' suivi d'un point décimal et d'un ou plusieurs chiffres, terminant par le signe pourcent.



## script pour lancer des actions sur un fichier log dans notepad ++

- dans modules_Extension/Python script  faire new script
- Ensuitepour le lancer faire modules_Extension/Scripts


```Python
# -*- coding: utf-8 -*-
import re

# Afficher la console Python Script
console.show()
console.clear()

# Texte complet du fichier ouvert dans Notepad++
text = editor.getText()

# Séparation du texte en lignes
lines = text.split('\r\n')

# Filtrer les lignes contenant 'RMSE'
filtered_lines = [line for line in lines if 'RMSE' in line]

# Concaténation des lignes filtrées pour former le nouveau texte
filtered_text = '\r\n'.join(filtered_lines)

# Remplacer un pattern par le même pattern suivi d'un saut de ligne dans le texte filtré
filtered_text = re.sub(r'Meilleurs paramètres: {', r'Meilleurs paramètres: {\r\n', filtered_text)

# Ajout du deuxième filtre
filtered_text = re.sub(r'message={', r'message={\r\n', filtered_text)

# Mettre à jour le texte dans l'éditeur
editor.setText(filtered_text)

# Expression régulière pour correspondre aux lignes avec RMSE inférieur à 1.5
regex = r"RMSE\s*:\s*(0\.\d+|1\.[0-7]\d*)"

# Trouver toutes les correspondances dans le texte filtré
matches = re.findall(regex, filtered_text)

# Afficher le nombre d'occurrences et les lignes correspondantes
occurrences = 0
for line in filtered_lines:
    if re.search(regex, line):
        occurrences += 1
        console.write("Ligne correspondante : " + line + "\n")

console.write("Nombre d'occurrences : " + str(occurrences) + "\n")

# Début et fin de l'action d'annulation pour toute la manipulation
editor.beginUndoAction()
editor.endUndoAction()

```