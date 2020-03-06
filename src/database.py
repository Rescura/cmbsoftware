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

        -videoList.db에 videoList 테이블이 없으면 만듭니다.
        """
        self.con = sqlite3.connect('./videoLists.db')
        self.cur = self.con.cursor()
        
        # 음악 테이블이 존재하는지 확인해서 없으면 만든다
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS videoList (
            videoId TEXT UNIQUE,
            videoTitle TEXT,
            videoDuration TEXT,
            thumbnailUrl TEXT NOT NULL ,
            count INTEGER DEFAULT 0,
            recent TEXT DEFAULT '없음'); 
            ''')

    def getDataFromDB(self, f_videoId):
        query = '''SELECT videoId, count, recent FROM videoList WHERE videoId = ?'''
        result =  self.con.execute(query, (f_videoId,)).fetchone()
        if result is None:
            print("[Database] 조회 결과 없음")
            return False, {"mod_count": 0, "mod_recent": "없음"}
        print("[Database] 조회 결과 있음")
        return True, {"mod_count": result[0], "mod_recent": result[1]}
        
    def processData(self, f_ytdata):
        dataFromBoth = []
        finalData = []
        for data in f_ytdata:
            isInDb, dbData = self.getDataFromDB(data["mod_videoId"])
            data["mod_count"] = dbData["mod_count"]
            data["mod_recent"] = dbData["mod_recent"]
            
            if isInDb:
                dataFromBoth.append(data)
                f_ytdata.remove(data)
            
        finalData.extend(dataFromBoth)
        finalData.extend(f_ytdata)

        return finalData