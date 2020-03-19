from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *

class MyResultWidget(QQuickView):
  
  def __init__(self, parent = None):
    super().__init__()
    self.setParent(parent)
    self.setSource(QUrl.fromLocalFile("resultTabQml.qml"))

  def updateQml(self, data):
    pass
