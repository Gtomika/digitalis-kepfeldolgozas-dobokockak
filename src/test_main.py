from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import test_gui_events
import os

# Nálam nem működött a relatív útvonal, mert a jelenlegi munkakönyvtár nem ez a 
# a mappa volt, hanem az src mappa. Átírtam úgy az útvonalakat, hogy ott keressék a 
# fájlokat és mappákat, ahol EZ a forrásfájl van.
# Továbbá a / jel helyett mindhol a join függvényt írtam - Tamás
fileDir = os.path.dirname(os.path.realpath(__file__))

# Teszt ablak osztály
class TestWindow(QMainWindow):
    def __init__(self):
        super(TestWindow, self).__init__()
        ui: QMainWindow = uic.loadUi(os.path.join(fileDir, 'ui', 'test_window.ui'), self) # A GUI-t tartalmazó fájl betöltése
        self.attachEvents(ui) # események hozzáadása
        self.setWindowIcon(QIcon(os.path.join(fileDir, 'ui', 'dice.ico')))
        self.show() # mutatás

    # Csatolja az eseményeket a gombokhoz, szövegekhez.
    def attachEvents(self, ui: QMainWindow): 
        test_gui_events.attachEvents(ui)

# A main függvény
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    sys.exit(app.exec_())