from ui import Gui
from PySide6.QtWidgets import QApplication
from loggeur import Loggeur
from downloader import *

app = QApplication([])
window = Gui()
window.show()
app.exec()