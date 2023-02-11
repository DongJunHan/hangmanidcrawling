import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_win_history_crawling

class WinHistoryImpl:
    def __init__(self, winObject:lotto_win_history_crawling.WinHistoryByArea):
        self.winObject = winObject
    
    def getData(self):
        winUtil = lotto_win_history_crawling.WinInfoUtil()
        queryParam = {}
        firstResult = {}
        secondResult = {}
        firstSido = {}
        secondSido = {}

        headers = winUtil.get_win_history_header()
        url = "https://dhlottery.co.kr/store.do"
        session = winUtil.get_session()
        queryParam["method"] = "topStore"

        for key, value in winUtil.lottoTypes.items():
            queryParam["pageGubun"] = value
            firstResult[key] = {}
            secondResult[key] = {}
            for sido in winUtil.address_map.keys():
                for sigugun in winUtil.address_map[sido]:
                    postData = winUtil.get_win_history_postdata(sido, sigugun)
                    firstHistory, secondHistory = \
                            self._parseData(session, url, headers, postData, queryParam)
                    firstSido[sido+" "+ sigugun] = firstHistory
                    secondSido[sido+" "+ sigugun] = secondHistory
            firstResult[key] = firstSido.copy()
            secondResult[key] = secondSido.copy()
            firstSido.clear()
            secondSido.clear()
        
        return firstResult, secondResult

    def _parseData(self, session, url, headers, postData, queryParam):
        return self.winObject.parseWinHistory(session, url, headers, postData, queryParam)