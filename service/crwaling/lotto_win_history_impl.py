import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_win_history_crawling
from service.compare import data_compare
from service.save import jdbc_config

class WinHistoryImpl:
    def __init__(self, winObject:lotto_win_history_crawling.WinHistoryByArea):
        self.winObject = winObject
        self.jdbcConfig = jdbc_config.JDBCConfig()
    
    def compareAndSaveData(self, fristList, secondList):
        lotto645 = data_compare.Lotto645WinInfoCompare()
        for k in fristList.keys():
            if k == "lotto645":
                l, unl = lotto645.compareHistoryToStoreInfo(1, fristList[k])
                l2, unl2 = lotto645.compareHistoryToStoreInfo(2, secondList[k])
                self.jdbcConfig.save_win_history_data(l)
                self.jdbcConfig.save_win_history_data(l2)
            # else:
                # l, unl = lotto645.compareHistoryToStoreInfo(1, fristList[k])
                # l2, unl2 = lotto645.compareHistoryToStoreInfo(2, secondList[k])
                # self.jdbcConfig.save_win_history_data(l)
                # self.jdbcConfig.save_win_history_data(l2)
        
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
                firstSido, secondSido = \
                        self._parseData(session, url, sido, headers, queryParam)
            firstResult[key] = firstSido.copy()
            secondResult[key] = secondSido.copy()
            firstSido.clear()
            secondSido.clear()
        return firstResult, secondResult

    def _parseData(self, session, url, sido, headers, queryParam):
        return self.winObject.parseWinHistory(session, url, sido, headers, queryParam)