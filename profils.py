from tkinter import *
from tkinter.messagebox import askokcancel
import os
import traceback
from context import lang, root, log, profiles_directory

class Profiles :
    def __init__(self):
        pass

    def profilesEditor(self) :
        try :
            def remove(name, cadre) :
                if askokcancel(self.confirmation, self.remove_profils_confirmation.format(name=name)) :
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
                remove_button = Button(cadre, text=lang.delete, relief=FLAT, command=lambda p=profil, c=cadre: remove(p, c))
                remove_button.pack(side=RIGHT)
            
        except Exception as e :
            log.error(e + traceback.format_exc())

            
        def get_profiles(self) :
            try :
                log.log(profiles_directory)
                return [file.removesuffix('.json').replace('_', ' ') for file in os.listdir(profiles_directory) if os.path.isfile(os.path.join(profiles_directory, file)) and file.endswith('.json') and not ' ' in file]
            except Exception as e :
                log.error(e + traceback.format_exc())

