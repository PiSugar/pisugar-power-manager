from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
from ui.mainWindowUI import Ui_MainWindow
from core.PiSugarCore import PiSugarCore


battery_percent = 0


class SugarMainWindow(Ui_MainWindow):

    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.editSingleTap.clicked.connect(self.helloworld)
    
    def helloworld(self):
        print("Hello")

    def updateBatteryStatus(self, percent, votage, current, model, battery_is_charging):

        rect = QtCore.QRect(80, 140, int(125 * percent / 100), 65)
        self.greenStatus.setGeometry(rect)
        self.yellowStatus.setGeometry(rect)
        self.redStatus.setGeometry(rect)
        if percent >= 30:
            self.greenStatus.show()
        else:
            self.greenStatus.hide()

        if 10 <= percent < 30:
            self.yellowStatus.show()
        else:
            self.yellowStatus.hide()

        if 0 <= percent < 10:
            self.redStatus.show()
        else:
            self.redStatus.hide()
        _translate = QtCore.QCoreApplication.translate
        self.batteryLabel.setText(_translate("MainWindow", str(int(percent)) + "%"))
        power = int(votage * current * 100) / 100
        if power < 0:
            power = - power
        self.votageLable.setText(_translate("MainWindow", "Power: " + str(round(power, 2)) + "W"))
        charging_str = " [charging]️" if battery_is_charging else ""
        self.modelLabel.setText(_translate("MainWindow", model + charging_str))
        print(percent, votage)


def refresh_battery():
    global battery_percent
    battery_percent = core.get_battery_percent()
    battery_votage = core.get_battery_votage()
    battery_current = core.get_battery_current()
    battery_model = core.get_model()
    battery_is_charging = core.get_battery_charging_status()

    main_window.updateBatteryStatus(battery_percent, battery_votage, battery_current, battery_model, battery_is_charging)
    action_percent.setText("Battery Level: " + str(int(battery_percent)) + "%")
    update_tray_icon(battery_percent, battery_model, battery_is_charging)

    threading.Timer(2.0, refresh_battery).start()


def update_tray_icon(precent, model, is_charging):
    icon_name = "battery_f.svg"
    icon_array = [
        [80, 100, "battery_f.svg"],
        [50, 80, "battery_e.svg"],
        [30, 50, "battery_d.svg"],
        [10, 30, "battery_c.svg"],
        [3, 10, "battery_b.svg"],
        [-1, 3, "battery_a.svg"]
    ]
    for item in icon_array:
        if item[0] < precent <= item[1]:
            icon_name = item[2]
    if is_charging:
        icon_name = "battery_charging.svg"
    if model is None:
        icon_name = "battery_unknown.svg"
    tray.setIcon(QIcon(sys.path[0] + "/icon/" + icon_name))


def open_main_window():
    MainWindow.show()
    MainWindow.activateWindow()


if __name__ == "__main__":
    import sys

    print("Hello world")
    core = PiSugarCore()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("fusion")
    MainWindow = QMainWindow()
    main_window = SugarMainWindow(MainWindow)
    MainWindow.show()

    # Create the tray icon
    tray_icon = QIcon(sys.path[0] + "/icon/battery_f.svg")
    tray = QSystemTrayIcon()
    tray.setIcon(tray_icon)
    tray.setVisible(True)
    tray.setToolTip("PiSugar Power Manager")
    menu = QMenu()
    action_percent = QAction("100%")
    action_percent.setDisabled(True)
    action_open_main = QAction("Main Window")
    action_open_main.triggered.connect(open_main_window)
    # action_exit = QAction("Exit")
    # action_exit.triggered.connect(exit)
    menu.addAction(action_percent)
    menu.addAction(action_open_main)
    # menu.addAction(action_exit)
    tray.setContextMenu(menu)

    # start refreshing battery info
    refresh_battery()

    sys.exit(app.exec_())
