import yt_dlp
from PIL import Image
import requests
from io import BytesIO
from tkinter import *
from PIL import Image, ImageTk
from tkinter.ttk import Progressbar
import threading
import queue
from tkinter.messagebox import askyesno, showwarning, askokcancel
import os
import json
from pathlib import Path
import traceback
import re
from datetime import datetime
from colorama import Fore, init
import webbrowser
import sys
import subprocess
import locale

# Ajoute des modules pour faciliter la detection par pyinstaler

import pyexpat
import unicodedata
print(unicodedata.name('é'))

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

class loggeur() :
    def __init__(self) :

        log_file = os.path.join(appData_folder, "logs")

        if not os.path.exists(log_file):
            os.makedirs(log_file)

        self.file = open(os.path.join(log_file, f"{datetime.now().strftime('%Y_%m_%d')}.log"), 'a+', encoding='utf-8')
        message = f"[START] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]"
        self.file.write(message + '\n')

    def log(self, message) :
        message = f"[INFO] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(message)

    def error(self, message) :
        message = f"[ERROR] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(Fore.RED + message)

    def warnig(self, message) :
        message = f"[WARNING] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(Fore.YELLOW + message)

log = loggeur()

init(autoreset=True)

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

try :
    with open(os.path.join(appData_folder, 'config.json'), 'r', encoding='utf-8') as f:
        configuration = json.load(f)
except :
    configuration = {}

def updtadeConfig(key, value) :
    configuration[key] = value
    with open(os.path.join(appData_folder, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(configuration, f, ensure_ascii=False, indent=4)


languages = ['fr_FR', 'en_EN']

language = configuration.get('lang', locale.getlocale()[0] if locale.getlocale()[0] in languages else 'en_EN')

class lang:
    def __init__(self, language='en_EN'):

        log.log(f'Language : {language}')

        path = os.path.join(lang_directory, f"{language}.json") if language in languages else 'en_EN'
        try:
            with open(os.path.join(lang_directory, "fr_FR.json"), "r", encoding="utf-8") as f:
                ref = list(json.load(f).keys())

            with open(path, "r", encoding="utf-8") as f:
                translations = json.load(f)

                cles = translations.keys()     
                    
                for cle in ref :
                    if cle not in cles :
                        log.warnig(f'Key \"{cle}\" not found in {language}.json.')
                        return self.__init__()

                # Attribue dynamiquement les traductions à l'objet
                for key, text in translations.items():
                    setattr(self, key, text)

        except Exception as e:
            log.error(f"Erreur de chargement des traductions : {e}")
            return self.__init__()
    
    def refresh(self, lang) :
        showwarning(t.warnig, t.restart_confirm)

        updtadeConfig('lang', lang)

        self.__init__(lang)
        root.update()
        # Détruit la fenêtre Tkinter
        root.destroy()

        # Redémarre le script Python
        log.log([sys.executable] + sys.argv)
        subprocess.Popen([sys.executable] + sys.argv, close_fds=True)
        sys.exit()

t = lang(language)

def get_profiles() :
    try :
        log.log(profiles_directory)
        return [file.removesuffix('.json').replace('_', ' ') for file in os.listdir(profiles_directory) if os.path.isfile(os.path.join(profiles_directory, file)) and file.endswith('.json') and not ' ' in file]
    except Exception as e :
        log.error(e + traceback.format_exc())

def remove_colors(log):
    # Expression régulière pour détecter les codes de couleur ANSI
    color_code_pattern = r'\x1b\[[0-9;]*m'
    # Supprimer les codes de couleur
    cleaned_log = re.sub(color_code_pattern, '', log)
    return cleaned_log

def download() :
    
    total = len(scrollable_frame.winfo_children())

    log.log(f'START DOWNLOAD OF {total} MOVIES')

    # Création de la fenêtre de progression
    progress_windows = Toplevel(root)

    Label(progress_windows, text=t.global_download).pack()

    allprogressBarDownload = Progressbar(progress_windows, orient=HORIZONTAL, length=400, mode='determinate')
    allprogressBarDownload.pack(side=TOP, fill="x", expand=True)

    Label(progress_windows, text=t.download_one).pack()    
    
    allProgresseLabel = Label(progress_windows, text=t.download_status.format(total=total))
    allProgresseLabel.pack(side=BOTTOM)

    
    progressBarDownload = Progressbar(progress_windows, orient=HORIZONTAL, length=400, mode='indeterminate')
    progressBarDownload.pack(side=TOP, fill="x", expand=True)
    progressBarDownload.start()

    ProgresseLabel = Label(progress_windows, text=t.downloading)
    ProgresseLabel.pack(side=BOTTOM)

    nbr = 0

    for widget in scrollable_frame.winfo_children(): #Liste les vidéos
        if isinstance(widget, Frame):
            url, options_file = None, None

            while url == None: # Récupère l'url dans le label texte masqué
                
                for child in widget.winfo_children():
                    if isinstance(child, Label) :
                        text = child.cget('text')
                        if text.startswith('url:') :
                            url = text.removeprefix('url:')
                            break
            
            while options_file == None : # Récupère l'url dans le label texte masqué
                
                for child in widget.winfo_children():
                    if isinstance(child, OptionMenu) :
                            options_file = os.path.join(profiles_directory, f"{child.cget('text').replace(' ', '_')}.json")
                            break
            
            log.log(f'DOWNLOAD NEW URL: {url} - {options_file}')

            class YTDLLogger:
                
                #Logger personnalisé pour capturer et afficher les messages de yt-dlp.
                
                def debug(self, msg):
                    # Affiche les messages de debug
                    msg = remove_colors(msg)

                    log.log(msg)

                    if msg.startswith('[download]') and not '100%' in msg :
                        if "%" in msg :
                            msg = msg.split(' ')
                            for i in msg :
                                try :
                                    msg.remove("")
                                except ValueError :
                                    break

                            progressBarDownload.config(mode='determinate')

                            progressBarDownload['value'] = int(float(msg[1].removesuffix('%')))
                            msg = t.download_progress.format(
                                    current=msg[1],
                                    total=msg[3],
                                    speed=msg[5],
                                    eta=msg[7]
                            )
                    else : 
                        progressBarDownload.config(mode='indeterminate')

                    ProgresseLabel.config(text=msg)

                def warning(self, msg):
                    # Affiche les avertissements
                    ProgresseLabel.config(text=f"WARNING: {msg}")
                    log.warnig(msg)

                def error(self, msg):
                    # Affiche les erreurs
                    ProgresseLabel.config(text=f"ERROR: {msg}")
                    log.error(msg)
                    
            # Récupère le profil choisi
            options = json.loads(open(options_file, 'r').read()) # Récupère le profil choisi
            options["outtmpl"] = os.path.join(download_folder, options["outtmpl"])

            options['quiet'] = True  # Supprime la sortie standard (redirigée vers le logger)
            options['logger'] = YTDLLogger() # Utilise le logger personnalisé
            options['extract_flat'] = True                      

            # Queue pour recuperer les donnes
            q = queue.Queue()
            download_finished = threading.Event()

            # Fonction qui exécute le téléchargement dans un thread séparé
            def process_download():
                try:
                    with yt_dlp.YoutubeDL(options) as ydl:
                        info = ydl.download([url])
                    q.put(info)  # Mettre l'info dans la queue pour être récupérée par le thread principal
                except Exception as e:
                    error_details = traceback.format_exc()
                    q.put(f"ERROR : {str(e)}")
                    log.error(f"{str(e)}\nContexte :\n{error_details}")
                finally:
                    download_finished.set()

            # Fonction pour vérifier la queue et mettre à jour l'interface
            def check_queue():
                try:
                    # Essayer de récupérer l'info sans bloquer
                    info = q.get_nowait()  

                    if isinstance(info, dict):  # Si l'info est un dictionnaire (métadonnées)
                        ProgresseLabel.config(text=t.complet_downloading)

                    else:  # Si c'est une erreur
                        ProgresseLabel.config(text=info)
                    
                    progress_windows.after(2000, progress_windows.destroy)  # Fermer après 2s

                except queue.Empty:  
                    progress_windows.update()


            # Démarrer le téléchargement dans un thread séparé
            thread = threading.Thread(target=process_download, daemon=True)
            thread.start()

            # Boucle pour attendre la fin du téléchargement
            while not download_finished.is_set():
                check_queue()
                progress_windows.update()  # Met à jour l'interface
                root.update()  # Met à jour la fenetre principal

        nbr += 1

        if allprogressBarDownload.winfo_exists():
            allprogressBarDownload.config(value=int(100*nbr/total))
        if allProgresseLabel.winfo_exists() :
            pourcent = 100*nbr/total
            allProgresseLabel.config(text=t.total_downloading_progress.format(
                nbr = nbr,
                total=total,
                pourcent=pourcent
            ))

    # Fermer la fenêtre de progression après la fin
    progress_windows.destroy()

    MoviesList.pack_forget()
    Next_button.pack_forget()

    ConfirmLabel.config(text=t.complet_downloading_confim_msg.format(download_folder=download_folder))
    ConfirmLabel.pack()

def select_profil() :

    if len(scrollable_frame.winfo_children()) == 0 : return

    profiles = get_profiles()
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, Frame):
            for child in widget.winfo_children(): # Retire le boutton suprimer
                if isinstance(child, Button):
                    child.pack_forget()

            # Ajoute une selection de profil
            
            selected_profile = StringVar(root)

            # Définir une valeur initiale pour la variable
            selected_profile.set(profiles[0])

            # Création de l'OptionMenu pour la sélection
            option_menu = OptionMenu(widget, selected_profile, *profiles)
            option_menu.pack()

            
    EntryFrame.pack_forget()
    Next_button.config(text=t.downloading, command=download)

def add_url(url=False, dowload_playlist=False):


    #Ajoute un classe pour intercepter les logs de yt_dlp et les afficher dans une fenetre séparer
    class YTDLLogger:
        """
        Logger personnalisé pour capturer et afficher les messages de yt-dlp.
        """
        def debug(self, msg):
            # Affiche les messages de debug
            ProgresseLabel.config(text=msg)
            log.log(f"{msg}")

        def warning(self, msg):
            # Affiche les avertissements
            ProgresseLabel.config(text=f"WARNING: {msg}")
            log.warnig(f"{msg}")

        def error(self, msg):
            # Affiche les erreurs
            ProgresseLabel.config(text=f"ERROR: {msg}")
            log.error(f"{msg}")

    #Ajoute une fonction pour ajouter une vidéo a la liste
    def add_movies(info, is_playlist=False) :
        
        duree_secondes = info.get('duration', 0)

        # Formater la durée en HH:MM:SS
        heures = duree_secondes // 3600
        minutes = (duree_secondes % 3600) // 60
        secondes = duree_secondes % 60

        title = info.get('title', 'Titre indisponible')
        view_count = info.get('view_count', None)
        subtitlte = (
            info.get('artist', info.get('uploader', t.artist_not_found))
            + ' · '
            + f"{heures:02}:{minutes:02}:{secondes:02}"
            + ' · '
            + (t.view_number_not_found if view_count is None else '{:,}'.format(view_count).replace(',', ' '))
            + ' ' + t.views
        )


        thumbnail_url = info.get('thumbnail')
        
        if is_playlist :
            title = '[Playlist] ' + title
            subtitlte += ' · ' + str(info.get('playlist_count', t.video_number_not_found)) + ' ' + t.video
            try:
                thumbnail_url = info.get('thumbnails')[0].get('url')
            except TypeError :
                thumbnail_url = False

        # Création d'un cadre pour chaque vidéo
        cadre = Frame(scrollable_frame)
        cadre.pack(fill=X, padx=10, pady=5)

        # Gestion de la miniature

        if thumbnail_url :

            response = requests.get(thumbnail_url)
            image = Image.open(BytesIO(response.content))
            width, height = image.size

            
        else :
            image = Image.open(os.path.join(os.path.join(res_directory, "img"), 'jaquette_default.png'))
        
        width, height = image.size
        new_height = 50
        new_width = int((new_height / height) * width)  # Calculer la nouvelle largeur en fonction de la hauteur

        # Redimensionner l'image tout en gardant les proportions
        image = image.resize((new_width, new_height))
            
        # Charger l'image et l'afficher
        image = ImageTk.PhotoImage(image)
        image_label = Label(cadre, image=image)
        image_label.image = image  # Préserver la référence pour éviter le garbage collection
        image_label.pack(side=LEFT, padx=5)


        # Ajouter les titres
        texte_frame = Frame(cadre)
        texte_frame.pack(side=LEFT, padx=10, fill=BOTH, expand=True)

        label_texte1 = Label(texte_frame, text=title, font=("Arial", 12, "bold"))
        label_texte1.pack(anchor="w")

        label_texte2 = Label(texte_frame, text=subtitlte, font=("Arial", 10))
        label_texte2.pack(anchor="w")

        label_url = Label(cadre, text=f"url:{url}", fg="white", font=("Arial", 0))
        label_url.pack_forget()

        # Ajouter un bouton "Supprimer"
        menu_button = Button(cadre, text=t.delete, relief=FLAT, command=cadre.destroy)
        menu_button.pack(side=RIGHT)
    
    #Récuperer l'url si non fournie comme argument
    if not url:
        url = EntryURL.get()
        if '&list=' in url :
            if askyesno('Playlist', t.playlist_confirm) :
                url = url.split('&list=')[0]
    
    log.log(f"NEW URL : {url}")

    # Effacer l'entrée URL
    EntryURL.delete(0, END)

    ydl_opts = {
            'quiet': True,  # Supprime la sortie standard (redirigée vers le logger)
            'logger': YTDLLogger(), # Utilise le logger personnalisé
            'skip_download' : True,
    }

    # Queue pour recuperer les donnes
    q = queue.Queue()

    # Fonction qui exécute le téléchargement dans un thread séparé
    def process_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)  # Extraire les métadonnées sans télécharger
            q.put(info)  # Mettre l'info dans la queue pour être récupérée par le thread principal
        except Exception as e:
            q.put(f"Erreur : {str(e)}")  # Mettre l'erreur dans la queue
        finally:
            progress_windows.after(2000, progress_windows.destroy)  # Fermer la fenêtre de progression après 0s

    # Fonction pour vérifier la queue et mettre à jour l'interface
    def check_queue():
        try:
            # Essayer de récupérer l'info sans bloquer
            info = q.get_nowait()  

            if isinstance(info, dict):  # Si l'info est un dictionnaire (métadonnées)
                ProgresseLabel.config(text=t.complet_downloading)

                if info.get('_type', None) == 'playlist' : #Si c'est une playlist
                    if dowload_playlist : # Vérifie si l'utilisateur a déja répondus a la question suivante
                        for video in info.get('entries') :
                            add_movies(video)
                    elif askyesno('Playlist', t.ask_playlist.format(nbr_video=str(info.get('playlist_count', 'Nombre de vidéo indisponible')))) : #Demande a l'utilisateur si on ajoute chaque vidéo séparément
                        add_movies(info, True)
                    else : 
                        add_url(url, True)
                else :
                    add_movies(info)

            else:  # Si c'est une erreur
                ProgresseLabel.config(text=info)
            
            progress_windows.after(0, progress_windows.destroy)  # Fermer après 2s

        except queue.Empty:  # Si la queue est vide, vérifier à nouveau
            progress_windows.after(100, check_queue)

    # Création de la fenêtre de progression
    progress_windows = Toplevel(root)

    # Barre de progression et label
    progressBarMetahdonne = Progressbar(progress_windows, orient=HORIZONTAL, length=400, mode='indeterminate')
    progressBarMetahdonne.pack(side=TOP, fill="x", expand=True)
    progressBarMetahdonne.start()

    ProgresseLabel = Label(progress_windows, text=t.downloading)
    ProgresseLabel.pack(side=BOTTOM)

    # Démarrer le téléchargement dans un thread séparé
    thread = threading.Thread(target=process_download, daemon=True)
    thread.start()

    # Lancer la vérification périodique de la queue
    check_queue()

def profilesEditor() :
    try :
        def remove(name, cadre) :
            if askokcancel(t.confirmation, t.remove_profils_confirmation.format(name=name)) :
                os.remove(f'{profiles_directory}/{name.replace(' ', '_')}.json')
                cadre.destroy()


        profilesRoot = Toplevel(root)

        ProfilesList = Frame(profilesRoot, relief=GROOVE)
        ProfilesList.pack(fill="both", expand=True, padx=5, pady=2.5)

        # Canvas pour le défilement
        ProfilesCanva = Canvas(ProfilesList, highlightthickness=0)
        ProfilesCanva.pack(side="left", fill="both", expand=True)

        # Barre de défilement verticale
        scrollbar = Scrollbar(ProfilesList, orient="vertical", command=ProfilesCanva.yview)
        scrollbar.pack(side="right", fill="y")
        ProfilesCanva.configure(yscrollcommand=scrollbar.set)

        # Frame pour les vidéos à l'intérieur du Canvas
        scrollable_frame = Frame(ProfilesCanva)
        canvas_frame = ProfilesCanva.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Ajuster la taille du Canvas en fonction du contenu
        def on_frame_configure(event):
            ProfilesCanva.configure(scrollregion=ProfilesCanva.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Ajuster la largeur du Canvas au redimensionnement
        ProfilesCanva.bind("<Configure>", lambda e: ProfilesCanva.itemconfig(canvas_frame, width=e.width))
        
        for profil in get_profiles() :
            cadre = Frame(scrollable_frame)
            cadre.pack(fill=X, padx=10, pady=5)

            # Ajouter les titres
            texte_frame = Frame(cadre)
            texte_frame.pack(side=LEFT, padx=10, fill=BOTH, expand=True)

            label_texte1 = Label(texte_frame, text=profil, font=("Arial", 12, "bold"))
            label_texte1.pack(anchor="w")

            # Ajouter un bouton "Supprimer"
            remove_button = Button(cadre, text=t.delete, relief=FLAT, command=lambda p=profil, c=cadre: remove(p, c))
            remove_button.pack(side=RIGHT)
        
    except Exception as e :
        log.error(e + traceback.format_exc())

def help() :
    webbrowser.open('https://github.com/Pythacode/telechargeur_youtube')

entry_color = 'white'

# Fenêtre principale
root = Tk()

icon = PhotoImage(file=Path(res_directory) / "icon" / "32.png")
root.iconphoto(True, icon)

root.title(t.root_title)
root.geometry("1000x500")

# Cadre pour la barre d'URL
EntryFrame = Frame(root, borderwidth=2, relief=SUNKEN, bg=entry_color)
EntryFrame.pack(fill="x", padx=5, pady=2.5)

# Entry pour les URLs
EntryURL = Entry(EntryFrame, relief=FLAT, bg=entry_color)
EntryURL.pack(side=LEFT, fill="x", expand=True)
EntryURL.bind("<Return>", lambda event=None: add_url())

# Boutton "ajouter"
EntryButton = Button(EntryFrame, text=t.add_button, command=add_url, relief=FLAT, bg=entry_color)
EntryButton.pack(side=RIGHT, padx=3.5)

# LabelFrame pour lister les vidéos
MoviesList = LabelFrame(root, text=t.Movie_list_label, relief=GROOVE)
MoviesList.pack(fill="both", expand=True, padx=5, pady=2.5)

# Canvas pour le défilement
MoviesCanva = Canvas(MoviesList, highlightthickness=0)
MoviesCanva.pack(side="left", fill="both", expand=True)

# Barre de défilement verticale
scrollbar = Scrollbar(MoviesList, orient="vertical", command=MoviesCanva.yview)
scrollbar.pack(side="right", fill="y")
MoviesCanva.configure(yscrollcommand=scrollbar.set)

# Frame pour les vidéos à l'intérieur du Canvas
scrollable_frame = Frame(MoviesCanva)
canvas_frame = MoviesCanva.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Ajuster la taille du Canvas en fonction du contenu
def on_frame_configure(event):
    MoviesCanva.configure(scrollregion=MoviesCanva.bbox("all"))

scrollable_frame.bind("<Configure>", on_frame_configure)

# Ajuster la largeur du Canvas au redimensionnement
MoviesCanva.bind("<Configure>", lambda e: MoviesCanva.itemconfig(canvas_frame, width=e.width))

# Button suivant
Next_button = Button(root, text=t.next_button_choice_profil, command=select_profil)
Next_button.pack(side=BOTTOM, fill="x", expand=True, padx=5)

ConfirmLabel = Label(root)
ConfirmLabel.pack_forget()

# Menubar
menubar = Menu(root)

file_menu = Menu(menubar, tearoff=0)

file_menu.add_command(label=t.Modify_Profils_Option, command=profilesEditor)
file_menu.add_separator()
file_menu.add_command(label=t.help, command=help)
file_menu.add_separator()
file_menu.add_command(label=t.quit, command=root.quit)

menubar.add_cascade(label=t.files_menubar, menu=file_menu)

language_menu = Menu(menubar, tearoff=0)

language = [i.removesuffix('.json') for i in os.listdir(lang_directory) if i.endswith('.json')]

for lang in language :
    if lang :
        lang_name = t.languages_list.get(lang)
        language_menu.add_command(label=lang_name, command=lambda l=lang: t.refresh(l))

menubar.add_cascade(label=t.languages, menu=language_menu)

root.config(menu=menubar)

root.mainloop()