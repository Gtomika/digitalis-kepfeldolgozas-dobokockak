from pathlib import Path
from PyQt5.QtCore import QDir, QThread, QUrl
from PyQt5.QtWidgets import QFileDialog, QLabel, QListWidget, QMainWindow, QProgressBar, QPushButton
import time
from algorithms.segment_count.dice_counter import count_dices

# egy kép neve és az arra elvárt eredmény
class ExpectedResult:
    def __init__(self, imageName: str, expected: int) -> None:
        self.imageName = imageName
        self.expected = expected

# a tesztek logjai, hogy később fájlba lehessen menteni
_testLogs: list[str] = []

_logSignal = None

_ui = None

def runTests(resultFile: str, imagePaths: list[str], ui: QMainWindow, logSignal, successSignal, failSignal, notRunSignal, displayResultSignal, progressSignal, preSignal):
    preSignal.emit(len(imagePaths), ui)
    # időmérés 
    startTime = time.time()
    # logolás előkészítése
    global _testLogs
    _testLogs.clear()
    global _logSignal
    _logSignal = logSignal
    global _ui
    _ui = ui
    logStart(resultFile, len(imagePaths))
    # elvárt eredmények olvasása (NEM biztos, hogy minden képhez talált elvárt eredményt)
    log('Elvárt eredmények beolvasása az eredményfájlból...')
    expectedResults = readResults(resultFile)
    log('A ' + str(len(imagePaths)) + ' képből ' + str(len(expectedResults)) + ' darabhoz sikerült elvárt eredményt találni az eredményfájlban.')
    # végigmegy az összes képen, és teszteli őket
    log('Kezdődik a képek tesztelése...')
    success = 0
    fail = 0
    notRun = 0
    counter = 1
    for imagePath in imagePaths:
        log(str(counter) + '. kép tesztelése: ' + imagePath)
        status = runTest(imagePath, expectedResults)
        if status == SUCCESS:
            success += 1
            successSignal.emit(success, ui)
        elif status == FAIL:
            fail += 1
            failSignal.emit(fail, ui)
        elif status == NOT_RUN:
            notRun += 1
            notRunSignal.emit(notRun, ui)
        else: # nem fordul elő?
            notRun += 1
            notRunSignal.emit(notRun, ui)
        progressSignal.emit(counter, ui)
        counter += 1
    # teszteredmények
    percentageNum = round(success / (success+fail), 2)
    successPercentage = str(percentageNum * 100) + '%'
    # időmérés vége
    endTime = time.time()
    elapsed = endTime - startTime
    # eredmények logolása
    logResults(success, fail, notRun, successPercentage, elapsed)
    # eredmények mutatása az UI-n
    displayResultSignal.emit(successPercentage, _testLogs, ui)

# eredmény konstansok
SUCCESS = 0
FAIL = -1
NOT_RUN = 1

# egy konkrét teszt futtatása, az egyik eredmény konstansot adja vissza
def runTest(imagePath: str, expectedResults: list[ExpectedResult]) -> int:
    expected = findExpectedResultForImage(imagePath, expectedResults)
    if expected == -1:
        log('Ehhez a képhez nem található elvárt eredmény, ezért ki lesz hagyva.')
        return NOT_RUN
    try:
        # itt kell meghívni a számoló algoritmust
        # ez nem mutat részeredményeket, az nagyon sok kép lenne minden tesztesetre
        result = count_dices(imagePath, False)
    except Exception as e:
        log('Hiba a kép tesztelése közben: ' + str(e))
        return NOT_RUN
    # kiértékelés
    if result == expected:
        log('Sikeres teszt, az elvárt és a kapott eredmény is ' + str(result) + '.')
        return SUCCESS
    else:
        log('Bukott teszt, az elvárt eredmény ' + str(expected) + ' volt, de ' + str(result) + ' lett detektálva.')
        return FAIL

# adott képhez megkeresi a listából az elvárt eredményt. -1-et ad vissza ha nem találta
def findExpectedResultForImage(imagePath: str, expectedResults: list[ExpectedResult]) -> int:
    for expectedResult in expectedResults:
        # csak fájlnév, kiterjesztés nélkül
        path = Path(imagePath)
        path.with_suffix('')
        if expectedResult.imageName == path.stem:
            return expectedResult.expected
    return -1

# beolvassa az eredményeket
def readResults(resultFile: str) -> list[ExpectedResult]:
    with open(resultFile, 'r') as file:
        lines = file.readlines()
    lineCounter = 1
    expectedResults: list[ExpectedResult] = []
    for line in lines:
        splitLine = line.split(';')
        if len(splitLine) == 2:
            expectedCount = parseExpected(splitLine[1])
            if(expectedCount != -1):
                # minden adat jó
                expectedResults.append(ExpectedResult(splitLine[0], expectedCount))
            else:
                log('A ' + str(lineCounter) + '. sor hibás az eredményfájlban: ' + line)
        else:
            log('A ' + str(lineCounter) + '. sor hibás az eredményfájlban: ' + line)
        lineCounter += 1
    return expectedResults

# ha sikertelen akkor -1-et ad vissza
def parseExpected(s):
    try:
        return int(s)
    except ValueError:
        return -1

# formázott dátum
def getCurrentDateString() -> str:
    current = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', current)

# formázott idő
def getCurrentTimeString() -> str:
    current = time.localtime()
    return time.strftime('%H:%M:%S', current)

# egy új logot jelenít meg (a log listához is hozzáírja)
def log(message: str):
    _testLogs.append(getCurrentTimeString() + ': ' + message + '\n')
    _logSignal.emit(message, _ui)

# teszt indítási információkat logol
def logStart(resultPath: str, imageCount: int):
    log('Tesztelés indul: ' + getCurrentDateString())
    log('Összesen ' + str(imageCount) + ' kép lesz tesztelve.')
    log('A helyes eredményeket tartalmazó fájl: ' + resultPath)
    log('------------------------------------------------------')

# teszt eredményeket logol
def logResults(success: int, fail: int, notRun: int, successPercentage: str, time: int):
    log('------------------------------------------------------')
    log('A tesztelés eredménye:')
    log('Sikeres tesztek: ' + str(success))
    log('Bukott tesztek: ' + str(fail))
    log('Nem futtatott tesztek: ' + str(notRun))
    if notRun > 0:
        log('A sikertelen futtatás okaiért lásd a logokat.')
    log('Sikerességi százalék: ' + str(successPercentage))
    log('Tesztelés időtartama: ' + str(time) + ' másodperc.')