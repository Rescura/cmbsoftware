# This Python file uses the following encoding: utf-8
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuickWidgets import QQuickWidget

class myQueueTab(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        queueQuickWidget = QQuickWidget(QUrl.fromLocalFile("queueTabQml.qml"))
        queueQuickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        layout.addWidget(queueQuickWidget)
        self.setLayout(layout)
