from ntpath import join
from PyQt5.QtWidgets import QCheckBox, QFileDialog, QLabel, QListWidget, QMainWindow, QProgressBar, QPushButton
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDir
import os
import test

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
    # log mentés
    saveLogsButton: QPushButton = ui.saveLogsButton
    saveLogsButton.clicked.connect(lambda: test.onSaveLogsClicked(ui)) 

# a választott mappa útvonala, nem biztos hogy érvényes
_folderPath: str = '-'

# amikor a mappa választó gombot megnyomják
def onFolderSelectClicked(ui: QMainWindow):
    folderPath = QFileDialog.getExistingDirectory(ui, 'Válassz teszt mappát')
    if folderPath == '':
        return
    # egy mappa ki lett választva
    global _folderPath
    _folderPath = QDir.toNativeSeparators(folderPath)
    onFolderSelected(ui, _folderPath)

# ha ki lesz pipálva a checkbox (vagy éppen nem)
def onRecursiveCheckboxChanged(ui: QMainWindow):
    # ha esetleg voltak eredmények
    clearTestResults(ui)
    # van-e mappa választva?
    if _folderPath != '-':
        # van mappa, újra kell vizsgálni
        recursiveCheckbox: QCheckBox = ui.recursiveCheckbox
        recursive = recursiveCheckbox.isChecked()
        analyzeSelectedFolder(ui, _folderPath, recursive)

# amikor ténylegesen lett mappa választva
def onFolderSelected(ui: QMainWindow, folderPath: str):
    # ha esetleg voltak eredmények
    clearTestResults(ui)
    # útvonal mutatása
    folderPathLabel: QLabel = ui.folderPathLabel
    folderPathLabel.setText(folderPath)
    # mappa vizsgálata, hogy jó-e
    recursiveCheckbox: QCheckBox = ui.recursiveCheckbox
    recursive = recursiveCheckbox.isChecked()
    analyzeSelectedFolder(ui, folderPath, recursive)

# a talált képek útvonalai
_imagePaths: list[str] = []

# az eredmény fájl útvonala
_resultPath: str = '-'

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
    global _resultPath
    _resultPath = findResultFile(folderPath)
    # mutatás
    resultFileLabel: QLabel = ui.resultFileLabel
    resultFileLabel.setText(_resultPath)
    # érvényes-e
    summaryLabel: QLabel = ui.testFolderSummary
    launchButton: QPushButton = ui.launchTestButton
    if(_resultPath != '-' and imageCount > 0):
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
        for folder, subfolders, files in os.walk(folderPath):
            for file in files: 
                absolute = os.path.join(folder, file)
                filePaths.append(QDir.toNativeSeparators(absolute))
    else:
        onlyFileNames = os.listdir(folderPath)
        for fileName in onlyFileNames:
            filePaths.append(os.path.join(folderPath, fileName))
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
    if resultPath == '-':
        return resultPath
    else:
        joined = os.path.join(folderPath, resultPath)
        return QDir.toNativeSeparators(joined)

# amikor a teszt indító gombot megnyomják, csak érvényes adatok esetén lehetséges
def onLaunchTestClicked(ui: QMainWindow):
    clearTestResults(ui)
    progressBar: QProgressBar = ui.progressBar
    progressBar.setEnabled(True)
    test.runTests(_resultPath, _imagePaths, ui)

# törli a teszt eredményeket mutató rész tartalmát
def clearTestResults(ui: QMainWindow):
    logWidget: QListWidget = ui.testLogsWidget
    logWidget.clear()
    progressBar: QProgressBar = ui.progressBar
    progressBar.setValue(0)
    progressBar.setEnabled(False)
    saveLogButton: QPushButton = ui.saveLogsButton
    saveLogButton.setEnabled(False)
    successLabel: QLabel = ui.successCountLabel
    successLabel.setText('0')
    failLabel: QLabel = ui.failCountLabel
    failLabel.setText('0')
    notRunLabel: QLabel = ui.notRunCountLabel
    notRunLabel.setText('0')
    percentageLabel: QLabel = ui.successPercentageLabel
    percentageLabel.setText('0%')
