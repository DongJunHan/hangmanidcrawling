import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.crwaling import lotto_store_crawling
from service.crwaling import lotto_win_history_crawling
# import jdbc

if __name__ == "__main__":

    parse_store = lotto_store_crawling.ParseStore()
    parse_win = lotto_win_history_crawling.WinInfo()
    parse_store.getStoreData()
    # parse_win.test()
    # parse_win.getStoreData()
    # parse_win.test()
    # a = jdbc.execute("select * from store",True)
    # print(a)
    # parse_win.test()
