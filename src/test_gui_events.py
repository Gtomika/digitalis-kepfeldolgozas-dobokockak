from PyQt5.QtWidgets import QCheckBox, QFileDialog, QLabel, QMainWindow, QPushButton
from PyQt5.QtWidgets import QMainWindow
import os

def attachEvents(ui: QMainWindow):
    # mappaválasztás
    folderSelectButton: QPushButton = ui.selectFolderButton
    folderSelectButton.clicked.connect(lambda: onFolderSelectClicked(ui))
    # rekurzív változtatás
    recursiveCheckbox: QCheckBox = ui.recursiveCheckbox
    recursiveCheckbox.stateChanged.connect(lambda: onRecursiveCheckboxChanged(ui))
    # teszt indítás
    launchTestButton: QPushButton = ui.launchTestButton
    launchTestButton.clicked.connect(lambda: onLaunchTestClicked(ui))

# a választott mappa útvonala, nem biztos hogy érvényes
_folderPath: str = '-'

# amikor a mappa választó gombot megnyomják
def onFolderSelectClicked(ui: QMainWindow):
    folderPath = QFileDialog.getExistingDirectory(ui, 'Válassz teszt mappát')
    if folderPath == '':
        return
    # egy mappa ki lett választva
    global _folderPath
    _folderPath = folderPath
    onFolderSelected(ui, folderPath)

# ha ki lesz pipálva a checkbox (vagy éppen nem)
def onRecursiveCheckboxChanged(ui: QMainWindow):
    # van-e mappa választva?
    if _folderPath != '-':
        # van mappa, újra kell vizsgálni
        recursiveCheckbox: QCheckBox = ui.recursiveCheckbox
        recursive = recursiveCheckbox.isChecked()
        analyzeSelectedFolder(ui, _folderPath, recursive)

# amikor ténylegesen lett mappa választva
def onFolderSelected(ui: QMainWindow, folderPath: str):
    # útvonal mutatása
    folderPathLabel: QLabel = ui.folderPathLabel
    folderPathLabel.setText(folderPath)
    # mappa vizsgálata, hogy jó-e
    recursiveCheckbox: QCheckBox = ui.recursiveCheckbox
    recursive = recursiveCheckbox.isChecked()
    analyzeSelectedFolder(ui, folderPath, recursive)

# a talált képek útvonalai
_imagePaths: list[str] = []

# mappa vizsgálata: van-e benne kép, eredmény fájl, stb. UI-t is firssíti
def analyzeSelectedFolder(ui: QMainWindow, folderPath: str, recursive: bool):
    # képek keresése és megszámolása
    global _imagePaths
    _imagePaths = findImages(folderPath, recursive)
    imageCount = len(_imagePaths)
    #mutatás
    imageCountLabel: QLabel = ui.imageCountLabel
    imageCountLabel.setText(str(imageCount))
    # eredmény fájl keresése
    resultFile = findResultFile(folderPath)
    # mutatás
    resultFileLabel: QLabel = ui.resultFileLabel
    resultFileLabel.setText(resultFile)
    # érvényes-e
    summaryLabel: QLabel = ui.testFolderSummary
    launchButton: QPushButton = ui.launchTestButton
    if(resultFile != '-' and imageCount > 0):
        summaryLabel.setStyleSheet('color: green;')
        summaryLabel.setText('A választott mappa megfelelő.')
        # teszt gomb bekapcsolása
        launchButton.setEnabled(True)
    else:
        summaryLabel.setStyleSheet('color: red;')
        summaryLabel.setText('A választott mappa érvénytelen.')
         # teszt gomb kikapcsolása
        launchButton.setEnabled(False)

# megfelelő formátumú képek számolása és az útvonalak begyűjtése
def findImages(folderPath: str, recursive: bool) -> list :
    imgPaths: list[str] = []
    filePaths: list[str] = []
    # rekurzív, vagy nem
    if recursive:
        for root, dirs, files in os.walk(folderPath):
            for file in files: 
                filePaths.append(file)
    else:
        filePaths = os.listdir(folderPath)
    # képek keresése
    for file in filePaths:
        if file.endswith('.png') or file.endswith('.jpg'):
                imgPaths.append(file)
    return imgPaths

# így kell hogy hívják az eredmény fájlt!
resultFolderName = 'values.txt'

# adott mappában keresi az eredmény fájlt. '-'et ad vissza ha nem találja
def findResultFile(folderPath: str) -> str:
    resultPath = '-'
    files = os.listdir(folderPath)
    for file in files:
        if file == resultFolderName:
            resultPath = file
    return resultPath

# amikor a teszt indító gombot megnyomják
def onLaunchTestClicked(ui: QMainWindow):
    print('TODO')