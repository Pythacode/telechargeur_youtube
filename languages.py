import os
from tkinter.messagebox import showinfo
import json
import locale
from context import configuration, log, lang_directory

class Lang:
    def __init__(self):

        if hasattr(configuration, "lang"):
            language = configuration.lang
        else:
            language = "en_EN"

        log.log(f'Language : {language}')

        path = os.path.join(lang_directory, f"{language}.json")
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
        configuration.updtadeConfig('lang', lang)
        showinfo(self.info, self.restart_info)
