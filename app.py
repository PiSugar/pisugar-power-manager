from PyQt5 import QtCore, QtGui, QtWidgets
import threading
from ui.mainWindowUI import Ui_MainWindow
from core.PiSugarCore import PiSugarCore


class SugarMainWindow(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.editSingleTap.clicked.connect(self.helloworld)
    
    def helloworld(self):
        print("Hello")


def refresh_battery():
    print(core.get_battery_percent())
    threading.Timer(2.0, refresh_battery).start()


if __name__ == "__main__":
    import sys

    print("Hello world")
    core = PiSugarCore()
    refresh_battery()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    win = SugarMainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    print("Bye world")