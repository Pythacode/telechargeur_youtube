import os
from tkinter.messagebox import showinfo
import yaml
from context import configuration, log, lang_directory

class Lang:
    def __init__(self):

        if hasattr(configuration, "lang"):
            language = configuration.lang
        else:
            language = "en_EN"

        log.log(f'Language : {language}')

        path = os.path.join(lang_directory, f"{language}.yaml")
        try:
            with open(os.path.join(lang_directory, "fr_FR.yaml"), 'r', encoding="utf-8") as file :
                ref = yaml.safe_load(file)

            with open(path, 'r', encoding="utf-8") as file :
                translations = yaml.safe_load(file)

            cles = translations.keys()
            ref_keys = ref.keys()     
                
            for cle in ref_keys :
                if cle in cles :
                    setattr(self, cle, translations[cle])
                else :
                    log.warnig(f'Key \"{cle}\" not found in {language}.yaml.')
                    setattr(self, cle, translations[cle])


        except Exception as e:
            log.error(f"Erreur de chargement des traductions : {e}")
            return self.__init__()
    
    def refresh(self, lang) :
        configuration.updtadeConfig('lang', lang)
        showinfo(self.info, self.restart_info)
