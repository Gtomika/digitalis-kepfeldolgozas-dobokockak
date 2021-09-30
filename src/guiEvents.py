import webbrowser
from PyQt5.QtCore import QFileSelector
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QDialog, QFileDialog, QPushButton
from PyQt5 import uic

# Megkapja a betöltött GUI-t és hozzáadja az eseményeket (kattintás, stb...)
def attachEvents(ui):
    print("Attaching events to the GUI...")
    # Menü sáv gombjainak kezelése
    attachToolbarEvents(ui)
    # Kép választásával kapcsolatos események
    attachFileSelectEvents(ui)

# A menü sáv gombjaihoz ad hozzá eseményeket
def attachToolbarEvents(ui):
    ui.menuGitHubButton.triggered.connect(onGitHubClicked)
    ui.menuMembersButton.triggered.connect(lambda: onMembersClicked(ui))

# Akkor hívódik, ha a GitHub gombra rányomtak
def onGitHubClicked():
    webbrowser.open_new_tab("https://github.com/Gtomika/digitalis-kepfeldolgozas-dobokockak")

# Akkor hívódik ha a csapattagok gombra rányomtak
def onMembersClicked(ui):
    dialog = MembersDialog()
    dialog.exec()

# Egyedi csapattag dialógus ablak
class MembersDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('members_dialog.ui', self)

# Hozzáadja az eseményeket azokhoz a gombokhoz amikkel képet lehet választani
def attachFileSelectEvents(ui):
    imagePreview = ui.imagePreview
    # kép választó gomb
    ui.selectImageButton.clicked.connect(lambda: onFileSelectButtonClicked(ui))
    # kép törlő gomb
    ui.closeImageButton.clicked.connect(lambda: onFileClosed(ui))

# Akkor hívódik, amikor a képválasztó gombra nyomnak
def onFileSelectButtonClicked(ui):
    #fileName két komponens: útvonal és a fájl szűrő ha nem lett megnyitva semmi, akkor üresek
    fileName = QFileDialog.getOpenFileName(ui, 'Kép megnyitása', '', 'Image Files (*.png *.jpg)')
    if fileName[0] == '':
        return
    # útvonal mutató beállítása
    ui.imagePath.setText(fileName[0])
    # kép előnézetének mutatása
    ui.imagePreview.setPixmap(QPixmap(fileName[0]))
    ui.imagePreview.setText('')
    # gombok bekapcsolása
    ui.closeImageButton.setEnabled(True)
    ui.countButton.setEnabled(True)

# Akkor hívódik amikor egy megnyitott képet bezárunk
def onFileClosed(ui):
    # útvonal mutató beállítása
    ui.imagePath.setText('')
    # előnézet törlése
    ui.imagePreview.setPixmap(QPixmap())
    ui.imagePreview.setText('Vagy húzd ide a választott képet!')
    # gombok kikapcsolása
    ui.closeImageButton.setEnabled(False)
    ui.countButton.setEnabled(False)
