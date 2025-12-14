# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'penslot.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(152, 52)
        Form.setMinimumSize(QSize(152, 52))
        Form.setMaximumSize(QSize(152, 52))
        self.PenButton = QPushButton(Form)
        self.PenButton.setObjectName(u"PenButton")
        self.PenButton.setGeometry(QRect(0, 0, 50, 51))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setUnderline(False)
        font.setStrikeOut(True)
        self.PenButton.setFont(font)
        self.EraserButton = QPushButton(Form)
        self.EraserButton.setObjectName(u"EraserButton")
        self.EraserButton.setGeometry(QRect(50, 0, 51, 51))
        font1 = QFont()
        font1.setPointSize(15)
        font1.setBold(True)
        font1.setStrikeOut(True)
        self.EraserButton.setFont(font1)
        self.ExitButton = QPushButton(Form)
        self.ExitButton.setObjectName(u"ExitButton")
        self.ExitButton.setGeometry(QRect(100, 0, 51, 51))
        font2 = QFont()
        font2.setPointSize(15)
        font2.setBold(True)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        self.ExitButton.setFont(font2)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.PenButton.setText(QCoreApplication.translate("Form", u"\u7b14", None))
        self.EraserButton.setText(QCoreApplication.translate("Form", u"\u6a61\u76ae", None))
        self.ExitButton.setText(QCoreApplication.translate("Form", u"\u9000\u51fa\n"
" PPT", None))
    # retranslateUi

