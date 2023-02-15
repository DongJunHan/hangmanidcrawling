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
        dataCompare = data_compare.WinHistoryInfoCompare()
        l, unl = dataCompare.compareLotto645HistoryToStoreInfo(1, fristList["lotto645"])
        l2, unl2 = dataCompare.compareLotto645HistoryToStoreInfo(2, secondList["lotto645"])
        
        self.jdbcConfig.save_win_history_data(l)
        self.jdbcConfig.save_win_history_data(l2)

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
        metropolitanCity = ["서울", "인천","울산","광주","부산","제주","대전","대구"]
        for key, value in winUtil.lottoTypes.items():
            queryParam["pageGubun"] = value
            firstResult[key] = {}
            secondResult[key] = {}
            for sido in winUtil.address_map.keys():
                sidoOther = None
                #광역시는 sido뒤에 광역시라고 붙여야 결과가 나옴
                # if key != "lotto645" and sido in metropolitanCity:
                #     if sido != "제주":
                #         sidoOther = sido + "광역시"
                #     else:
                #         sidoOther = "제주도"
                for sigugun in winUtil.address_map[sido]:
                    postData = winUtil.get_win_history_postdata(sido, sigugun)
                    firstHistory, secondHistory = \
                            self._parseData(session, url, headers, postData, queryParam)
                    # if sidoOther is not None:
                    #     postData = winUtil.get_win_history_postdata(sidoOther, sigugun)
                    #     firstHistoryOther, secondHistoryOther = \
                    #         self._parseData(session, url, headers, postData, queryParam)
                        # for i in range(len(firstHistoryOther)):
                            # firstHistory.append(firstHistoryOther[i])
                        # for i in range(len(secondHistoryOther)):
                            # secondHistory.append(secondHistoryOther[i])

                    firstSido[sido+" "+ sigugun] = firstHistory
                    secondSido[sido+" "+ sigugun] = secondHistory
            firstResult[key] = firstSido.copy()
            secondResult[key] = secondSido.copy()
            firstSido.clear()
            secondSido.clear()
        return firstResult, secondResult

    def _parseData(self, session, url, headers, postData, queryParam):
        return self.winObject.parseWinHistory(session, url, headers, postData, queryParam)