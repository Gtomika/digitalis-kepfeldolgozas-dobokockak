from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import gui_events

# Saját ablak osztály
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        ui: QMainWindow = uic.loadUi('ui/window.ui', self) # A GUI-t tartalmazó fájl betöltése
        self.attachEvents(ui) # események hozzáadása
        self.setWindowIcon(QIcon('ui/dice.ico'))
        self.show() # mutatás

    # Csatolja az eseményeket a gombokhoz, szövegekhez.
    def attachEvents(self, ui: QMainWindow): 
        gui_events.attachEvents(ui)

# A main függvény
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())


