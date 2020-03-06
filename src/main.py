import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtQuickWidgets import *
from mytablewidget import myTableWidget
from myresulttab import myResultTab
from myqueuetab import myQueueTab
from model import ResultModel
import pprint
import sqlite3
import requests
import database as dbMod
import re
import youtube
#        액션
#        |--1.실행용 함수 => insertFunc
#        |--2.실행취소용 함수 => insertRedoFunc
#        
#        When called, action gathers and holds variables at its call (action-scoped var)
#        액션이 호출됐을때, 액션은 필요한 정보들을 저장한다. (액션 범위의 변수)
#        Methods declared inside an action are executed by using action-scoped var as parameters
#        액션에 속한 함수들은 액션 범위의 변수를 인자로 삼아 실행된다.

stack = QUndoStack()
form_class = uic.loadUiType(("mainWindowUI.ui"))[0]
db = dbMod.dbHandler()
CONST_RECENT_REGEX = re.compile(r'\d{8}[ ]+\d{2}:+\d{2}:+d{2}')

class Inquire(QUndoCommand):

    def __init__(self, maxRes:int, prevTitle=None, prevArtist=None, curTitle= None, curArtist= None):
        super().__init__()
        self.prevTitle = prevTitle
        self.prevArtist = prevArtist
        self.curTitle =  curTitle
        self.curArtist = curArtist
        self.maxRes = maxRes
        self.setText("Inquire")

    def redo(self):
        pageToken, ytData = youtube.getDataFromYoutube(self.maxRes, self.curTitle, self.curArtist)
        result = db.processData(ytData)

        return result

    def undo(self):
        # TODO : 이전 검색 정보를 요청해서 return하는 함수 만들기(정보는 초기 정보만)
        pageToken, ytData = youtube.getDataFromYoutube(self.maxRes, self.prevTitle, self.prevArtist)
        result = db.processData(ytData)

        return result

class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.curDisplayingTitle = ''
        self.curDisplayingArtist = ''
        self.undoHotkey.setEnabled(False)
        self.redoHotkey.setEnabled(False)
        self.setWindowTitle("CMBsoftware")
        self.setGeometry(100, 100, 600, 500)
        self.titleInput.setFocus(True)
        self.maxResult = 20

        #TabWidget과 탭에 보여질 QuickWidget들 초기화
        self.tabWidget.clear()
        self.resultQuickWidget = QQuickWidget()
        self.resultQuickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.resultContext = self.resultQuickWidget.rootContext()
        self.resModel = ResultModel([
            {
            "mod_thumbnailUrl" : "https://i.ytimg.com/vi/tXV7dfvSefo/hqdefault.jpg",
            "mod_videoId":"tXV7dfvSefo",
            "mod_videoTitle" : "버스커 버스커 (Busker Busker) - 벚꽃 엔딩",
            "mod_channelTitle" : "Stone Music Entertainment",
            "mod_duration":"4:55",
            "mod_count" : 1,
            "mod_recent": "2020-02-24(월) 기훈-점심",
            "mod_stage" : "Updated"
        },
        {
            "mod_thumbnailUrl" : "https://i.ytimg.com/vi/VgwcPiCjQ-0/hqdefault.jpg",
            "mod_videoId" : "VgwcPiCjQ-0",
            "mod_videoTitle" : "Oh Wonder - Lose It",
            "mod_channelTitle" : "OhWonderMusicVEVO",
            "mod_duration" : "3:41",
            "mod_count" : 0,
            "mod_recent": "없음",
            "mod_stage" : "Normal"
        }])
        self.updateResultContext()

        self.queueQuickWidget = QQuickWidget()
        self.queueQuickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.queueContext = self.queueQuickWidget.rootContext()
        self.tabWidget.insertTab(0, self.resultQuickWidget, "Result")
        self.tabWidget.insertTab(1, self.queueQuickWidget, "Queue")

        # 단축키 슬롯 매칭
        #self.resultContext.onRightClick.connect(self._onRightClick)
        self.saveDatabaseHotkey.triggered.connect(self._saveDatabaseHotkey)
        self.undoHotkey.triggered.connect(self._undoHotkey)
        self.redoHotkey.triggered.connect(self._redoHotkey)
        #self.addToQueueAction.triggered.connect(self._addToQueueAction)


    @pyqtSlot()
    def updateResultContext(self): 
        self.resultContext.setContextProperty("resultModel", self.resModel)
        self.resultQuickWidget.setSource(QUrl.fromLocalFile("resultTabQml.qml"))            

    def getDataFromApiBtnPressed(self):
        targetTitle = self.titleInput.text()
        targetArtist = self.artistInput.text()
        inquireAction = Inquire()
        stack.push(inquireAction)

    def _onRightClick(self):
        resRightClick = Qmenu()
        resRightClick.addAction()

    def _undoHotkey(self):
        print("_undoHotkey 실행됨\n")
        stack.undo()
        pass

    def _redoHotkey(self):
        print("_redoHotkey 실행됨\n")
        stack.redo()
        pass

    def _saveDatabaseHotkey(self):
        # TODO : 삭제될 항목들 팝업을 띄워 알리기
        db.con.commit()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
