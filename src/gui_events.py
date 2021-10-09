import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPixmap

from PyQt5.QtWidgets import QAction, QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QPushButton, QVBoxLayout
from PyQt5 import uic
import threading
import time

# kép megjelenítő
class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        self.setText('Kép előnézet')
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''
            QLabel {
                border: 4px dashed black
            }
        ''')

# Megkapja a betöltött GUI-t és hozzáadja az eseményeket (kattintás, stb...)
def attachEvents(ui: QMainWindow):
    print("Attaching events to the GUI...")
    # Menü sáv gombjainak kezelése
    attachToolbarEvents(ui)
    # Kép választásával kapcsolatos események
    attachFileSelectEvents(ui)
    # a kép számolását indító gomb
    countButton: QPushButton = ui.countButton
    countButton.clicked.connect(lambda: onCountClicked(ui))

# A menü sáv gombjaihoz ad hozzá eseményeket
def attachToolbarEvents(ui: QMainWindow):
    githubAction: QAction = ui.menuGitHubButton
    githubAction.triggered.connect(onGitHubClicked)
    membersAction: QAction = ui.menuMembersButton
    membersAction.triggered.connect(onMembersClicked)

# Akkor hívódik, ha a GitHub gombra rányomtak
def onGitHubClicked():
    webbrowser.open_new_tab("https://github.com/Gtomika/digitalis-kepfeldolgozas-dobokockak")

# Akkor hívódik ha a csapattagok gombra rányomtak
def onMembersClicked():
    dialog = MembersDialog()
    dialog.exec()

# Egyedi csapattag dialógus ablak
class MembersDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/members_dialog.ui', self)

# Hozzáadja az eseményeket azokhoz a gombokhoz amikkel képet lehet választani
def attachFileSelectEvents(ui: QMainWindow):
    # kép előnézet hozzáadása
    imagePreview = ImagePreview()
    layout: QVBoxLayout = ui.imagePreviewLayout
    layout.addWidget(imagePreview)
    # kép választó gomb
    selectButton: QPushButton = ui.selectImageButton
    selectButton.clicked.connect(lambda: onFileSelectButtonClicked(ui, imagePreview))
    # kép törlő gomb
    closeButton: QPushButton = ui.closeImageButton
    closeButton.clicked.connect(lambda: onFileClosed(ui, imagePreview))

# Akkor hívódik, amikor a képválasztó gombra nyomnak
def onFileSelectButtonClicked(ui: QMainWindow, imagePreview: ImagePreview):
    #fileName két komponens: útvonal és a fájl szűrő ha nem lett megnyitva semmi, akkor üresek
    fileName = QFileDialog.getOpenFileName(ui, 'Kép megnyitása', '', 'Image Files (*.png *.jpg)')
    if fileName[0] == '':
        return
    # útvonal mutató beállítása
    path: QLabel = ui.imagePath
    path.setText(fileName[0])
    # kép előnézetének mutatása
    imagePreview.setPixmap(QPixmap(fileName[0]))
    # gombok bekapcsolása
    closeButton: QPushButton = ui.closeImageButton
    closeButton.setEnabled(True)
    countButton: QPushButton = ui.countButton
    countButton.setEnabled(True)

# Akkor hívódik amikor egy megnyitott képet bezárunk
def onFileClosed(ui: QMainWindow, imagePreview: ImagePreview):
    # útvonal mutató beállítása
    path: QLabel = ui.imagePath
    path.setText('')
    # előnézet törlése
    imagePreview.setPixmap(QPixmap())
    imagePreview.setText('Kép előnézet')
    # gombok kikapcsolása
    closeButton: QPushButton = ui.closeImageButton
    closeButton.setEnabled(False)
    countButton: QPushButton = ui.countButton
    countButton.setEnabled(False)
    # ha van eredmény, akkor annak a törlése
    resultLabel: QLabel = ui.result
    resultLabel.setText('-')
    timeLabel: QLabel = ui.time
    timeLabel.setText('-')

# Akkor hívódik amikor a számolás indítására nyomunk
def onCountClicked(ui: QMainWindow):
    ui.setEnabled(False)
    QApplication.setOverrideCursor(Qt.WaitCursor)
    # számolás a HÁTTÉRBEN
    thread = threading.Thread(target=executeCountingOperation, args=[ui])
    thread.setDaemon(True)
    thread.start()

# A számoló függvény ami a háttérben fut
def executeCountingOperation(ui: QMainWindow):
    # időmérés indítása
    startTime = time.time()
    # TODO: ez csak várakozik, helyette az igazik számolás kell!
    time.sleep(2)
    count = 3
    # időmérés leállítása
    endTime = time.time()
    elapsed = round(endTime - startTime, 5)
    # UI frissítése az eredményekkel
    resultLabel: QLabel = ui.result
    resultLabel.setText(str(count))
    timeLabel: QLabel = ui.time
    timeLabel.setText(str(elapsed) + ' másodperc')
    ui.setEnabled(True)
    QApplication.restoreOverrideCursor()


