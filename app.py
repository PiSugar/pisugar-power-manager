from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
import time
import os
from core.PiSugarCore import PiSugarCore

SYS_TIME = 0
RTC_TIME = 0
BATTERY_PERCENT = -1
TIME_TYPE = 0
TIME_SET = QtCore.QTime(0, 0)
WEEK_REPEAT = 0b0000000
SHOULD_CLEAN_ALARM = False
SAFE_SHUTDOWN_LEVEL = -1
SAFE_SHUTDOWN_TRIGGERED = False
ICON_FLASH = True


def refresh_battery():
    global BATTERY_PERCENT
    BATTERY_PERCENT = core.get_battery_percent()
    battery_votage = core.get_battery_votage()
    battery_current = core.get_battery_current()
    battery_model = core.get_model()
    battery_is_charging = core.get_battery_charging_status()
    if battery_model != "":
        action_percent.setText(str(int(BATTERY_PERCENT)))
    else:
        action_percent.setText("Unkown Power Source")
    update_tray_icon(BATTERY_PERCENT, battery_model, battery_is_charging)
    threading.Timer(1.0, refresh_battery).start()


def refresh_time():
    global SYS_TIME
    global RTC_TIME
    SYS_TIME = time.time()
    RTC_TIME = core.get_rtc_time()
    threading.Timer(0.5, refresh_time).start()


def update_tray_icon(precent, model, is_charging):
    global ICON_FLASH
    icon_name = "battery_100.svg"
    icon_array = [
        [90, 100, "battery_100.svg"],
        [80, 90, "battery_90.svg"],
        [70, 80, "battery_80.svg"],
        [60, 70, "battery_70.svg"],
        [50, 60, "battery_60.svg"],
        [40, 50, "battery_50.svg"],
        [30, 40, "battery_40.svg"],
        [20, 30, "battery_30.svg"],
        [5, 20, "battery_20.svg"],
        [-1, 5, "battery_5.svg"],
    ]
    for item in icon_array:
        if item[0] < precent <= item[1]:
            icon_name = item[2]
    if is_charging:
        icon_name = "battery_charging.svg"
    # icon_name = "battery_5.svg"
    if icon_name == "battery_5.svg":
        if ICON_FLASH:
            icon_name = "battery_0.svg"
        ICON_FLASH = not ICON_FLASH
    if model == "":
        icon_name = "battery_unknow.svg"
    tray.setIcon(QIcon(sys.path[0] + "/icon/" + icon_name))


def open_main_window():
    print("Open MainWindow")


def logger(log):
    localtime = time.asctime(time.localtime(time.time()))
    f = open('pisugar_log.txt', 'a+')
    new = str(localtime) + " : " + log + "\n"
    print(new)
    f.write(new)
    f.flush()
    f.close()


if __name__ == "__main__":
    import sys

    # initial core
    core = PiSugarCore()

    # create the main window
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("fusion")

    # create the tray icon
    tray_icon = QIcon(sys.path[0] + "/icon/battery_100.svg")
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

    # start refreshing ui
    refresh_battery()
    refresh_time()

    sys.exit(app.exec_())
