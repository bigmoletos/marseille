


## Configuration de VSCode pour utiliser CUDA :

Assurez-vous d'avoir installé les outils de développement CUDA sur votre système. Vous pouvez les télécharger depuis le site Web de NVIDIA.

- Ouvrez votre projet dans VSCode.

- Créez un fichier **tasks.json** dans le dossier .vscode de votre projet s'il n'existe pas déjà.

- Dans le fichier tasks.json, vous pouvez définir les tâches de compilation CUDA et les configurations associées. Voici un exemple de configuration de base :


```Python
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "build",
            "type": "shell",
            "command": "nvcc",
            "args": [
                "-arch=sm_86",
                "-o",
                "${fileBasenameNoExtension}.exe",
                "${file}"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```