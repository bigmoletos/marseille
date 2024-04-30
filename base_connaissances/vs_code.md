# augmentation de la mémoire utilisable par vscode avec powershell
```bash

$env:NODE_OPTIONS="--max-old-space-size=81920"

```

# augmentation de la mémoire utilisable par vscode avec cmd
```bash

set NODE_OPTIONS=--max-old-space-size=81920


```
## pour augmenter de facon permanente la memoire dans le .bshrc on peut  export la constante
### au besoin création du fichier bashrc sous le terminal gitbash
```bash
touch ~/.bashrc
touch ~/.bash_profile

```
### dans le ficier bashrc :
```bash
# augmentation de la taille de la memoire utilisée par vs_code, son noyau étant du node_js
# taille allouée de 80 Go
export NODE_OPTIONS=--max-old-space-size=81920

```
### relance du fichier .bashrc
```bash
source ~/.bashrc
source ~/.bash_profile

```

### fichier .bahsrc type

```bash

#Chemin d'accès personnalisé
export PATH=$PATH:~/bin

#Paramètres de terminal
export CLICOLOR=1
export LSCOLORS=ExFxCxDxBxegedabagacad

#Fonctions shell personnalisées
function gitclean() {
    git branch --merged | egrep -v "(^\*|master|main)" | xargs git branch -d
}

#Configuration de l'éditeur par défaut
export EDITOR='code --wait'  # Pour utiliser Visual Studio Code

#Prompt personnalisé
export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "

#Correction automatique des erreurs de frappe pour cd
shopt -s cdspell

#Historique des commandes
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups

#alias
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# augmentation de la taille de la memoire utilisée par vs_code, son noyau étant du node_js
# taille allouée de 80 Go
export NODE_OPTIONS=--max-old-space-size=81920

```

