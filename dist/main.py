import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5.QtCore import *
from mytablewidget import myTableWidget
import sqlite3
import database as dbMod
import re

#        액션
#        |--1.실행용 함수 => insertFunc
#        |--2.실행취소용 함수 => insertRedoFunc
#        
#        When called, action gathers and holds variables at its call (action-scoped var)
#        액션이 호출됐을때, 액션은 필요한 정보들을 저장한다. (액션 범위의 변수)
#        Methods declared inside an action are executed by using action-scoped var as parameters
#        액션에 속한 함수들은 액션 범위의 변수를 인자로 삼아 실행된다.


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("mainWindowUI.ui")[0]

db = dbMod.dbHandler()
#recent 데이터 regex
CONST_RECENT_REGEX = re.compile(r'\d{8}[ ]+\d{2}:+\d{2}:+d{2}')

actionStack = []
undoActionStack = []
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        # 데이터베이스에 레이블을 추가했을때 부여될 songId
        # Max(songId) + 1
        self.tableWidget.setDbHandler(db)
        self.curDisplayingTitle = ''
        self.curDisplayingArtist = ''
        self._displayTable()
        self.undoHotkey.setEnabled(False)
        self.redoHotkey.setEnabled(False)
        self.setWindowTitle("CMBsoftware")
        self.setGeometry(100, 100, 600, 500)
        self.titleInput.setFocus(True)

        self.tableWidget.lineEditReturnPressedSig.connect(self._lineEditReturnPressedSlot)
        self.saveDatabaseHotkey.triggered.connect(self._saveDatabaseHotkey)
        self.insertHotkey.triggered.connect(self._insertHotkey)
        self.modifyCellHotkey.triggered.connect(self._modifyCellHotkey)
        self.deleteHotkey.triggered.connect(self._deleteHotkey)
        self.updateHotkey.triggered.connect(self._updateHotkey)
        self.moveFocusHotkey.triggered.connect(self._moveFocusHotkey)
        self.undoHotkey.triggered.connect(self._undoHotkey)
        self.redoHotkey.triggered.connect(self._redoHotkey)

    def _displayTable(self)->None:
        """
        검색버튼을 누르지 않고 테이블 화면을 갱신하는 액션

        다른 액션들에 의해 사용되어진다.
        이 액션은 되돌려지지 않는다.
        """
        f_lastTitle = self.curDisplayingTitle
        f_lastArtist = self.curDisplayingArtist

        func_displayTable = self.tableWidget.displayData
        func_getData = db.getData

        func_displayTable(func_getData(f_lastTitle, f_lastArtist))
        return


    def getInquireAction(self, prevT:str, prevA:str, curT:str, curA:str, beforeText:str, console):
        """
        검색창에 입력한 정보를 조회 / 조회 실행취소 하는 함수를 반환하는
        inquireAction을 반환합니다.

        1.getinquireAction함수로 얻은 inquireAction을 저장
        (이때 반환받은 inquireAction은 getinquireAction에서 얻은 인자를 그대로 저장함)
        2.저장한 inquireAction에 isUndo 인자를 주어
        추가 / 추가 실행취소 하는 함수를 반환받아서 실행.
        (이때 반환받은 함수는 insertAction에 저장된 인자를 사용함)
        """
        def inquireAction(isUndo:bool=False):
            """
            검색버튼을 눌러서 정보를 조회했을때 추가되는 액션

            isUndo=False로 실행되면 현재 표시할 데이터를 표시해주는 inquireFunc를 반환한다
            isUndo=True로 실행되면 이전에 표시했던 데이터를 표시해주는 inquireUndoFunc를 반환한다
            """
            nonlocal prevT
            nonlocal prevA
            nonlocal curT
            nonlocal curA
            nonlocal console
            nonlocal beforeText

            func_displayTable = self.tableWidget.displayData
            func_getData = db.getData

            def inquireFunc():
                func_displayTable(func_getData(curT, curA))
                console.setText("다음을 조회합니다 : '{}', '{}'".format(curT, curA))

            def inquireUndoFunc():
                func_displayTable(func_getData(prevT, prevA))
                console.setText("'{}', '{}' 조회를 취소하고 다음을 조회합니다 : '{}', '{}'".format(curT, curA, prevT, prevA))

            if not isUndo:
                return inquireFunc
            else:
                return inquireUndoFunc
        
        return inquireAction


    def inquireDataBtnPressed(self) :
        print("inquireDataBtnPressed 함수 작동됨")
        self.prevDisplayingArtist = self.curDisplayingArtist
        self.prevDisplayingTitle = self.curDisplayingTitle
        self.curDisplayingArtist = self.artistInput.text()
        self.curDisplayingTitle = self.titleInput.text()

        print("prev : '{}', '{}'\ncur : '{}', '{}'".format(
            self.prevDisplayingTitle, self.prevDisplayingArtist,
            self.curDisplayingTitle, self.curDisplayingArtist))

        tempInquireAction = self.getInquireAction(
            prevT=self.prevDisplayingTitle, prevA=self.prevDisplayingArtist,
            curT=self.curDisplayingTitle, curA=self.curDisplayingArtist, 
            console=self.console, beforeText=self.undoHotkey.text())
        executingInquireFunc = tempInquireAction(isUndo=False)
        executingInquireFunc()

        actionStack.append(tempInquireAction)
        self.undoHotkey.setEnabled(True)
        undoActionStack.clear()
        self.redoHotkey.setEnabled(False)

        

    def getInsertAction(self, f_title:str, f_artist:str, console) :
        """
        입력된 데이터를 추가 / 추가 실행취소 하는 함수를 반환하는
        insertAction을 반환합니다.

        1.getinsertAction함수로 얻은 insertAction을 저장
        (이때 반환받은 insertAction은 getinsertAction에서 얻은 인자를 그대로 저장함)
        2.저장한 insertAction에 isUndo 인자를 주어
        추가 / 추가 실행취소 하는 함수를 반환받아서 실행.
        (이때 반환받은 함수는 insertAction에 저장된 인자를 사용함)
        """
        def insertAction(isUndo=False) :
            nonlocal f_artist
            nonlocal f_title
            nonlocal console

            func_insertDb = db.insertData
            func_insertedStageAppend = self.tableWidget.insertedStage.append
            func_displayTable = self._displayTable

            def insertFunc(): 
                func_insertedStageAppend({'Title':f_title, 'Artist':f_artist})
                try :
                    func_insertDb(f_title, f_artist)
                except sqlite3.IntegrityError as uniqueErr:
                    raise uniqueErr
                else:
                    func_displayTable()
                    console.setText("성공적으로 '{}', '{}' 를 추가했습니다!".format(f_title, f_artist))

            func_deleteDb = db.deleteData
            func_insertedStageRemove = self.tableWidget.insertedStage.remove

            def insertFuncUndo() :
                func_insertedStageRemove({'Title':f_title, 'Artist':f_artist})
                func_deleteDb(f_title, f_artist)
                func_displayTable()
                console.setText("실행 취소 : '{}', '{}' 추가".format(f_title, f_artist))

            if not isUndo :
                return insertFunc
            else :
                return insertFuncUndo

        return insertAction

    def insertDataBtnPressed(self):
        insertingTitle = self.titleInput.text()
        insertingArtist = self.artistInput.text()

        if len(insertingTitle) == 0 or len(insertingArtist) == 0 :
            self.console.setText("제목과 아티스트 모두 입력해야 추가할 수 있습니다!")
            return

        tempInsertAction = self.getInsertAction(
            f_title=insertingTitle,
            f_artist=insertingArtist,
            console=self.console)
        executingInsertFunc = tempInsertAction(isUndo=False)
        try :
            executingInsertFunc()
        except sqlite3.IntegrityError:
            self.console.setText("입력한 데이터가 이미 데이터베이스에 존재합니다!")
        else :
            actionStack.append(tempInsertAction)
            self.undoHotkey.setEnabled(True)
            undoActionStack.clear()
            self.redoHotkey.setEnabled(False)
            
        

    def getDeleteAction(self, f_artist:str, f_title:str, console):

        def deleteAction(isUndo=False):
            nonlocal f_title
            nonlocal f_artist
            nonlocal console

            func_deletedStageAppend = self.tableWidget.deletedStage.append
            func_deletedStageRemove = self.tableWidget.deletedStage.remove
            func_displayTable = self._displayTable

            def deleteFunc():
                func_deletedStageAppend({'Title':f_title, 'Artist':f_artist})
                func_displayTable()
                console.setText("성공적으로 '{}', '{}' 를 삭제했습니다!".format(f_title, f_artist))

            def deleteUndoFunc():
                func_deletedStageRemove({'Title':f_title, 'Artist':f_artist})
                func_displayTable()
                console.setText("다음 삭제를 취소합니다 : '{}', '{}'".format(f_title, f_artist))

            if not isUndo:
                return deleteFunc
            else :
                return deleteUndoFunc

        return deleteAction

    def deleteDataBtnPressed(self):
        
        deletingRow = self.tableWidget.curSelectedRow
        if deletingRow < 0:
            self.console.setText("삭제할 데이터를 선택한 후 삭제버튼을 눌러주세요!")
            print("삭제할 데이터를 선택한 후 삭제버튼을 눌러주세요!")
            return
        else:
            deletingTitle = self.tableWidget.cellWidget(deletingRow, 1).getLabelText()
            deletingArtist = self.tableWidget.cellWidget(deletingRow, 2).getLabelText()
            tempDeleteAction = self.getDeleteAction(
                f_artist=deletingArtist,
                f_title=deletingTitle, 
                console = self.console)
            executingDeleteAction = tempDeleteAction(isUndo = False)
            executingDeleteAction()

            actionStack.append(tempDeleteAction)
            self.undoHotkey.setEnabled(True)
            undoActionStack.clear()
            self.redoHotkey.setEnabled(False)

            


    def getUpdateAction(self, f_songId:int, f_title:str, f_artist:str, f_oldCount:int, f_newCount:int, f_oldRecent:str, f_newRecent:str, console):

            def updateAction(isUndo = False):
                nonlocal f_songId
                nonlocal f_title
                nonlocal f_artist
                nonlocal f_oldCount
                nonlocal f_newCount
                nonlocal f_oldRecent
                nonlocal f_newRecent
                nonlocal console

                func_updatedStageAppend = self.tableWidget.updatedStage.append
                func_updatedStageRemove = self.tableWidget.updatedStage.remove
                func_updateDb = db.updateData
                func_displayTable = self._displayTable

                def updateFunc():
                    func_updatedStageAppend({
                        'songId':f_songId,
                        'oldCount':f_oldCount,
                        'oldRecent':f_oldRecent,
                        'newCount':f_newCount,
                        'newRecent':f_newRecent
                    })
                    func_updateDb(f_songId, f_newCount, f_newRecent)
                    func_displayTable()
                    console.setText("성공적으로 {}, {}을 업데이트했습니다!".format(f_title, f_artist))
                
                def updateUndoFunc():
                    func_updatedStageRemove({
                        'songId':f_songId,
                        'oldCount':f_oldCount,
                        'oldRecent':f_oldRecent,
                        'newCount':f_newCount,
                        'newRecent':f_newRecent
                    })
                    func_updateDb(f_songId, f_oldCount, f_oldRecent)
                    func_displayTable()
                    console.setText("실행취소 : {}, {} 업데이트".format(f_title, f_artist))
                
                if not isUndo :
                    return updateFunc
                else :
                    return updateUndoFunc

            return updateAction

    def updateDataBtnPressed(self):
        updatingRow = self.tableWidget.curSelectedRow
        if updatingRow < 0 :
            self.console.setText("업데이트할 데이터를 선택한 후 삭제버튼을 눌러주세요!")
            print("업데이트할 데이터를 선택한 후 삭제버튼을 눌러주세요!")
            return
        else:
            updatingSongId = int(self.tableWidget.cellWidget(updatingRow, 0).getLabelText())
            title, artist, oldCount, oldRecent = db.getInfoById(updatingSongId, True, True, True, True)
            newCount = oldCount+1
            newRecent = dbMod.returnTime('%m.%d(%a) %H:%M')

            tempUpdateAction = self.getUpdateAction(
                f_songId=updatingSongId,
                f_title = title,
                f_artist = artist,
                f_oldCount = oldCount,
                f_newCount = newCount,
                f_oldRecent=oldRecent,
                f_newRecent = newRecent,
                console = self.console)

            tempUpdateFunc = tempUpdateAction(isUndo=False)
            tempUpdateFunc()

            actionStack.append(tempUpdateAction)
            self.undoHotkey.setEnabled(True)
            undoActionStack.clear()
            self.redoHotkey.setEnabled(False)

            

    def getModifyAction(self, songId:int, f_title:str, f_artist:str, f_colName:str, f_oldVal, f_newVal, console):
        
        def modifyAction(isUndo = False):
            nonlocal songId, f_title, f_artist, f_colName, f_oldVal, f_newVal, console

            func_modifiedStageAppend = self.tableWidget.modifiedStage.append
            func_modifiedStageRemove = self.tableWidget.modifiedStage.remove
            func_modifyDb = db.modifyData
            func_displayTable = self._displayTable

            def modifyFunc():
                func_modifiedStageAppend({
                    'songId':songId,
                    'colName':f_colName,
                    'oldVal':f_oldVal,
                    'newVal':f_newVal
                })
                try:
                    func_modifyDb(songId, f_colName, f_newVal)
                except sqlite3.IntegrityError as uniqueErr:
                    raise uniqueErr
                else:
                    func_displayTable()
                    console.setText("성공적으로 {}, {}의 {}데이터를 {}에서 {}으로 수정했습니다!".format(f_title, f_artist, f_colName, f_oldVal, f_newVal))

            def modifyUndoFunc():
                func_modifiedStageRemove({
                    'songId':songId,
                    'colName':f_colName,
                    'oldVal':f_oldVal,
                    'newVal':f_newVal
                })
                func_modifyDb(songId, f_colName, f_oldVal)
                func_displayTable()

            if not isUndo:
                return modifyFunc
            else :
                return modifyUndoFunc

        return modifyAction

    def _lineEditReturnPressedSlot(self, row:int, col:int, songId:int, colName:str, oldVal:str, newVal:str) :
        if colName == 'Count':
            try :
                oldVal = int(oldVal)
                newVal = int(newVal)
            except ValueError :
                self.console.setText("Count에는 숫자만 입력할 수 있습니다!")
                return

        if oldVal == newVal:
            self.console.setText("수정하려는 내용이 기존의 내용과 일치합니다!")
            return

        title, artist = db.getInfoById(songId, True, True, False, False)
        tempModifyAction = self.getModifyAction(
            songId=songId,
            f_title = title,
            f_artist = artist,
            f_colName = colName,
            f_oldVal = oldVal,
            f_newVal = newVal,
            console = self.console)
        tempModifyFunc = tempModifyAction(isUndo=False)

        try:
            tempModifyFunc()
        except sqlite3.IntegrityError:
            self.console.setText("데이터를 수정하게 되면 기존의 데이터와 중복됩니다!")
        else:
            actionStack.append(tempModifyAction)
            undoActionStack.clear()

            self.undoHotkey.setEnabled(True)

    def _modifyCellHotkey(self):
        row = self.tableWidget.curSelectedRow
        col = self.tableWidget.curSelectedCol
        self.tableWidget.curDblClickedCellRow = row
        self.tableWidget.curDblClickedCellCol = col
        widget = self.tableWidget.cellWidget(row, col)
        if col != 0:
            if not widget.isLineEditDisplayed:
                widget.showLineEdit()
            else :
                widget.hideLineEdit()
                self.tableWidget.setFocus(True)

    def _moveFocusHotkey(self):
        self.titleInput.setFocus(True)      

    def _insertHotkey(self):
        self.insertDataBtnPressed()

    def _deleteHotkey(self):
        self.deleteDataBtnPressed()

    def _updateHotkey(self):
        self.updateDataBtnPressed()

    def _undoHotkey(self):
        print("_undoHotkey 실행됨\n")
        print(actionStack)
        undoingAction = actionStack.pop()
        undoingFunc = undoingAction(isUndo=True)
        print("실행취소하는 행동 : "+str(undoingFunc))
        undoingFunc()

        undoActionStack.append(undoingAction)
        self.redoHotkey.setEnabled(True)
        #실행취소할 행동이 없다면 행동을 비활성화 시킴
        if len(actionStack) == 0:
            self.undoHotkey.setEnabled(False)


    def _redoHotkey(self):
        print("_redoHotkey 실행됨\n")
        print(undoActionStack)
        redoAction = undoActionStack.pop()
        redoFunc = redoAction(isUndo=False)
        print("다시 실행하는 행동 : "+str(redoFunc))
        redoFunc()

        actionStack.append(redoAction)
        self.undoHotkey.setEnabled(True)
        #다시실행할 행동이 없다면 행동을 비활성화 시킴
        if len(undoActionStack) == 0:
            self.redoHotkey.setEnabled(False)

    def _saveDatabaseHotkey(self):
        # TODO : 삭제될 항목들 팝업을 띄워 알리기
        print("삭제될 데이터들 :"+str(self.tableWidget.deletedStage))
        for song in self.tableWidget.deletedStage:
            db.deleteData(song['Title'], song['Artist'], True)
        print("변경된 내용이 성공적으로 저장되었습니다!")
        self.console.setText("변경된 내용이 성공적으로 저장되었습니다!")
        self.tableWidget.insertedStage.clear()
        self.tableWidget.updatedStage.clear()
        self.tableWidget.modifiedStage.clear()
        self.tableWidget.deletedStage.clear()
        actionStack.clear()
        undoActionStack.clear()
        db.con.commit()
        self._displayTable()

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
