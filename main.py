# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(792, 449)
        MainWindow.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.ADD_BUTTON = QtWidgets.QPushButton(self.centralwidget)
        self.ADD_BUTTON.setObjectName("ADD_BUTTON")
        self.gridLayout.addWidget(self.ADD_BUTTON, 0, 0, 1, 1)
        self.ADD_BUTTON_2 = QtWidgets.QPushButton(self.centralwidget)
        self.ADD_BUTTON_2.setObjectName("ADD_BUTTON_2")
        self.gridLayout.addWidget(self.ADD_BUTTON_2, 0, 2, 1, 1)
        self.DELETE_BUTTON_2 = QtWidgets.QPushButton(self.centralwidget)
        self.DELETE_BUTTON_2.setObjectName("DELETE_BUTTON_2")
        self.gridLayout.addWidget(self.DELETE_BUTTON_2, 0, 3, 1, 1)
        self.DELETE_BUTTON = QtWidgets.QPushButton(self.centralwidget)
        self.DELETE_BUTTON.setObjectName("DELETE_BUTTON")
        self.gridLayout.addWidget(self.DELETE_BUTTON, 0, 1, 1, 1)
        self.test_list = QtWidgets.QListWidget(self.centralwidget)
        self.test_list.setObjectName("test_list")
        self.gridLayout.addWidget(self.test_list, 2, 0, 1, 2)
        self.test_list_2 = QtWidgets.QListWidget(self.centralwidget)
        self.test_list_2.setObjectName("test_list_2")
        self.gridLayout.addWidget(self.test_list_2, 2, 2, 1, 2)
        self.LANG_COMBOBOX = QtWidgets.QComboBox(self.centralwidget)
        self.LANG_COMBOBOX.setObjectName("LANG_COMBOBOX")
        self.gridLayout.addWidget(self.LANG_COMBOBOX, 3, 3, 1, 1)
        self.TR_LABEL = QtWidgets.QLabel(self.centralwidget)
        self.TR_LABEL.setObjectName("TR_LABEL")
        self.gridLayout.addWidget(self.TR_LABEL, 3, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 792, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ADD_BUTTON.setText(_translate("MainWindow", "ADD"))
        self.ADD_BUTTON_2.setText(_translate("MainWindow", "ADD"))
        self.DELETE_BUTTON_2.setText(_translate("MainWindow", "DELETE"))
        self.DELETE_BUTTON.setText(_translate("MainWindow", "DELETE"))
        self.TR_LABEL.setText(_translate("MainWindow", "TextLabel"))
        self.label.setText(_translate("MainWindow", "1"))
        self.label_2.setText(_translate("MainWindow", "2"))
