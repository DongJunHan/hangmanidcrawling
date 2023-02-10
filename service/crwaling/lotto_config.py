import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from service.crwaling import lotto_win_history_impl, lotto_store_info_impl
from service.crwaling import lotto_win_history_crawling, lotto_store_crawling
class LottoConfig:
    def parseWinHistory(self):
        winHistoryImpl = lotto_win_history_impl.WinHistoryImpl(lotto_win_history_crawling.WinHistoryAllByArea())
        return winHistoryImpl.getData()
    
    def parseStoreInfo(self):
        storeInfoImpl = lotto_store_info_impl.StoreInfoImpl(lotto_store_crawling.StoreInfoAllByArea())
        return storeInfoImpl.getData()
        