# ![logo_affichage](https://github.com/user-attachments/assets/ef984914-7e06-4a17-88af-2c2e0b46bc80) Telechargeur youtube




## Sommaire

- [installation](https://github.com/Pythacode/telechargeur_youtube?tab=readme-ov-file#instalation)
- [Fonctionnement](https://github.com/Pythacode/telechargeur_youtube?tab=readme-ov-file#fonctionnement)
- [Explication du code : En cours de rédaction](https://github.com/Pythacode/telechargeur_youtube?tab=readme-ov-file#explication_du_code)
- [Crédits](https://github.com/Pythacode/telechargeur_youtube?tab=readme-ov-file#crédits)

## Installation

Pour installer l'app, vous pouvez [télécharger un executable depuis les releases](https://github.com/Pythacode/telechargeur_youtube/releases), ou [télécharger le code source](https://github.com/Pythacode/telechargeur_youtube/archive/refs/heads/main.zip) puis intaller les dépendance :

### Dépendance :

- Python 3
- Pip
- Tous les modules dans [requirements.txt](https://github.com/Pythacode/telechargeur_youtube/blob/main/requirements.txt)

> [!TIP]
> Vous pouvez installer les modules avec `pip install -r requirements.txt`

## Fonctionnement

> [!WARNING]
> Attention, il est recomander d'utiliser cette application avec une bonne connection.

### Ajouter des vidéos.

Sur le premier écran de l'application, vous pouvez ajouter des URLs de vidéos dans la zone de texte prévus à cette effet.
Après avoir valider et attendus quelques instants, la vidéo apparait dans la liste. vous pouvez la suprimer, en ajouter d'autre ou passer à l'étape suivante. Vous pouvez aussi ajouter une playlist - en tant que tel, ou en séparant chaque vidéo.

### Choix du profil

Une fois que vous avez appuyer sur le boutton `Choisir le profil de téléchargement`, pour chaque vidéo, vous pouvez choisir un des deux profils : `Best audio` ou `Best vidéo`.
Dans les version future, d'autre profils et la posibilité d'en créer sois même seras implémenté.

### Téléchargement

Une fois les profils choisi et le boutton `Téléchargement` préssé, deux barre de progression s'affiche :
Une du téléchargement global et une de la vidéo actuelle.

Une fois le téléchargement terminé, les téléchargement sont dans vos dossier "Téléchargements"

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

Pour l'instant, cet outils permet seulement de suprimer les profils.

## Explication du code

### Classe `loggeur()`

Classe qui me permet de gérer les logs. Elle contient 4 fonction :

#### `__init__(self)` : Initialise les logs.

Cette fonction crée le dossier {APPDATA}/log si il n'exsiste pas, elle crée à l'interieur le fichier "AAAA_MM_DD.log" si il n'exsiste pas et écrit dedant "[START] [AAA-MM-DD HH:MM:SS]".

#### `log(self, message)`, `error(self, message)`, warnig(self, message)`

Ces fonction ajoute au log le message suivant :

`[PREFIX] [AAA-MM-DD HH:MM:SS] : msg`

Là ou prefix est différent pour chaque fonction (respectivement `INFO`, `ERROR`, `WARNIG`.
Elle affiche aussi `msg` dans la console, en rouge dans `ERROR` et en jaune dans `WARNIG`.

## Crédits

Code : Nathanaëlle [@Pythacode](https://github.com/Pythacode/)

Traduction :
- Français : Nathanaëlle [@Pythacode](https://github.com/Pythacode/)
- Allemand : Cyanne [@Art34mis](https://github.com/Art34mis/)
- Anglais : GreGrenier

#
__© Tous droits réservés 2025__

*Made by Nath with* :heart:
