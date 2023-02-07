import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import unittest
from service.crwaling import lotto_store_crawling, lotto_win_history_crawling
class TestStoreInfo(unittest.TestCase):
    def test_store_info(self):
        pass


class TestWinInfo(unittest.TestCase):
    win = lotto_win_history_crawling.WinInfo()

    def test_win_info(self):
        queryString = {}
        queryString["method"] = "topStore"
        queryString["pageGubun"] = self.win.lottoTypes["lotto645"]
        sido = "서울"
        sigugun = "마포구"
        url = "https://dhlottery.co.kr/store.do"
        self.win._parseAllWinInfoByArea(url, sido, sigugun, queryString)
        print(self.win.first_win_info)
        print(self.win.second_win_info)
