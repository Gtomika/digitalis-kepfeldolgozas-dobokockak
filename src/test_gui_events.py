import time
from PyQt5.QtWidgets import QCheckBox, QFileDialog, QLabel, QListWidget, QMainWindow, QProgressBar, QPushButton
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDir, QThread, QUrl, pyqtSignal
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
    saveLogsButton.clicked.connect(lambda: onSaveLogsClicked(ui)) 

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

#amikor a háttérszál logolni akar ezt hívja
def onLog(message: str, ui: QMainWindow):
    logWidget: QListWidget = ui.testLogsWidget
    logWidget.addItem(message)
    logWidget.update()

def onSuccess(count: int, ui: QMainWindow):
    successLabel: QLabel = ui.successCountLabel
    successLabel.setText(str(count))
    successLabel.update()

def onFail(count: int, ui: QMainWindow):
    failLabel: QLabel = ui.failCountLabel
    failLabel.setText(str(count))
    failLabel.update()

def onNotRun(count: int, ui: QMainWindow):
    notRunLabel: QLabel = ui.notRunCountLabel
    notRunLabel.setText(str(count))
    notRunLabel.update()

def displayResults(successPercentage: str, logs: list, ui: QMainWindow):
    percentageLabel: QLabel = ui.successPercentageLabel
    percentageLabel.setText(successPercentage)
    # mentés gomb engedélyezése
    saveLogsButton: QPushButton = ui.saveLogsButton
    saveLogsButton.setEnabled(True)
    launchButton: QPushButton = ui.launchTestButton
    launchButton.setEnabled(True)
    #logok mentése
    global _logs
    _logs = logs

#PyQt5 szál osztály
class TestRunner(QThread):

    on_log_signal = pyqtSignal(str, QMainWindow)

    on_success_signal = pyqtSignal(int, QMainWindow)

    on_fail_signal = pyqtSignal(int, QMainWindow)

    on_not_run_signal = pyqtSignal(int, QMainWindow)

    on_display_results_signal = pyqtSignal(str, list, QMainWindow)

    on_progress_signal = pyqtSignal(int, QMainWindow)

    on_pre_signal = pyqtSignal(int, QMainWindow)

    def __init__(self, ui: QMainWindow):
        QThread.__init__(self)
        self.ui = ui

    def run(self):
        test.runTests(_resultPath, _imagePaths, self.ui, self.on_log_signal, self.on_success_signal, self.on_fail_signal,
                 self.on_not_run_signal, self.on_display_results_signal, self.on_progress_signal, self.on_pre_signal)

def onPreTesting(max, ui: QMainWindow):
    percentageLabel: QLabel = ui.successPercentageLabel
    percentageLabel.setText('...')
    launchButton: QPushButton = ui.launchTestButton
    launchButton.setEnabled(False)
    progressBar: QProgressBar = ui.progressBar
    progressBar.setMinimum(0)
    progressBar.setMaximum(max)
    progressBar.setEnabled(True)
    progressBar.setValue(0)

def onProgress(counter: int, ui: QMainWindow):
    progressBar: QProgressBar = ui.progressBar
    progressBar.setValue(counter)
    progressBar.update()

_logs: list[str] = []

# amikor a mentés gombra kattintunk, akkor az eredmények el lesznek mentve a választott fájlba
def onSaveLogsClicked(ui: QMainWindow):
    defaultName = QUrl.fromLocalFile('testlog_' + str(int(time.time())) + '.log')
    logFile = QFileDialog.getSaveFileUrl(ui, caption='Log mentése', directory=defaultName, filter='Log fájlok (*.log)')
    logFilePath = logFile[0].toLocalFile()
    if(logFilePath == ''):
        return
    logFilePath = QDir.toNativeSeparators(logFilePath)
    with open(logFilePath, 'w+') as f:
        f.writelines(_logs)

_testRunner = None

# amikor a teszt indító gombot megnyomják, csak érvényes adatok esetén lehetséges
def onLaunchTestClicked(ui: QMainWindow):
    clearTestResults(ui)
    progressBar: QProgressBar = ui.progressBar
    progressBar.setEnabled(True)
    global _testRunner
    # szál létrehozása
    _testRunner = TestRunner(ui)
    # háttér események kapcsolása
    _testRunner.on_log_signal.connect(onLog)
    _testRunner.on_success_signal.connect(onSuccess)
    _testRunner.on_fail_signal.connect(onFail)
    _testRunner.on_not_run_signal.connect(onNotRun)
    _testRunner.on_display_results_signal.connect(displayResults)
    _testRunner.on_pre_signal.connect(onPreTesting)
    _testRunner.on_progress_signal.connect(onProgress)
    # indítás
    _testRunner.start()
    

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
