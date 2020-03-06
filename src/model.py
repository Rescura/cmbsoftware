from PyQt5.QtCore import *
from PyQt5.QtSql import *
import database as dbMod
import pprint

class ResultModel(QAbstractListModel):
    """
    ResultModel은 resultTabQML 파일에서 보여줄 데이터를 담고있는 모델이다.
    """
    ThumbnailUrlRole = Qt.UserRole + 1
    VideoIdRole = Qt.UserRole + 2
    VideoTitleRole = Qt.UserRole + 3
    ChannelTitleRole = Qt.UserRole + 4
    DurationRole = Qt.UserRole + 5
    CountRole = Qt.UserRole + 6
    RecentRole = Qt.UserRole + 7
    StageRole = Qt.UserRole + 8

    _roleNames =  {
        ThumbnailUrlRole: b'mod_thumbnailUrl',
        VideoIdRole : b'mod_videoId',
        VideoTitleRole : b'mod_videoTitle',
        ChannelTitleRole : b'mod_channelTitle',
        DurationRole : b'mod_duration',
        CountRole : b'mod_count',
        RecentRole: b'mod_recent',
        StageRole : b'mod_stage'
        }

    def __init__(self, data = None):
        super().__init__()
        self.songs = data

        pprint.pprint(self.songs)

    def roleNames(self):
        return self._roleNames

    def rowCount(self, index, parent=QModelIndex()):
        """
        현재 모델에 데이터가 몇개 있는지를 반환한다
        """
        return len(self.songs)

    def data(self, index:QModelIndex, role):
        """
        현재 모델의 데이터를 반환한다
        """
        row = index.row()
        print("[ResultModel] Row:{}, Role:{} 데이터 요청".format(row, role))

        if role == self.ThumbnailUrlRole:
            return self.songs[row]["mod_thumbnailUrl"]

        elif role == self.VideoIdRole:
            return self.songs[row]["mod_videoId"]

        elif role == self.VideoTitleRole:
            return self.songs[row]["mod_videoTitle"]

        elif role == self.ChannelTitleRole:
            return self.songs[row]["mod_channelTitle"]

        elif role == self.DurationRole:
            return self.songs[row]["mod_duration"]

        elif role == self.CountRole:
            return self.songs[row]["mod_count"]

        elif role == self.RecentRole:
            return self.songs[row]["mod_recent"]

        elif role == self.StageRole:
            return self.songs[row]["mod_stage"]

    #def flags(self, index:int):
    #    """
    #    Qt::ItemIsEditable 값을 반환하는 함수
    #    이 값이 반환되어야 QML에서 사용자가 데이터를 수정할 수 있다.
    #    """
    #    return  Qt.ItemIsEnabled, Qt.ItemIsEditable

    #def setData(self, index:QModelIndex, value, role)->bool:
    #    """
    #    QML에서 데이터를 변경할때 쓰이는 함수
    #    """
    #    if role == Qt.EditRole and index.isValid():
    #        self.songs[]
#
    #    else
    #        return False
