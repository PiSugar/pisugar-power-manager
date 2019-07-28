# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'repeat_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RepeatForm(object):
    def setupUi(self, RepeatForm):
        RepeatForm.setObjectName("RepeatForm")
        RepeatForm.resize(214, 351)
        RepeatForm.setMinimumSize(QtCore.QSize(214, 351))
        RepeatForm.setMaximumSize(QtCore.QSize(214, 351))
        self.checkBoxOnce = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxOnce.setGeometry(QtCore.QRect(40, 40, 161, 27))
        self.checkBoxOnce.setObjectName("checkBoxOnce")
        self.checkBoxEveryday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxEveryday.setGeometry(QtCore.QRect(40, 70, 161, 27))
        self.checkBoxEveryday.setObjectName("checkBoxEveryday")
        self.checkBoxMonday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxMonday.setGeometry(QtCore.QRect(40, 100, 161, 27))
        self.checkBoxMonday.setObjectName("checkBoxMonday")
        self.checkBoxTuesday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxTuesday.setGeometry(QtCore.QRect(40, 130, 161, 30))
        self.checkBoxTuesday.setObjectName("checkBoxTuesday")
        self.checkBoxWednesday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxWednesday.setGeometry(QtCore.QRect(40, 160, 161, 30))
        self.checkBoxWednesday.setObjectName("checkBoxWednesday")
        self.checkBoxTursday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxTursday.setGeometry(QtCore.QRect(40, 190, 161, 30))
        self.checkBoxTursday.setObjectName("checkBoxTursday")
        self.checkBoxFriday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxFriday.setGeometry(QtCore.QRect(40, 220, 161, 30))
        self.checkBoxFriday.setObjectName("checkBoxFriday")
        self.checkBoxSaturday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxSaturday.setGeometry(QtCore.QRect(40, 250, 161, 30))
        self.checkBoxSaturday.setObjectName("checkBoxSaturday")
        self.checkBoxSunday = QtWidgets.QCheckBox(RepeatForm)
        self.checkBoxSunday.setGeometry(QtCore.QRect(40, 280, 161, 30))
        self.checkBoxSunday.setObjectName("checkBoxSunday")

        self.retranslateUi(RepeatForm)
        QtCore.QMetaObject.connectSlotsByName(RepeatForm)

    def retranslateUi(self, RepeatForm):
        _translate = QtCore.QCoreApplication.translate
        RepeatForm.setWindowTitle(_translate("RepeatForm", "Repeat"))
        self.checkBoxOnce.setText(_translate("RepeatForm", "Once"))
        self.checkBoxEveryday.setText(_translate("RepeatForm", "Everyday"))
        self.checkBoxMonday.setText(_translate("RepeatForm", "Monday"))
        self.checkBoxTuesday.setText(_translate("RepeatForm", "Tuesday"))
        self.checkBoxWednesday.setText(_translate("RepeatForm", "Wednesday"))
        self.checkBoxTursday.setText(_translate("RepeatForm", "Tursday"))
        self.checkBoxFriday.setText(_translate("RepeatForm", "Friday"))
        self.checkBoxSaturday.setText(_translate("RepeatForm", "Saturday"))
        self.checkBoxSunday.setText(_translate("RepeatForm", "Sunday"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    RepeatForm = QtWidgets.QWidget()
    ui = Ui_RepeatForm()
    ui.setupUi(RepeatForm)
    RepeatForm.show()
    sys.exit(app.exec_())

