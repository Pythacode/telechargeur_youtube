from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QLocale
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QWidget, QLineEdit, QHBoxLayout,
    QFrame, QProgressBar, QScrollArea, QSizePolicy,
    QMessageBox, QComboBox
)
from downloader import Moteur
from context import *
from PySide6.QtGui import QPixmap, QAction, QIcon
import requests
from PySide6.QtGui import QImageReader
from PySide6.QtCore import QByteArray, QBuffer, QIODevice
import webbrowser
from pathlib import Path

class Video(QFrame):

    def __init__(self, title, text, video_id, remove_function, thumbnail_url):
        super().__init__()
        self.video_id = video_id

        self.setObjectName("video")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        main_layout = QHBoxLayout(self)
        hbox_container = QWidget()

        hbox_layout = QVBoxLayout(hbox_container)

        title_label = QLabel(title)
        title_label.setObjectName('Title')
        text_label = QLabel(text)
        button = QPushButton(lang.delete)
        button.clicked.connect(lambda : remove_function(self, video_id))
        button.setObjectName("remove_button")
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        hbox_layout.addWidget(title_label)
        hbox_layout.addWidget(text_label)

        img_label = QLabel()
        img_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        if thumbnail_url :

            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()

            # Charger dans un QPixmap
            pixmap = QPixmap()
            if not pixmap.loadFromData(response.content):
                print("Erreur : Impossible de charger l'image WebP.")
                img_load = False
                
            width = pixmap.width()
            height = pixmap.height()

            new_height = 80
            new_width = int((new_height / height) * width)

            pixmap = pixmap.scaled(new_width, new_height)
            img_load = True
        else :
            img_load = False

        if not img_load :
            pixmap = QPixmap(os.path.join(os.path.join(res_directory, "img"), 'jaquette_default.png'))
        
        img_label.setPixmap(pixmap)

        main_layout.addWidget(img_label)        
        main_layout.addWidget(hbox_container)
        main_layout.addWidget(button)

class Gui(QMainWindow):
    
    signal = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(lang.root_title)
        self.setWindowIcon(QIcon("res/icon/32.png"))
        self.resize(800, 600)
        self.setMinimumSize(400, 300)

        self.title_max_lenght = 35

        # Setup UI

        self.central_widget = QWidget()

        self.setCentralWidget(self.central_widget)

        self.central_layout = QVBoxLayout(self.central_widget)
     
        self.url_entry_frame = self.get_url_entry()
        self.video_list_object = self.get_video_list_container()

        self.central_layout.addWidget(self.url_entry_frame)
        self.central_layout.addWidget(self.video_list_object)
        self.central_layout.addWidget(self.get_footer())

        self.create_menubar()

        # Moteur 

        self.downloader = Moteur()

        self.thread = QThread()
        self.thread.setObjectName("DownloaderThread")

        self.downloader.add_video.connect(self.add_video)
        self.downloader.error_signal.connect(self.error)
        self.downloader.progress_hooks.connect(self.update_dwnl_progress)

        self.downloader.moveToThread(self.thread)

        self.signal.connect(self.downloader.executer)

        self.thread.start()

    def closeEvent(self, event):
        self.thread.quit()
        self.thread.wait()
        log.info("[CLOSE] --------------------------------")
        event.accept()

    def start(self, fonction, *args, **kwargs):
        self.signal.emit((fonction, args, kwargs))

    def error(self, e):
        # Add gestion error pls
        log.error(e)
        QMessageBox.critical(
            self,
            "Error",
            log.remove_colors(str(e))
        )

        self.url_entry.setReadOnly(False)
        self.add_url_button.setDisabled(False)
        self.url_entry.clear()
        self.progressbar.setRange(0, 100)
        
    def add_video(self, data) : 

        duree_secondes = data.get('duration', 0)

        # Formater la durée en HH:MM:SS
        hours = duree_secondes // 3600
        minutes = (duree_secondes % 3600) // 60
        secondes = duree_secondes % 60

        time = f"{minutes:02}:{secondes:02}"
        if hours > 0 :
            time = f"{hours:02}:{time}"

        title = data.get('title', '')
        if len(title) > self.title_max_lenght :
            title = title[:self.title_max_lenght-10] + '...' + title[-7:]
        view_count = data.get('view_count', None)
        subtitlte = (
            data.get('artist', data.get('uploader', lang.artist_not_found))
            + ' · '
            + time
            + ' · '
            + (lang.view_number_not_found if view_count is None else '{:,}'.format(view_count).replace(',', ' '))
            + ' ' + lang.views
        )

        thumbnail_url = None
        best_pref = -float('inf')

        for thumbnail in data.get('thumbnails') :
            if thumbnail.get('preference', -float('inf')) >= best_pref :
                best_pref = thumbnail.get('preference', -float('inf'))
                thumbnail_url = thumbnail.get('url')

        video = Video(title, subtitlte, data.get('id'), self.remove_video, thumbnail_url)
        self.layout_video_list.addWidget(video, alignment=Qt.AlignmentFlag.AlignTop)

        self.next_button.setDisabled(False)
        self.url_entry.setReadOnly(False)
        self.url_entry.clear()
        self.add_url_button.setDisabled(False)
        self.next_button.setDisabled(False)
        self.progressbar.setRange(0, 100)

    def remove_video(self, videoFrame, video_id) :
        self.layout_video_list.removeWidget(videoFrame)
        videoFrame.deleteLater()
        del self.downloader.to_download[video_id]
        if len(self.downloader.to_download) == 0 :
            self.next_button.setDisabled(True)

    def get_url_entry(self) :
        
        frame = QFrame()
        frame.setObjectName("urlEntryContent")
        frame.setFixedHeight(45)

        with open("res/styles/entry_url.qss", "r") as f:
            frame.setStyleSheet(f.read())

        # Url entry
        self.url_layout = QHBoxLayout(frame)

        self.url_entry = QLineEdit()
        self.url_entry.setObjectName("urlEntry")
        self.url_entry.setPlaceholderText("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.add_url_button = QPushButton(lang.add_button)


        self.add_url_button.clicked.connect(self.on_add_url)
        self.url_entry.returnPressed.connect(self.on_add_url)
        
        self.url_layout.addWidget(self.url_entry)
        self.url_layout.addWidget(self.add_url_button)

        return frame

    def help(self) :
        webbrowser.open("https://yt-dlp-gui.nathanaelle.org/")

    def set_languages(self, language_code) :
        lang.refresh(language_code)
        QMessageBox.information(
            self,
            "Information",
            lang.restart_info
        )

    def create_menubar(self) :
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(f"&{lang.files_menubar}")

        profil_editor_action = QAction(f"&{lang.Modify_Profils_Option}", self)
        profil_editor_action.setShortcut("Ctrl+M")
        profil_editor_action.triggered.connect(profiles.profilesEditor)
        profil_editor_action.setDisabled(True)

        help_action = QAction(f"&{lang.help}", self)
        help_action.setShortcut("Ctrl+H")
        help_action.triggered.connect(self.help)

        file_menu.addAction(profil_editor_action)
        file_menu.addAction(help_action)

        file_menu.addSeparator()

        contribute_action = QAction(f"&{lang.contribute}", self)
        contribute_action.triggered.connect(lambda : webbrowser.open('https://github.com/Pythacode/yt-dlp-gui#Contribuer'))

        file_menu.addAction(contribute_action)

        file_menu.addSeparator()

        quit_action = QAction(f"&{lang.quit}", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)

        file_menu.addAction(quit_action)

        settings_menu = menu_bar.addMenu(f"&{lang.settings}")
        languages_menu = settings_menu.addMenu(f"&{lang.languages}")

        language = [i.removesuffix('.yaml') for i in os.listdir(lang_directory) if i.endswith('.yaml')]

        for language_code in language :
            locale = QLocale(language_code)

            name = f"{locale.nativeLanguageName()} ({locale.nativeCountryName()})"

            lang_action = QAction(f"&{name}", self)
            lang_action.triggered.connect(lambda checked=False, code=language_code : self.set_languages(code))
            languages_menu.addAction(lang_action)

    def get_video_list_container(self) :

        video_list = QScrollArea()
        video_list.setObjectName("VideoList")

        self.video_list = QWidget()
        self.layout_video_list = QVBoxLayout(self.video_list)

        video_list.setWidget(self.video_list)
        video_list.setWidgetResizable(True)

        with open("res/styles/video_list.qss", "r") as f:
            video_list.setStyleSheet(f.read())

        self.layout_video_list.setSpacing(10)

        return video_list

    def get_footer(self) :

        footer_frame = QFrame()
        footer = QHBoxLayout(footer_frame)

        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, 100)

        self.next_button = QPushButton(lang.next_button)
        self.next_button.clicked.connect(self.select_profil)
        self.next_button.setObjectName("nextButton")
        self.next_button.setDisabled(True)

        footer.addWidget(self.progressbar)
        footer.addWidget(self.next_button)

        return footer_frame

    def select_profil(self) :
        self.central_layout.removeWidget(self.url_entry_frame)
        self.url_entry_frame.deleteLater()

        videos_frames = self.video_list.findChildren(QFrame, "video")

        available_profiles = profiles.get_profiles()

        for video_frame in videos_frames :
            video_layout = video_frame.findChild(QHBoxLayout, "")

            button = video_frame.findChild(QPushButton, "remove_button")
            button.deleteLater()

            profiles_combo = QComboBox()
            profiles_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            profiles_combo.addItems(available_profiles)
            profiles_combo.currentTextChanged.connect(lambda profil, video_id=video_frame.video_id: self.set_profile_for_video(video_id, profil))

            video_layout.addWidget(profiles_combo)

        self.next_button.setText(lang.download)
        self.next_button.clicked.disconnect()
        self.next_button.clicked.connect(self.download)

    def get_download_advencement_frame(self) :

        frame = QFrame()

        self.advencement_layout = QVBoxLayout(frame)


        self.download_advencement_label = QLabel(lang.download)
        self.download_advencement_label.setAlignment(Qt.AlignCenter)

        self.download_advencement_progressbar = QProgressBar()
        self.download_advencement_progressbar.setRange(0, 0)

        self.global_download_advencement_label = QLabel(lang.total_downloading_progress)
        self.global_download_advencement_label.setAlignment(Qt.AlignCenter)

        self.global_download_advencement_progressbar = QProgressBar()
        self.global_download_advencement_progressbar.setRange(0, 100)

        self.advencement_layout.addWidget(self.download_advencement_label)
        self.advencement_layout.addWidget(self.download_advencement_progressbar)
        self.advencement_layout.addWidget(self.global_download_advencement_label)
        self.advencement_layout.addWidget(self.global_download_advencement_progressbar)

        return frame

    def update_dwnl_progress(self, d) :

        _type = d.get('_type', None)

        if _type == 'next_video' :
            self.current_dl = d['current']
            self.total_dl = d['total']
            percent = ((self.current_dl)*100)/self.total_dl
            text = lang.total_downloading_progress.format(
                nbr=self.current_dl + 1,
                total=self.total_dl,
                pourcent=percent
            )
            self.global_download_advencement_label.setText(text)
            self.global_download_advencement_progressbar.setValue(int(percent))

        elif _type == 'end' :
            self.next_button.setDisabled(False)
            self.global_download_advencement_label.setText(lang.complet_downloading_confim_msg.format(download_folder = download_folder))
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.closeEvent)

        else :

            if d['status'] == 'downloading':
                percent = log.remove_colors(d.get('_percent_str', '0%')).strip().replace('%', ' %')
                current = log.remove_colors(d.get('_downloaded_bytes_str')).strip()
                total = log.remove_colors(d.get('_total_bytes_str')).strip()
                speed = log.remove_colors(d.get('_speed_str', '?')).strip()
                eta = log.remove_colors(d.get('_eta_str', '?')).strip()
                filename = Path(
                    log.remove_colors(
                        d.get('filename', 'unknown')
                    )
                ).stem
                if len(filename) > self.title_max_lenght :
                    filename = filename[:self.title_max_lenght-10] + '...' + filename[-7:]
                
                text = lang.download_progress.format(
                    filename=filename,
                    percent=percent,
                    current=current,
                    total=total,
                    speed=speed,
                    eta=eta
                )

                percent = d.get('_percent', 0)

                self.download_advencement_progressbar.setRange(0, 100)

                self.download_advencement_progressbar.setValue(int(percent))

                percent_per_video = 100/self.total_dl

                percent_global = ((self.current_dl)*100)/self.total_dl + percent * percent_per_video / 100

                self.global_download_advencement_label.setText(
                    lang.total_downloading_progress.format(
                        nbr=self.current_dl + 1,
                        total=self.total_dl,
                        pourcent=round(percent_global, 1)
                    )
                )
                self.global_download_advencement_progressbar.setValue(int(percent_global))

            elif d['status'] == 'finished':
                text = lang.complet_downloading
                self.download_advencement_progressbar.setRange(0, 0)

            self.download_advencement_label.setText(text)

    def download(self) :
        self.video_list_object.deleteLater()
        self.progressbar.deleteLater()
        download_advencement_frame = self.get_download_advencement_frame()
        self.central_layout.insertWidget(0, download_advencement_frame)
        self.next_button.setDisabled(True)
        self.next_button.setText('Fermer')

        self.start(self.downloader.start_download)

    def set_profile_for_video(self, video_id, profil) :
        self.downloader.to_download[video_id] = profil

    def on_add_url(self):
        url = (self.url_entry.displayText())
        if url == '' or url in self.downloader.to_download :
            return

        self.next_button.setDisabled(True)        
        self.url_entry.setReadOnly(True)
        self.add_url_button.setDisabled(True)
        self.progressbar.setRange(0, 0)

        self.start(self.downloader.add_url, url)

