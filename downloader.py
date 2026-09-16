from PySide6.QtCore import QObject, Signal, Slot
import time
from context import *
import yt_dlp
import json

class Moteur(QObject):

    add_video = Signal(object)
    error_signal = Signal(object)
    progress_hooks = Signal(dict)

    @Slot(object)
    def executer(self, message):
        fonction, args, kwargs = message

        fonction(*args, **kwargs)
    
    def __init__(self):
        super().__init__()
        self.to_download = {}
        self.browser_name = None
        self.browser_name = configuration.get('cookies_browser', None)

    def add_url(self, url):
        
        log.info(f"NEW URL : {url}")

        ydl_opts = {
                'quiet': True, 
                'logger': log, 
                'skip_download' : True,
        }


        if self.browser_name :
            ydl_opts['cookies-from-browser'] = self.browser_name

        try :
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e :
            self.error_signal.emit(e)
            return

        self.to_download[info['id']] = profiles.get_profiles()[0]
        #info = json.loads(open("info.exmpl.json", 'r').read())
        self.add_video.emit(info)

    def handle_progress(self, data):
        self.progress_hooks.emit(data)

    def set_nav_for_cookies(self, nav_name) :
        if nav_name == lang.none :
            self.browser_name = None
        else :
            self.browser_name = nav_name.lower()
        configuration.updtadeConfig('cookies_browser', self.browser_name)

    def start_download(self):
        for  index, (url, profil) in enumerate(self.to_download.items()) :

            data = {
                '_type' : 'next_video',
                'total' : len(self.to_download),
                'current' : index
            }

            self.progress_hooks.emit(data)

            log.info(f"Start download of url \"{url}\" with profile \"{profil}\"")

            option_file = os.path.join(profiles_directory, f"{profil.replace(' ', '_')}.json")
            options = json.loads(open(option_file, 'r').read())
            options["outtmpl"] = os.path.join(download_folder, options["outtmpl"])

            options['quiet'] = True
            options['logger'] = log
            options['progress_hooks'] = [self.handle_progress]
            options['extract_flat'] = True
            if self.browser_name :
                options['cookies-from-browser'] = self.browser_name

            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    info = ydl.download([url])
            except Exception as e:
                self.error_signal.emit(e)
                log.error(str(e))        
                        
        data = {
            '_type' : 'end'
        }

        self.progress_hooks.emit(data)
