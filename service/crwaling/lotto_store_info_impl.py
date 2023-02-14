import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_store_crawling
from service.compare import data_compare
from save import jdbc_config
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
            for sigugun in storeUtil.address_map[key]:
                postData = storeUtil.get_other_storeinfo_postdata(sido, sigugun)
                speetto = self._parseData(session, url, headers, postData, {"method":"sellerInfoPrintResult"})
                postData = storeUtil.get_lotto645_storeinfo_postdata(sido, sigugun)
                lotto645 = self._parseData(session, url, headers, postData, {"method":"sellerInfo645Result"})
                storeDataes = data_compare.StoreInfoCompare().compareStores(speetto, lotto645, sido, sigugun)
                result.append(storeDataes)
        return result
    def _parseData(self, session, url, headers, postData, queryParam):
        return self.storeObject.parseStoreInfo(session, url, headers, postData, queryParam)