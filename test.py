import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import unittest
import json
import re
import requests
from html.parser import HTMLParser
from service.crwaling import lotto_store_crawling, lotto_win_history_crawling, lotto_config
from service.compare import data_compare
from service.save import jdbc_config
from dto import util

class TestStoreInfo(unittest.TestCase):
    def test_store_info(self):
        storeInfo = lotto_config.LottoConfig().parseStoreInfo()
        jdbc_config.JDBCConfig().save_store_data(storeInfo)
class TestWinInfo(unittest.TestCase):
    dataCompare = data_compare.WinHistoryInfoCompare()
    save = jdbc_config.JDBCConfig()

    def test_win_info(self):
        first_win_info , second_win_info = lotto_config.LottoConfig().parseWinHistory()
        with open("./win_history_노원.json", "w") as f:
            f.write(first_win_info.__str__())

        with open("./win_history_노원_2.json", "w") as f:
            f.write(second_win_info.__str__())
    
    def test_query(self):
        with open("./win_history_노원.json") as f:
            a = json.load(f)
            firstRankWinHistory = {}
            firstRankWinHistory["lotto645"] = a
        with open("./win_history_노원_2.json") as f:
            a = json.load(f)
            secondRankWinHistory = {}
            secondRankWinHistory["lotto645"] = a

        lotto_config.LottoConfig().compareAndSaveWinHistory(firstRankWinHistory, secondRankWinHistory)
        
        # self.save.save_win_history_data(result)
    

    def test_regex(self):
        file_name = "nodata_1win.html"
        with open(f"./{file_name}","r") as f:
            html = f.read()
        #parse table tag
        p = re.compile("(?<=\<table class\=\"tbl_data tbl_data_col\">)(.*?)(?=<\/tbody>)",re.DOTALL)
        m = p.findall(html)
        arr = []
        for i in m:
            i = i.replace("\n","").replace("\t","").replace("\r","")
            #parse tr tag
            p = re.compile("(?<=\<tr>)(.*?)(?=<\/tr>)")
            a = p.findall(i)
            arr.append(a)
        key = {}
        td = {}
        #parse th tag
        for i in range(len(arr)):
            td[str(i+1) + "st"] = {}
            for j in range(len(arr[i])):
                p = re.compile("(?<=\<th scope\=\"col\">)(.*?)(?=<\/th>)")
                if p.search(arr[i][j]):
                    key[str(i+1) + "st"] = p.findall(arr[i][j])
                else:
                    #parse td tag
                    p = re.compile("(?<=\<td>)(.*?)(?=<\/td>)")
                    if p.search(arr[i][j]):
                        td[str(i+1) + "st"][j] = p.findall(arr[i][j])
                    
                    p = re.compile("(?<=\<td class=\"lt\">)(.*?)(?=<\/td>)", re.DOTALL)
                    if p.search(arr[i][j]):
                        td[str(i+1) + "st"][j] = p.findall(arr[i][j])
        
        #save data
        for k1,v1 in td.items():
            for k, v in v1.items():
                p = re.compile("(?<=\<a href=\"\#\" class=\"btn_search\" onClick=\"javascript\:showMapPage\(\\')(.*?)(?=\\'\)\")")
                for i in range(len(v)):
                    if p.search(v[i]):
                        td[k1][k][i] = p.findall(v[i])[0]
        print(key)
        print(td)
        st1 = td["1st"]
        print(len(st1))
    
    def test_long_lat(self):
        valueHistory = {1: ['1', '스파', '자동 ', '서울 노원구 동일로 1493 상계주공아파트(10단지) 주공10단지종합상가111', '11100773']}
        winInfo = lotto_win_history_crawling.WinInfoUtil()
        value = winInfo.get_latitude_longitude(1,valueHistory)
        print(value)
