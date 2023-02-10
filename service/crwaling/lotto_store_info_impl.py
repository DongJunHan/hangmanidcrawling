import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_store_crawling
from service.compare import data_compare
from save import DB_save
class StoreInfoImpl:
    def __init__(self, storeObject:lotto_store_crawling.StoreInfoByArea):
        self.storeObject = storeObject
    
    def getData(self):
        storeUtil = lotto_store_crawling.StoreInfoUtil()
        url = "https://dhlottery.co.kr/store.do"
        session = storeUtil.get_session()
        headers = storeUtil.get_storeinfo_Headers()
        
        for key in storeUtil.address_map.keys():
            sido = key
            for sigugun in storeUtil.address_map[key]:
                postData = storeUtil.get_storeinfo_postdata(sido, sigugun)
                speetto = self._parseData(session, url, headers, postData, {"method":"sellerInfoPrintResult"})
                lotto645 = self._parseData(session, url, headers, postData, {"method":"sellerInfo645Result"})
                storeDataes = data_compare.StoreInfoCompare().compareStores(speetto, lotto645, sido, sigugun)
                DB_save.StoreInfoSave().save_store_data(storeDataes)

    def _parseData(self, session, url, headers, postData, queryParam):
        return self.storeObject.parseStoreInfo(session, url, headers, postData, queryParam)