from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def main():
    application = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(100, 100, 300, 300)
    window.setWindowTitle('Dobókockák')

    label = QtWidgets.QLabel(window)
    label.setText('Helló!')
    label.move(10,10)

    window.show()
    sys.exit(application.exec_())

main()