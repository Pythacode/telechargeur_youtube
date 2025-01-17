import yt_dlp
from PIL import Image
import requests
from io import BytesIO
from tkinter import *
from PIL import Image, ImageTk
from tkinter.ttk import Progressbar
import threading
import queue
from tkinter.messagebox import askyesno
import os
import json
from pathlib import Path
import traceback

# Détecter le système d'exploitation
if os.name == 'nt':  # Windows
    # Le dossier "Téléchargements" de l'utilisateur sur Windows
    chemin_telechargements = Path(os.environ['USERPROFILE']) / 'Downloads'
elif os.name == 'posix':  # macOS ou Linux
    # Le dossier "Téléchargements" de l'utilisateur sur Linux ou macOS
    chemin_telechargements = Path(os.environ['HOME']) / 'Downloads'
else:
    chemin_telechargements = None

res_directory = 'res' # Chemin du dossier ressources statique
profiles_directory = "profiles" # Chemin des profiles de téléchargement


def download() :
    print(len(scrollable_frame.winfo_children()))
    nbr = 1
    for widget in scrollable_frame.winfo_children(): #Liste les vidéos
        if isinstance(widget, Frame):
            url = None
            while url == None : # Récupère l'url dans le label texte masqué
                
                for child in widget.winfo_children():
                    if isinstance(child, Label):
                        text = child.cget('text')
                        if text.startswith('url:') :
                            url = text[4:]

            for child in widget.winfo_children():
                    
                if isinstance(child, OptionMenu):
                    class YTDLLogger:
                        
                        #Logger personnalisé pour capturer et afficher les messages de yt-dlp.
                        
                        def debug(self, msg):
                            # Affiche les messages de debug
                            ProgresseLabel.config(text=msg)

                        def warning(self, msg):
                            # Affiche les avertissements
                            ProgresseLabel.config(text=f"WARNING: {msg}")

                        def error(self, msg):
                            # Affiche les erreurs
                            ProgresseLabel.config(text=f"ERROR: {msg}")
                            
                    
                    options = json.loads(open(f'{os.path.join(profiles_directory, f'{child.cget('text')}.json')}', 'r').read()) # Récupère le profil choisi
                    #Télécharge la vidéo
                    options["outtmpl"] = os.path.join(chemin_telechargements, options["outtmpl"])

                    options['quiet'] = True,  # Supprime la sortie standard (redirigée vers le logger)
                    options['logger'] = YTDLLogger()
                    options['extract_flat'] = True  # Utilise le logger personnalisé                    

                    # Queue pour recuperer les donnes
                    q = queue.Queue()
                    download_finished = threading.Event()

                    # Fonction qui exécute le téléchargement dans un thread séparé
                    def process_download():
                        try:
                            with yt_dlp.YoutubeDL(options) as ydl:
                                info = ydl.download([url])  # Extraire les métadonnées sans télécharger
                            q.put(info)  # Mettre l'info dans la queue pour être récupérée par le thread principal
                        except Exception as e:
                            error_details = traceback.format_exc()
                            q.put(f"Erreur : {str(e)}\nContexte :\n{error_details}")
                            print(f"Erreur : {str(e)}\nContexte :\n{error_details}")
                        finally:
                            download_finished.set()

                    # Fonction pour vérifier la queue et mettre à jour l'interface
                    def check_queue():
                        try:
                            # Essayer de récupérer l'info sans bloquer
                            info = q.get_nowait()  

                            if isinstance(info, dict):  # Si l'info est un dictionnaire (métadonnées)
                                ProgresseLabel.config(text=f"Dowloading complet")

                            else:  # Si c'est une erreur
                                ProgresseLabel.config(text=info)
                            
                            progress_windows.after(2000, progress_windows.destroy)  # Fermer après 2s

                        except queue.Empty:  # Si la queue est vide, vérifier à nouveau
                            progress_windows.after(100, check_queue)

                    # Création de la fenêtre de progression

                    progress_windows = Toplevel(root)

                    # Barre de progression et label
                    progressBarMetahdonne = Progressbar(progress_windows, orient=HORIZONTAL, length=400, mode='indeterminate')
                    progressBarMetahdonne.pack(side=TOP, fill="x", expand=True)
                    progressBarMetahdonne.start()

                    ProgresseLabel = Label(progress_windows, text="Téléchargement")
                    ProgresseLabel.pack(side=BOTTOM)

                    # Démarrer le téléchargement dans un thread séparé
                    thread = threading.Thread(target=process_download, daemon=True)
                    thread.start()

                    # Lancer la vérification périodique de la queue
                    check_queue()

                    # Boucle pour attendre la fin du téléchargement
                    while not download_finished.is_set():
                        check_queue()
                        progress_windows.update()  # Met à jour l'interface

                    # Fermer la fenêtre de progression après la fin
                    progress_windows.destroy()
        nbr += 1

def select_profil() :
    profiles_files = [f[:-5] for f in os.listdir(profiles_directory) if os.path.isfile(os.path.join(profiles_directory, f)) and f.endswith('.json')]
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, Frame):
            for child in widget.winfo_children(): # Retire le boutton suprimer
                if isinstance(child, Button):
                    child.pack_forget()

            # Ajoute une selection de profil
            
            selected_profile = StringVar(root)

            # Définir une valeur initiale pour la variable
            selected_profile.set(profiles_files[0])

            # Création de l'OptionMenu pour la sélection
            option_menu = OptionMenu(widget, selected_profile, *profiles_files)
            option_menu.pack()

            
    EntryFrame.pack_forget()
    Next_button.config(text="Téléchargement", command=download)


def add_url(url=False, dowload_playlist=False):

    #Ajoute un classe pour intercepter les logs de yt_dlp et les afficher dans une fenetre séparer
    class YTDLLogger:
        """
        Logger personnalisé pour capturer et afficher les messages de yt-dlp.
        """
        def debug(self, msg):
            # Affiche les messages de debug
            ProgresseLabel.config(text=msg)

        def warning(self, msg):
            # Affiche les avertissements
            ProgresseLabel.config(text=f"WARNING: {msg}")

        def error(self, msg):
            # Affiche les erreurs
            ProgresseLabel.config(text=f"ERROR: {msg}")

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
            info.get('artist', info.get('uploader', 'Artiste indisponible'))
            + ' · '
            + f"{heures:02}:{minutes:02}:{secondes:02}"
            + ' · '
            + ('Nombre de vues indisponible' if view_count is None else '{:,}'.format(view_count).replace(',', ' '))
            + ' vues'
        )


        thumbnail_url = info.get('thumbnail')
        
        if is_playlist :
            title = '[Playlist] ' + title
            subtitlte += ' · ' + str(info.get('playlist_count', 'Nombre de vidéo indisponible')) + ' vidéos'
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
        menu_button = Button(cadre, text="Supprimer", relief=FLAT, command=cadre.destroy)
        menu_button.pack(side=RIGHT)
    
    #Récuperer l'url si non fournie comme argument
    if not url:
        url = EntryURL.get()
        if '&list=' in url :
            if askyesno('Playlist', 'Attention, vous vous apretez à ajouter une playlist générer automatiquement par youtube, Pour garder uniquement la vidéo que vous regardiez, appuyer sur oui, si vous voulez télecharger la playlist, appuyer sur non.') :
                url = url.split('&list=')[0]

    # Effacer l'entrée URL
    EntryURL.delete(0, END)

    ydl_opts = {
            'quiet': True,  # Supprime la sortie standard (redirigée vers le logger)
            'logger': YTDLLogger(),
            'extract_flat': True,  # Utilise le logger personnalisé
        }
    
    if dowload_playlist : 
        ydl_opts['extract_flat'] = False

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
                ProgresseLabel.config(text=f"Dowloading complet")

                if info.get('_type', None) == 'playlist' : #Si c'est une playlist
                    if dowload_playlist : # Vérifie si l'utilisateur a déja répondus a la question suivante
                        for video in info.get('entries') :
                            add_movies(video)
                    elif askyesno('Playlist', f"L'URL que vous avez fourni est une playlist, voulez-vous l'ajouter en tant que playlist ou en plusieurs vidéos ?\nAttention, en fonction du nombre de vidéos (ici {str(info.get('playlist_count', 'Nombre de vidéo indisponible'))}), cette opération peut prendre du temps\n\n(Oui -> playliste / Non -> Vidéos)") : #Demande a l'utilisateur si on ajoute chaque vidéo séparément
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

    ProgresseLabel = Label(progress_windows, text="Téléchargement")
    ProgresseLabel.pack(side=BOTTOM)

    # Démarrer le téléchargement dans un thread séparé
    thread = threading.Thread(target=process_download, daemon=True)
    thread.start()

    # Lancer la vérification périodique de la queue
    check_queue()

    # Mainloop Tkinter
    root.mainloop()

# Fenêtre principale
root = Tk()
root.title("Téléchargeur YouTube")
root.geometry("1000x500")

# Cadre pour la barre d'URL
EntryFrame = Frame(root)
EntryFrame.pack(fill="x", padx=5, pady=2.5)

# Entry pour les URLs
EntryURL = Entry(EntryFrame)
EntryURL.pack(side=LEFT, fill="x", expand=True, padx=2.5)
EntryURL.bind("<Return>", lambda event=None: add_url())

# Boutton "ajouter"
EntryButton = Button(EntryFrame, text="Ajouter", command=add_url)
EntryButton.pack(side=RIGHT, padx=3.5)

# LabelFrame pour lister les vidéos
MoviesList = LabelFrame(root, text="Vidéos à télécharger", relief=GROOVE)
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
Next_button = Button(root, text="Choisir le profil de téléchargement", command=select_profil)
Next_button.pack(side=BOTTOM, fill="x", expand=True, padx=5, pady=2.5)

root.mainloop()
