
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from database import dbHandler

class myTableWidget(QTableWidget) :

    lineEditReturnPressedSig = pyqtSignal(int,int,int,str,str,str)
    normalCellCss = "background-color: #ffffff;"
    insertedCellCss = "background-color: #66ff91;"
    updatedCellCss = "background-color: #66e8ff;"
    modifiedCellCss = "background-color: #ffff66;"
    deletedCellCss = "background-color: #ff6666;"
    selectedCellCss = "border : 2px solid #ffdd03;"
    def setDbHandler(self, f_db:dbHandler):
        self.db = f_db
        #print("setDbHandler로 지정한 myTableWindow의 db:"+str(type(f_db)))

    def getColName(self, idx)->str:
        return {
            0 : 'songId',
            1 : 'Title',
            2 : 'Artist',
            3 : 'Count',
            4 : 'Recent'
        }.get(idx, 'ERROR')

    def __init__(self, f_db) :
        self.db = f_db
        print("__init__으로 지정한 myTableWindow의 db :"+str(type(f_db)))
        self.prevDblClickedCellRow = -1
        self.prevDblClickedCellCol = -1
        self.curDblClickedCellRow = -1
        self.curDblClickedCellCol = -1
        self.prevSelectedRow = -1
        self.prevSelectedCol = -1
        self.curSelectedRow = -1
        self.curSelectedCol = -1
        # {Title':제목, 'Artist':아티스트}
        self.insertedStage = []
        
        # {'songId':id, 'newCount':기존 count+1, 'oldRecent':예전시각, 'newRecent':새로운시각}
        self.updatedStage =[]
        
        # {'Title':제목, 'Artist':아티스트 }
        self.deletedStage = []
        
        # {'songid': id, 'colName':컬럼이름, 'oldVal':예전값 'newVal':새값}
        self.modifiedStage = []

        super().__init__()
        self.setRowCount(5)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(("songId", "Title", "Artist", "Count", "Recent"))
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Interactive)
        horizontalHeader.setStretchLastSection(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.show()
        
        self.cellDoubleClicked.connect(self._cellDoubleClicked)
        self.currentCellChanged.connect(self._currentCellChanged)

    def _cellDoubleClicked(self, clickedRow:int, clickedCol:int):
        print("_cellDoubleClicked 함수 작동됨")
        if clickedCol is 0:
            return
        self.curDblClickedCellRow = clickedRow
        self.curDblClickedCellCol = clickedCol
        tempMyCellWidget = self.cellWidget(clickedRow, clickedCol)
        #print("더블클릭된 셀의 cellWidget() : "+str(tempMyCellWidget))
        isDeleted = tempMyCellWidget.property('deletedCell')
        print(type(isDeleted), isDeleted)
        if isDeleted :
            return
        #print("이전 : ({}, {})".format(self.prevDblClickedCellRow, self.prevDblClickedCellCol))
        #print("현재 : ({}, {})".format(self.curDblClickedCellRow, self.curDblClickedCellCol))
        #print("tempMyCellWidget : {}".format(tempMyCellWidget))
        #print("self.cellWidget() : {}".format((self.cellWidget(self.curDblClickedCellRow, self.curDblClickedCellCol))))
        
        if tempMyCellWidget.isLineEditDisplayed :
            tempMyCellWidget.hideLineEdit()
        else :
            tempMyCellWidget.showLineEdit()
        
        if self.prevDblClickedCellRow >=0 and self.prevDblClickedCellCol>0 :
            if clickedRow is not self.prevDblClickedCellRow or clickedCol is not self.prevDblClickedCellCol :
                self.cellWidget(self.prevDblClickedCellRow, self.prevDblClickedCellCol).hideLineEdit()

        self.prevDblClickedCellRow = clickedRow
        self.prevDblClickedCellCol = clickedCol

    def _currentCellChanged(self, curSelectedRow:int, curSelectedCol:int, prevSelectedRow:int, prevSelectedCol:int)->None:
        self.prevSelectedRow = prevSelectedRow
        self.prevSelectedCol = prevSelectedCol
        self.curSelectedRow = curSelectedRow
        self.curSelectedCol = curSelectedCol
        print("({}, {}), ({}, {})".format(self.prevSelectedRow, self.prevSelectedCol, self.curSelectedRow, self.curSelectedCol))
        if self.prevSelectedRow >=0 and self.prevSelectedCol>=0 :
            try :
                tempWidget = self.cellWidget(self.prevSelectedRow, self.prevSelectedCol)
                styleSheet = tempWidget.styleSheet()
                styleSheet = styleSheet.replace(self.selectedCellCss, "")
                tempWidget.setStyleSheet(styleSheet)
                tempWidget.hideLineEdit();
            except AttributeError:
                pass
            #prevSelectedCell = self.cellWidget(self.prevSelectedRow, self.prevSelectedCol)
            #prevSelectedCell.setStyleSheet(prevSelectedCell.styleSheet().replace(self.selectedCellCss, ''))
            #self.setCellWidget(self.prevSelectedRow, self.prevSelectedCol, prevSelectedCell)
            #print("이전에 선택된 셀 ({}, {}) {}".format(self.prevSelectedRow, self.prevSelectedCol, prevSelectedCell))
        if self.curSelectedRow >=0 and self.curSelectedCol >=0:
            try :
                tempWidget = self.cellWidget(self.curSelectedRow, self.curSelectedCol)
                styleSheet = tempWidget.styleSheet()
                tempWidget.setStyleSheet(styleSheet+self.selectedCellCss)
            except AttributeError:
                pass
            #curSelectedCell = self.cellWidget(self.curSelectedRow, self.curSelectedCol)
            #curSelectedCell.setStyleSheet(curSelectedCell.styleSheet()+'\n'+self.selectedCellCss)
            #self.setCellWidget(self.curSelectedRow, self.curSelectedCol, curSelectedCell)
            #print("현재 선택된 셀 ({}, {}) {}".format(self.curSelectedRow, self.curSelectedCol, curSelectedCell))

    @pyqtSlot()
    def lineEditEnterPressed(self):
        #songId, targetCol, oldVal,newVal
        print("lineEditEnterPressed 함수 작동됨")
        changingMyCellWidget = self.cellWidget(self.curDblClickedCellRow, self.curDblClickedCellCol)
        changingSongId = int(self.cellWidget(self.curDblClickedCellRow, 0).getLabelText())
        changingColName = self.getColName(self.curDblClickedCellCol)
        oldVal = changingMyCellWidget.getLabelText()
        newVal = changingMyCellWidget.getLineEditText()

        self.lineEditReturnPressedSig.emit(self.curDblClickedCellRow, self.curDblClickedCellCol, changingSongId, changingColName, oldVal, newVal)


    def displayData(self, data:list)->None:
        self.setRowCount(len(data))
        self.setColumnCount(5)
        print("data")
        print(data)
        print("insertedStage")
        print(self.insertedStage)
        print("updatedStage")
        print(self.updatedStage)
        print("deletedStage")
        print(self.deletedStage)
        print("modifiedStage")
        print(self.modifiedStage)
        for rowidx, row in enumerate(data):
            tempSongTitle = row[1]
            tempSongArtist = row[2]
            rowStyleText = self.normalCellCss
            rowStage = 'normal'
            # 추가했지만 저장하지 않은 셀이라면
            for song in self.insertedStage :
                if song['Title'] == tempSongTitle and song['Artist']==tempSongArtist:
                    rowStyleText = self.insertedCellCss
                    rowStage = 'inserted'
            #업데이트했지만 저장하지 않은 셀이라면
            for song in self.updatedStage :
                if song['songId'] == row[0]:
                    rowStyleText = self.updatedCellCss
                    rowStage = 'updated'
            # 삭제했지만 저장하지 않은 셀이라면
            for song in self.deletedStage:
                if song['Title'] == tempSongTitle and song['Artist']==tempSongArtist:
                    rowStyleText = self.deletedCellCss
                    rowStage = 'deleted'
            #print("row{} 의 styleText={}, rowStage={}".format(rowidx, rowStyleText, rowStage))
            
            for colidx, col in enumerate(row):
                styleText = rowStyleText
                stage = rowStage
                # 수정된 셀이라면
                for cell in self.modifiedStage:
                    if colidx == 0:
                        pass    #수정된 값과 songId가 같으면 songId칸까지 바꾸기 때문에 songId는 제외
                    elif cell['colName'] == self.getColName(colidx) and cell['songId'] == row[0]:
                        if stage != 'deleted' :
                            styleText = self.modifiedCellCss
                if rowidx == self.curSelectedRow and colidx == self.curSelectedCol:
                    styleText = styleText+self.selectedCellCss
                tempMyCellWidget = self.cellWidget(rowidx, colidx)
                if tempMyCellWidget is None:
                    tempMyCellWidget = myCellWidget(self)
                    self.setCellWidget(rowidx, colidx, tempMyCellWidget)

                tempMyCellWidget.setLabelText(str(col))
                tempMyCellWidget.setStyleSheet(styleText)
#tableWidget에 사용될 위젯 클래스
#더블클릭시 QLineEdit을 표시한다
#QLineEdit에서 값을 변화시키고 엔터를 누르면 변화를 시킨다.
#다시 더블클릭하면 QLineEdit을 숨긴다.
#혹은 다른 셀을 선택했을때에도 QLineEdit을 숨긴다.
class myCellWidget(QWidget):

    def getLabelText(self)->str:
        return self.label.text()

    def getLineEditText(self)->str:
        return self.lineEdit.text()

    def setLabelText(self, f_text:str)->None:
        self.label.setText(f_text)

    def __init__(self, parent:myTableWidget, text:str=None):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.show()
        self.lineEdit = QLineEdit()
        self.lineEdit.hide()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineEdit)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.isLineEditDisplayed = False
        self.setLayout(self.layout)

        self.lineEdit.returnPressed.connect(parent.lineEditEnterPressed)

    def showLineEdit(self):
        if not self.property('deletedCell'):
            self.lineEdit.show()
            self.lineEdit.setFocus(True)
            self.isLineEditDisplayed = True

    def hideLineEdit(self): 
        self.lineEdit.hide()
        self.isLineEditDisplayed = False