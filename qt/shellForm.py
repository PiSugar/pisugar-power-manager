# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shell_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ShellForm(object):
    def setupUi(self, ShellForm):
        ShellForm.setObjectName("ShellForm")
        ShellForm.resize(400, 194)
        ShellForm.setMinimumSize(QtCore.QSize(400, 194))
        ShellForm.setMaximumSize(QtCore.QSize(400, 194))
        self.plainTextEdit = QtWidgets.QPlainTextEdit(ShellForm)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 50, 361, 81))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.inputLabel = QtWidgets.QLabel(ShellForm)
        self.inputLabel.setGeometry(QtCore.QRect(20, 20, 361, 22))
        self.inputLabel.setObjectName("inputLabel")
        self.saveButton = QtWidgets.QPushButton(ShellForm)
        self.saveButton.setGeometry(QtCore.QRect(150, 140, 99, 30))
        self.saveButton.setObjectName("saveButton")

        self.retranslateUi(ShellForm)
        QtCore.QMetaObject.connectSlotsByName(ShellForm)

    def retranslateUi(self, ShellForm):
        _translate = QtCore.QCoreApplication.translate
        ShellForm.setWindowTitle(_translate("ShellForm", "Edit Custom Shell"))
        self.plainTextEdit.setPlaceholderText(_translate("ShellForm", "Type your shell script here ..."))
        self.inputLabel.setText(_translate("ShellForm", "Custom Shell on Single Tap :"))
        self.saveButton.setText(_translate("ShellForm", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ShellForm = QtWidgets.QWidget()
    ui = Ui_ShellForm()
    ui.setupUi(ShellForm)
    ShellForm.show()
    sys.exit(app.exec_())

