# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ServerSettingForm(object):
    def setupUi(self, ServerSettingForm):
        ServerSettingForm.setObjectName("ServerSettingForm")
        ServerSettingForm.resize(387, 196)
        ServerSettingForm.setMinimumSize(QtCore.QSize(387, 196))
        ServerSettingForm.setMaximumSize(QtCore.QSize(387, 196))
        self.label = QtWidgets.QLabel(ServerSettingForm)
        self.label.setGeometry(QtCore.QRect(40, 35, 91, 22))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(ServerSettingForm)
        self.lineEdit.setGeometry(QtCore.QRect(140, 30, 81, 32))
        self.lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(ServerSettingForm)
        self.label_2.setGeometry(QtCore.QRect(40, 85, 91, 22))
        self.label_2.setObjectName("label_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(ServerSettingForm)
        self.lineEdit_2.setGeometry(QtCore.QRect(140, 80, 201, 32))
        self.lineEdit_2.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.saveButton = QtWidgets.QPushButton(ServerSettingForm)
        self.saveButton.setGeometry(QtCore.QRect(140, 140, 99, 30))
        self.saveButton.setObjectName("saveButton")

        self.retranslateUi(ServerSettingForm)
        QtCore.QMetaObject.connectSlotsByName(ServerSettingForm)

    def retranslateUi(self, ServerSettingForm):
        _translate = QtCore.QCoreApplication.translate
        ServerSettingForm.setWindowTitle(_translate("ServerSettingForm", "Server Setting"))
        self.label.setText(_translate("ServerSettingForm", "Server Port"))
        self.lineEdit.setText(_translate("ServerSettingForm", "3001"))
        self.label_2.setText(_translate("ServerSettingForm", "Password"))
        self.lineEdit_2.setText(_translate("ServerSettingForm", "pisugar"))
        self.saveButton.setText(_translate("ServerSettingForm", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ServerSettingForm = QtWidgets.QWidget()
    ui = Ui_ServerSettingForm()
    ui.setupUi(ServerSettingForm)
    ServerSettingForm.show()
    sys.exit(app.exec_())

