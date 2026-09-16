# ![logo_affichage](./docs/logo_affichage.png) Telechargeur youtube


## Sommaire

- [installation](#installation)
- [Fonctionnement](#fonctionnement)
- [Explication du code](#explication_du_code)
- [Contribuer](#Contribuer)
- [Crédits](#crédits)

## Installation

Pour installer l'app, vous pouvez ~~[télécharger un executable depuis les releases](https://github.com/Pythacode/telechargeur_youtube/releases)~~, ou [télécharger le code source](https://github.com/Pythacode/telechargeur_youtube/archive/refs/heads/main.zip) puis intaller les dépendance :

Assurez-vous d'avoir télécharger le code source dans un dossier et d'avoir python3 et pip d'instalé.

Ensuite installer les dépendances avec
```shell
pip install -r requirements.txt
```

## Fonctionnement

> [!WARNING]
> Il est requis d'utiliser cette application avec une bonne connection.

L'aplication est compatible avec toutes les plateformes de [ytb-dlp](https://github.com/yt-dlp/yt-dlp).

### Ajouter des vidéos.

Sur le premier écran de l'application, vous pouvez ajouter des URLs de vidéos dans la zone de texte prévus à cette effet.
Après avoir valider et attendus quelques instants, la vidéo apparait dans la liste. vous pouvez la suprimer, en ajouter d'autre ou passer à l'étape suivante. Vous pouvez aussi ajouter une playlist.

### Choix du profil

Une fois que vous avez appuyer sur le boutton `Choisir le profil de téléchargement`, pour chaque vidéo, vous pouvez choisir un des trois profils : `Best audio`, `Best vidéo` ou `Best Vidéo under 1080p`.
Dans les version future, d'autre profils et la posibilité d'en créer sois même seras implémenté.

### Téléchargement

Une fois les profils choisi et le boutton `Téléchargement` préssé, deux barre de progression s'affiche :
Une du téléchargement global et une de la vidéo actuelle.

Une fois le téléchargement terminé, les téléchargement sont dans votre dossier Téléchargements

> [!WARNING]
> Comme la date du fichier est la date de l'upload sur youtube, il se peut qu'elle se retrouve à la fin de votre dossier téléchargement.

### Languages

Vous pouvez changer de langues dans le menu `Langues`.

Une fois la langue choisi sélectionner, vous devez relancer l'application.

Langues diponible :

- Français
- Anglais
- Allemand

### Outils d'édition de profils

> [!CAUTION]
> Seul les fonctions `__init__` et `getprofiles` fonctionent, l'autre utilisant tkinter, elle à temporairement été désactiver le temps de la redéveloper avec la nouvelle architecture & qt6.

Pour l'instant, cet outils permet seulement de suprimer les profils.

## Explication du code

### Architecture

```
├── context.py # Fichier ou sont initialiser la langues, les réglages...
└── main.py
    └── ui.py # Interface Graphique
        └── moteur.py # Moteur de yt-dlp
```

### Classe `loggeur()` (loggeur.py)

Classe qui permet de gérer les logs. Elle contient 4 fonction :

#### `__init__(self)` : Initialise les logs.

Cette fonction crée le dossier {APPDATA}/log si il n'exsiste pas, elle crée à l'interieur le fichier "AAAA_MM_DD.log" si il n'exsiste pas et écrit dedant "[START] [AAA-MM-DD HH:MM:SS]".

#### `info(self, message)`, `error(self, message)`, `warning(self, message)`

Ces fonction ajoute au log le message suivant :

`[PREFIX] [AAA-MM-DD HH:MM:SS] : msg`

Là ou prefix est différent pour chaque fonction (respectivement `INFO`, `ERROR`, `WARNING`).
Elle affiche aussi `msg` dans la console, en rouge dans `ERROR` et en jaune dans `WARNING`.

## Contribuer
Vous pouvez librement contribuer, en codant ou en traduisant.
Pour ce faire [ouvrez une pull request](https://github.com/Pythacode/telechargeur_youtube/pulls) ou [envoyez-moi un mail](mailto:contact+yt-dlp@nathanaelle.org) pour vous assurez que personne ne travaille sur la même chose que vous.
Si vous voulez participer mais que vous ne savez pas quoi faire, lancez l'aplication et regardez par vous même, il reste beucoup à améliorer

## Crédits

Code : Nathanaëlle [@Pythacode](https://github.com/Pythacode/)

Traduction :
- Français : Nathanaëlle [@Pythacode](https://github.com/Pythacode/)
- Allemand : Cyanne [@Art34mis](https://github.com/Art34mis/)
- Anglais : GreGrenier

<hr>
*Made by Nath with* :heart:


> [!IMPORTANT]
> Ce projet est sous licence Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).<br>
> Vous pouvez copier, distribuer et modifier ce projet à condition que ce soit à des fins non commerciales et que vous me créditiez.<br>
> [Texte complet de la licence](LICENSE)<br>
> [Site officiel de la licence](https://creativecommons.org/licenses/by-nc/4.0/legalcode.fr)<br>
