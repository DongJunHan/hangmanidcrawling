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
        others = data_compare.OtherWinInfoCompare()
        l, unknown = lotto645.compareHistoryToStoreInfo(1, fristList["lotto645"])
        l2, unknown2 = lotto645.compareHistoryToStoreInfo(2, secondList["lotto645"])
        self._save_log_win_history(unknown)
        self._save_log_win_history(unknown2)
            
        ol, unknownOther = others.compareHistoryToStoreInfo(1, fristList)
        ol2, unknownOther2 = others.compareHistoryToStoreInfo(2, secondList)
        self._save_log_win_history(unknownOther)
        self._save_log_win_history(unknownOther2)

        self.jdbcConfig.save_win_history_data(l)
        self.jdbcConfig.save_win_history_data(l2)

        self.jdbcConfig.save_win_history_data(ol)
        self.jdbcConfig.save_win_history_data(ol2)
        
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
                firstSigugun, secondSigugun = \
                        self._parseData(session, url, sido, headers, queryParam)
                firstSido[sido] = firstSigugun.copy()
                secondSido[sido] = secondSigugun.copy()
                firstSigugun.clear()
                secondSigugun.clear()
            firstResult[key] = firstSido.copy()
            secondResult[key] = secondSido.copy()
            firstSido.clear()
            secondSido.clear()
        return firstResult, secondResult

    def _parseData(self, session, url, sido, headers, queryParam):
        return self.winObject.parseWinHistory(session, url, sido, headers, queryParam)
    
    def _save_log_win_history(self, winhistory_data):
        for item in winhistory_data:
            with open("./error_win_history.txt", "a") as f:
                for k,v in item.items():
                    f.write(f"{k}:{str(v)}, ")
                f.write("\n")
            