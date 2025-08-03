import os
import sys
from tkinter import Tk
from pathlib import Path

app_name = "Youtube_downloader"

# Détecter le système d'exploitation
if os.name == 'nt':  # Windows
    download_folder = Path(os.environ['USERPROFILE']) / 'Downloads'
    appData_folder = Path(os.getenv('APPDATA')) / app_name
elif os.name == 'posix':  # macOS ou Linux
    download_folder = Path(os.environ['HOME']) / 'Downloads'
    appData_folder = Path(os.environ['HOME']) / '.local' / 'share' / app_name
else:
    download_folder = Path(".")
    appData_folder = Path(".")

if getattr(sys, 'frozen', False):
    # Cas de l'exécutable
    res_directory = os.path.join(os.path.dirname(sys.executable), 'res') # Chemin du dossier ressources statique
    profiles_directory = os.path.join(appData_folder, "profiles") # Chemin des profiles de téléchargement
    lang_directory = os.path.join(res_directory, "lang")
else:
    appData_folder = './'
    res_directory = 'res' # Chemin du dossier ressources statique
    profiles_directory = "profiles" # Chemin des profiles de téléchargement
    lang_directory = os.path.join(res_directory, "lang")

root = Tk()

from loggeur import Loggeur
log = Loggeur(appData_folder)

from configuration import Config
configuration = Config()

from languages import Lang
lang = Lang()

from profils import Profiles
profiles = Profiles()