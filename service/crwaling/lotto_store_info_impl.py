import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_store_crawling
from service.compare import data_compare
from save import jdbc_config
import json
class StoreInfoImpl:
    def __init__(self, storeObject:lotto_store_crawling.StoreInfoByArea):
        self.storeObject = storeObject
        self.jdbcConfig = jdbc_config.JDBCConfig()
    
    def getData(self):
        storeUtil = lotto_store_crawling.StoreInfoUtil()
        url = "https://dhlottery.co.kr/store.do"
        session = storeUtil.get_session()
        headers = storeUtil.get_storeinfo_Headers()
        result = []
        for key in storeUtil.address_map.keys():
            sido = key
            #연금복권/스피또 상점정보와 로또645상점 정보 두 개를 가져와서 
            #StoreInfoCompare를 통하여 같은 상점 정보면 연금복권/스피또 상점정보를 저장
            # 같지 않으면 따로따로 저장.
            #세종시 때는 시도만 있으므로 시도로만 검색하도록 변경
            if len(storeUtil.address_map[key]) > 0:
                for sigugun in storeUtil.address_map[key]:
                    postData = storeUtil.get_other_storeinfo_postdata(sido, sigugun)
                    speetto = self._parseData(session, url, headers, postData, {"method":"sellerInfoPrintResult"})
                    postData = storeUtil.get_lotto645_storeinfo_postdata(sido, sigugun)
                    lotto645 = self._parseData(session, url, headers, postData, {"method":"sellerInfo645Result"})
                    storeDataes = data_compare.StoreInfoCompare().compareStores(speetto, lotto645, sido, sigugun)
                    result.append(storeDataes)
            else:
                postData = storeUtil.get_other_storeinfo_postdata(sido, "")
                speetto = self._parseData(session, url, headers, postData, {"method":"sellerInfoPrintResult"})
                postData = storeUtil.get_lotto645_storeinfo_postdata(sido, "")
                lotto645 = self._parseData(session, url, headers, postData, {"method":"sellerInfo645Result"})
                storeDataes = data_compare.StoreInfoCompare().compareStores(speetto, lotto645, sido, "")
                result.append(storeDataes)
        return result
    def _parseData(self, session, url, headers, postData, queryParam):
        return self.storeObject.parseStoreInfo(session, url, headers, postData, queryParam)