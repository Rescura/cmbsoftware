# This Python file uses the following encoding: utf-8
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuickWidgets import QQuickWidget
from model import ResultModel

class myResultTab(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.resultQuickWidget = QQuickWidget()
        self.resultQuickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.layout.addWidget(self.resultQuickWidget)
        self.setLayout(self.layout)
    
    def setModel(self, f_model:ResultModel):
        self.model = f_model
        self.resultQuickWidget.rootContext().setContextProperty("resultModel",self.model)

    def loadQmlFile(self):
        self.resultQuickWidget.setSource(QUrl.fromLocalFile("resultTabQml.qml"))