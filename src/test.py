# This Python file uses the following encoding: utf-8
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickView
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
form_class = uic.loadUiType("mainWindowUI.ui")[0]\

class tempWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = tempWindow()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
