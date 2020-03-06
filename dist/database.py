import sqlite3
import datetime as dt
import re, math

def returnTime(f_format:str):
    """
    현재 시간을 반환한다.
    f_format형태의 string으로 현재 시간을 반환한다.
    *f_format %Y%m%d %H:%M:%S -> YYYYMMDD HH:MM:SS
    """
    d = dt.datetime.today()
    dateStr = d.strftime(f_format)
    day = dateStr[6:9]

    return{
        'Sun' : dateStr.replace('Sun', '일'),
        'Mon' : dateStr.replace('Mon', '월'),
        'Tue' : dateStr.replace('Tue', '화'),
        'Wed' : dateStr.replace('Wed', '수'),
        'Thu' : dateStr.replace('Thu', '목'),
        'Fri' : dateStr.replace('Fri', '금'),
        'Sat' : dateStr.replace('Sat', '토')
    }.get(day, dateStr)

class dbHandler():

    CONST_TBL_REGEX = re.compile('_+[0-9]{8}')

    def __init__(self):
        """
        데이터베이스 핸들러를 초기화 합니다.

        -musicLists.db에 musicList 테이블이 없으면 만듭니다.
        """
        self.con = sqlite3.connect('./musicLists.db')
        self.cur = self.con.cursor()
        
        # 음악 테이블이 존재하는지 확인해서 없으면 만든다
        self.query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='musicList'"
        self.cur.execute(self.query)
        if self.cur.fetchone()[0]==0:
            self.cur.execute('''
            CREATE TABLE musicList (
                songId INTEGER NOT NULL PRIMARY KEY,
                Title TEXT NOT NULL,
                Artist TEXT NOT NULL,
                Count INTEGER NOT NULL,
                Recent TEXT NOT NULL,
                UNIQUE(Title, Artist));''')


    def modifyData(self, f_songId:int, f_targetCol:str, f_targetVal)->None:
        """
        테이블에 있는 셀을 더블클릭해서 값을 수정한 후 엔터를 눌렀을때 데이터베이스의 값을 수정함.

        수정한 후 이상이 없으면 0을, 수정한 후 레이블이 중복되는 경우 -1을 반환함
        """
        print("{} {} {}".format(f_targetCol, f_targetVal, f_songId))
        if f_targetCol != 'Count' :
            f_targetVal = "'"+f_targetVal+"'"
        self.query = '''UPDATE musicList SET {}={} WHERE songId={}'''.format(f_targetCol, f_targetVal, f_songId)
        print(self.query)
        try:
            self.cur.execute(self.query)
        except sqlite3.IntegrityError as UniqueErr:
            raise UniqueErr
        else:
            return

    def getData(self, f_title:str = '', f_artist:str = '')->list:
        self.data = []
        print("현재 검색하는 정보 : '{}', '{}'".format(f_title, f_artist))
        if len(f_title)==0 and len(f_artist)==0 :
            self.query = ("SELECT * FROM musicList ORDER BY recent DESC")
        
        elif len(f_title)==0 :
            self.query = ("SELECT * FROM musicList WHERE artist LIKE'{}%' ORDER BY recent DESC".format(f_artist))
        
        elif len(f_artist)==0 :
            self.query = ("SELECT * FROM musicList WHERE title LIKE '{}%' ORDER BY recent DESC".format(f_title))
        
        else :
            self.query = ("SELECT * FROM musicList WHERE title LIKE '{}%' AND artist LIKE '{}%' ORDER BY recent DESC".format(f_title, f_artist))

        
        self.data.extend(self.cur.execute(self.query).fetchall())
        #print("database.py getData에 사용된 쿼리 : "+self.query)
        #print("database.py getData의 결과 : "+str(self.data))
        return self.data


    def insertData(self, f_title:str='', f_artist:str='')->int:
        print("다음 데이터를 추가합니다 : '{}', '{}'".format(f_title, f_artist))
        """
        insert record into database(into musicList table)

        if one of f_title or f_artist is not filled, it returns 1
        if record inserted by this function is already in musicList database, it returns -1
        if record inserted without any errors, it returns 0
        """

        if len(f_title)==0 or len(f_artist)==0 :
            print("Database.py : 제목과 아티스트가 모두 입력되어야만 데이터베이스에 추가할 수 있습니다")
            return 1
        f_title = f_title.replace("'", "''")
        f_artist = f_artist.replace("'", "''")
        self.query = '''INSERT INTO musicList (Title, Artist, Count, Recent) VALUES('{}', '{}', {}, '{}')'''.format(f_title, f_artist, 1, returnTime('%m.%d(%a) %H:%M'))
        print("{} 삽입에 사용된 쿼리 : {}".format(f_title, self.query))
        try:
            self.cur.execute(self.query)
        except sqlite3.IntegrityError as UniqueErr:
            raise UniqueErr
        else:
            print("dataBase에 성공적으로 값을 입력함 : '{}' '{}'".format(f_title, f_artist))
            # self.con.commit()
            return 0

    def deleteData(self, f_title:str, f_artist:str, commit:bool = False):
        print("다음 데이터를 지웁니다 : '{}', '{}'".format(f_title, f_artist))
        self.query='''DELETE FROM musicList WHERE Title = ? AND Artist=?'''
        self.cur.execute(self.query, (f_title, f_artist))
        if commit:
            self.con.commit()

    def updateData(self, f_songId:int, f_count:int, f_recent:int):
        self.query='''UPDATE musicList SET Count=?, Recent = ? WHERE songId=?'''
        self.cur.execute(self.query, (f_count, f_recent ,f_songId))

    def getInfoById(self, id:int, title:bool, artist:bool, count:bool, recent:bool)->list:
        info = []
        if title:
            info.extend(self.cur.execute("SELECT Title FROM musicList WHERE songId=?", (id,)).fetchone())
        if artist:
            info.extend(self.cur.execute("SELECT Artist FROM musicList WHERE songId=?", (id,)).fetchone())
        if count :
            info.extend(self.cur.execute("SELECT Count FROM musicList WHERE songId=?", (id,)).fetchone())
        if recent :
            info.extend(self.cur.execute("SELECT Recent FROM musicList WHERE songId=?", (id,)).fetchone())

        return info

    def getInfoByTA(self, title:str, artist:str, songId:bool, count:bool, recent:bool):
        info = []
        if songId:
            info.extend(self.cur.execute("SELECT songId FROM musicList WHERE Title=? AND Artist=?", (title, artist)).fetchone())
        if count :
            info.extend(self.cur.execute("SELECT Count FROM musicList WHERE Title=? AND Artist=?", (title, artist)).fetchone())
        if recent :
            info.extend(self.cur.execute("SELECT Recent FROM musicList WHERE Title=? AND Artist=?", (title, artist)).fetchone())

        return info