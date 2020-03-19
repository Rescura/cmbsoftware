import requests
import pprint
import re
import isodate

APIKEY = 'AIzaSyCW46MBJpp66t8-l3QbLVjylQQacwPmTlc'

def getDataFromYoutube(maxResult:int, f_title:str='', f_artist:str='', pageToken:str='')->str:
  """
  제목, 아티스트를 통해 유튜브 동영상의 videoId와 썸네일 주소를 반환함
  
  검색결과의 다음 페이지를 요청하는 nextPageToken과 받은 데이터를 반환한다.
  """

  snippetQueries = {
    "key": APIKEY,
    "part": "snippet",
    "order": "relevance",
    "q": f_artist + '+' + f_title,
    "pageToken" : pageToken,
    "type": "video",
    "maxResults": maxResult
  }
  contentDetailQueries = {
    "key": APIKEY,
    "part": "contentDetails",
    "id":""
  }
  snippetReqUrl = ' https://www.googleapis.com/youtube/v3/search'
  contentDetailUrl = 'https://www.googleapis.com/youtube/v3/videos'
  returnData = []

  #snippet 데이터를 받아옴
  snippetRes = requests.get(snippetReqUrl, params = snippetQueries)
  snippetData = snippetRes.json()

  nextPageToken = snippetData["nextPageToken"]

  for idx, snippetItem in enumerate(snippetData["items"]):
    snippet = snippetItem["snippet"]

    videoId = snippetItem["id"]["videoId"].replace("&#39;", "'")
    videoTitle = snippet["title"].replace("&#39;", "'")
    channelTitle = snippet["channelTitle"].replace("&#39;", "'")
    thumbnailUrl = snippet["thumbnails"]["high"]["url"]

    returnData.append(
      {
      "mod_thumbnailUrl": thumbnailUrl,
      "mod_videoId":videoId,
      "mod_videoTitle": videoTitle,
      "mod_channelTitle": channelTitle,
      "mod_duration": "",
      "mod_count": 0,
      "mod_recent" : "없음"
      })

    contentDetailQueries["id"] = contentDetailQueries["id"] + videoId + ','
    
  detailRes = requests.get(contentDetailUrl, params=contentDetailQueries)
  detailData = detailRes.json()
  # pprint.pprint(detailData)

  for idx, detailItem in enumerate(detailData["items"]):
    detail = detailItem["contentDetails"]
    rawDuration = detail["duration"]
    duration = str(isodate.parse_duration(rawDuration))
    returnData[idx]["mod_duration"] = duration
  
  return nextPageToken, returnData

# 유튜브 영상 보기 
# https://www.youtube.com/watch?v + (videoId)
