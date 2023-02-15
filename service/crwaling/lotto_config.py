import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from service.crwaling import lotto_win_history_impl, lotto_store_info_impl
from service.crwaling import lotto_win_history_crawling, lotto_store_crawling
class LottoConfig:
    def __init__(self):
        self.winHistoryImpl = lotto_win_history_impl.WinHistoryImpl(lotto_win_history_crawling.WinHistoryAllByArea())
        self.storeInfoImpl = lotto_store_info_impl.StoreInfoImpl(lotto_store_crawling.StoreInfoAllByArea())
    
    def parseWinHistory(self):
        return self.winHistoryImpl.getData()
    
    def compareAndSaveWinHistory(self, firstRankWinHistory, secondRankWinHistory):
        self.winHistoryImpl.compareAndSaveData(firstRankWinHistory, secondRankWinHistory)

    def parseStoreInfo(self):
        return self.storeInfoImpl.getData()
        