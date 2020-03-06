import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import QtQml.Models 2.2

Item{
    signal onRightClick(double x, double y, string videoId)
    signal onLeftClick(double x, double y, string videoId)
    /*
    ListModel{
        id:resultModel
        
        ListElement{
            mod_thumbnailUrl : "https://i.ytimg.com/vi/tXV7dfvSefo/hqdefault.jpg"
            mod_videoId:"tXV7dfvSefo"
            mod_videoTitle : "버스커 버스커 (Busker Busker) - 벚꽃 엔딩"
            mod_channelTitle : "Stone Music Entertainment"
            mod_duration:"4:55"
            mod_count : 1
            mod_recent : "2020-02-24(월) 기훈-점심"
            mod_stage : "Updated"
        }
        ListElement{
            mod_thumbnailUrl : "https://i.ytimg.com/vi/VgwcPiCjQ-0/hqdefault.jpg"
            mod_videoId : "VgwcPiCjQ-0"
            mod_videoTitle : "Oh Wonder - Lose It"
            mod_channelTitle : "OhWonderMusicVEVO"
            mod_duration : "3:41"
            mod_count : 0
            mod_recent : "없음"
            mod_stage : "Normal"
        }
    }
    */
    

    Component{

        id:resultDelegate
        RowLayout{

            spacing: 2
            Image{
                id:thumbnail
                source: mod_thumbnailUrl
                Layout.maximumHeight:90
                Layout.maximumWidth:120

                MouseArea{
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    anchors.fill : parent
                    onClicked: {
                        if(mouse.button == Qt.RightButton){
                            console.log(mod_videoTitle + "마우스 우클릭")
                            onRightClick(mouseX, mouseY, mod_videoId)
                            //TODO: 우클릭 메뉴 만들기
                        }
                        else if(mouse.button == Qt.LeftButton){
                            console.log(mod_videoTitle + "마우스 왼클릭")
                            onLeftClick(mouseX, mouseY, mod_videoId)
                            //TODO : 현재 선택한 video 바꾸기
                        }
                    }
                }
            }
            //TODO: 영상 길이를 알려주는 조그만 Text 표시하기

                ColumnLayout{

                    spacing:2
                    Text{
                        id: songTitle
                        text:mod_videoTitle
                        font.family: "NanumBarunGothic"
                        font.bold : true
                        font.pixelSize: 17
                    }

                    Text{
                        id:channelTitle
                        text:mod_channelTitle
                        font.family: "NanumBarunGothic"
                        font.pixelSize: 12
                    }
                    Text{
                        id:count
                        text:"최근 2주간 튼 횟수 : "+mod_count
                        font.family: "NanumBarunGothic"
                        font.pixelSize: 10
                    }
                    Text{
                        id:recent
                        text:mod_recent
                        font.family: "NanumBarunGothic"
                        font.pixelSize: 10
                    }
                }
        }
    }

    ListView{
        id:songList
        model:resultModel   
        delegate:resultDelegate
        anchors.fill:parent
        clip:false
    }

}


/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
