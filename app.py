from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
import time
from ui.mainWindowUI import Ui_MainWindow
from ui.repeatForm import Ui_RepeatForm
from core.PiSugarCore import PiSugarCore

SYS_TIME = 0
RTC_TIME = 0
BATTERY_PERCENT = 0
TIME_TYPE = 0
TIME_SET = QtCore.QTime(0, 0)
WEEK_REPEAT = 0b0000000
SHOULD_CLEAN_ALARM = False


class SugarMainWindow(Ui_MainWindow):

    def __init__(self, MainWindow):
        super().setupUi(MainWindow)

        self.timeType.currentIndexChanged.connect(self.time_type_change)
        self.timeEdit.setDisplayFormat("hh:mm:ss")
        self.timeEdit.timeChanged.connect(self.time_change)
        self.timeType.setCurrentIndex(TIME_TYPE)
        self.actionSync_Time_Pi_to_RTC.triggered.connect(self.sync_time_pi_rtc)
        self.timeReapeat.clicked.connect(self.open_repeat_win)
        self.check_clock_set()

    def time_type_change(self, index):
        global TIME_TYPE
        TIME_TYPE = index
        if index != 1:
            RepeatForm.hide()
        self.check_clock_set()

    def time_change(self, time):
        global TIME_SET
        TIME_SET = time
        self.check_clock_set()

    def open_repeat_win(self):
        RepeatForm.show()
        RepeatForm.activateWindow()

    def check_clock_set(self):
        _translate = QtCore.QCoreApplication.translate
        global TIME_SET
        global TIME_TYPE
        global WEEK_REPEAT
        global SHOULD_CLEAN_ALARM
        if TIME_TYPE == 1:
            self.timeEdit.setDisabled(False)
            self.timeReapeat.setDisabled(False)
            time_to_set = core.read_time()
            time_to_set[0] = TIME_SET.second()
            time_to_set[1] = TIME_SET.minute()
            time_to_set[2] = TIME_SET.hour()
            core.clock_time_set(time_to_set, WEEK_REPEAT)
            SHOULD_CLEAN_ALARM = WEEK_REPEAT == 0
            core.clean_clock_flag()
            self.clockMsg.setText(_translate("MainWindow", self.get_clock_msg()))
        else:
            self.timeEdit.setDisabled(True)
            self.timeReapeat.setDisabled(True)
            self.clockMsg.setText(_translate("MainWindow", "Auto Boot Off"))

    def get_clock_msg(self):
        global WEEK_REPEAT
        if WEEK_REPEAT == 0b1111111:
            return "Everyday"
        if WEEK_REPEAT == 0b0000000:
            return "Once"
        alarm_week = []
        if WEEK_REPEAT & 0b0000001 == 0b0000001:
            alarm_week.append("Sun")
        if WEEK_REPEAT & 0b0000010 == 0b0000010:
            alarm_week.append("Mon")
        if WEEK_REPEAT & 0b0000100 == 0b0000100:
            alarm_week.append("Tue")
        if WEEK_REPEAT & 0b0001000 == 0b0001000:
            alarm_week.append("Wed")
        if WEEK_REPEAT & 0b0010000 == 0b0010000:
            alarm_week.append("Thu")
        if WEEK_REPEAT & 0b0100000 == 0b0100000:
            alarm_week.append("Fri")
        if WEEK_REPEAT & 0b1000000 == 0b1000000:
            alarm_week.append("Sat")
        return "Repeat on " + ", ".join(alarm_week)

    def sync_time_pi_rtc(self):
        core.sync_time_pi2rtc()

    def update_battery_status(self, percent, votage, current, model, battery_is_charging):
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
        self.powerLabel.setText(_translate("MainWindow", "Power: " + str(round(power, 2)) + "W"))
        charging_str = " [charging]️" if battery_is_charging else ""
        self.modelLabel.setText(_translate("MainWindow", model + charging_str))
        print(percent, votage)

    def update_time(self, sys_time, rtc_time):
        _translate = QtCore.QCoreApplication.translate
        sys_time_string = time.asctime(time.localtime(sys_time))
        rtc_time_string = time.strftime("%w %b %d %H:%M:%S %Y", rtc_time)
        self.actionRTC_Time.setText(_translate("MainWindow", "RTC Time :    " + rtc_time_string))
        self.actionPi_Time.setText(_translate("MainWindow", "Pi Time : " + sys_time_string))


class SugarRepeatForm(Ui_RepeatForm):

    def __init__(self, RepeatForm):
        super().setupUi(RepeatForm)
        self.checkBoxOnce.clicked.connect(self.once_check)
        self.checkBoxEveryday.clicked.connect(self.everyday_check)
        self.checkBoxMonday.clicked.connect(self.mon_check)
        self.checkBoxTuesday.clicked.connect(self.tue_check)
        self.checkBoxWednesday.clicked.connect(self.wed_check)
        self.checkBoxTursday.clicked.connect(self.thu_check)
        self.checkBoxFriday.clicked.connect(self.fri_check)
        self.checkBoxSaturday.clicked.connect(self.sat_check)
        self.checkBoxSunday.clicked.connect(self.sun_check)

    def update_checkbox(self):
        global WEEK_REPEAT
        self.checkBoxEveryday.setChecked(WEEK_REPEAT == 0b1111111)
        self.checkBoxEveryday.setDisabled(WEEK_REPEAT == 0b1111111)
        self.checkBoxSunday.setChecked(WEEK_REPEAT & 0b0000001 == 0b00000001)
        self.checkBoxMonday.setChecked(WEEK_REPEAT & 0b0000010 == 0b00000010)
        self.checkBoxTuesday.setChecked(WEEK_REPEAT & 0b0000100 == 0b00000100)
        self.checkBoxWednesday.setChecked(WEEK_REPEAT & 0b0001000 == 0b00001000)
        self.checkBoxTursday.setChecked(WEEK_REPEAT & 0b0010000 == 0b00010000)
        self.checkBoxFriday.setChecked(WEEK_REPEAT & 0b0100000 == 0b00100000)
        self.checkBoxSaturday.setChecked(WEEK_REPEAT & 0b1000000 == 0b1000000)
        self.checkBoxOnce.setChecked(WEEK_REPEAT == 0b0000000)
        main_window.check_clock_set()

    def once_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = 0b0000000
        self.update_checkbox()

    def everyday_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = 0b1111111
        self.update_checkbox()

    def sun_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0000001
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1111110
        self.update_checkbox()

    def mon_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0000010
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1111101
        self.update_checkbox()

    def tue_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0000100
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1111011
        self.update_checkbox()

    def wed_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0001000
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1110111
        self.update_checkbox()

    def thu_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0010000
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1101111
        self.update_checkbox()

    def fri_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b0100000
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b1011111
        self.update_checkbox()

    def sat_check(self, value):
        global WEEK_REPEAT
        if value:
            WEEK_REPEAT = WEEK_REPEAT | 0b1000000
        else:
            WEEK_REPEAT = WEEK_REPEAT & 0b0111111
        self.update_checkbox()


def refresh_battery():
    global BATTERY_PERCENT
    BATTERY_PERCENT = core.get_battery_percent()
    battery_votage = core.get_battery_votage()
    battery_current = core.get_battery_current()
    battery_model = core.get_model()
    battery_is_charging = core.get_battery_charging_status()

    # update UI
    main_window.update_battery_status(BATTERY_PERCENT, battery_votage, battery_current, battery_model, battery_is_charging)
    action_percent.setText("Battery Level: " + str(int(BATTERY_PERCENT)) + "%")
    tray.setToolTip("Battery: " + str(int(BATTERY_PERCENT)) + "%")
    update_tray_icon(BATTERY_PERCENT, battery_model, battery_is_charging)

    # localtime = time.asctime(time.localtime(time.time()))
    # f = open('record.txt', 'a+')
    # new = str(localtime) + " : " + str(battery_votage) + " : " + str(int(BATTERY_PERCENT)) + "\n"
    # f.write(new)
    # f.flush()
    # f.close()

    threading.Timer(2.0, refresh_battery).start()


def refresh_time():
    global SYS_TIME
    global RTC_TIME
    SYS_TIME = time.time()
    RTC_TIME = core.get_rtc_time()

    #update UI
    main_window.update_time(SYS_TIME, RTC_TIME)

    threading.Timer(0.5, refresh_time).start()


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

    # initial core
    core = PiSugarCore()

    # create the main window
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("fusion")
    MainWindow = QMainWindow()
    main_window = SugarMainWindow(MainWindow)
    MainWindow.show()

    # create the tray icon
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

    # start refreshing ui
    refresh_battery()
    refresh_time()

    # create repeat form
    RepeatForm = QWidget()
    repeatForm = SugarRepeatForm(RepeatForm)

    sys.exit(app.exec_())
