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
    
    def test_save_lotto_type(self):
        jdbc_config.JDBCConfig().save_store_lotto_types()

class TestCompareInfo(unittest.TestCase):
    def test_store_compare(self):
        with open('annual_speetto.json') as f:
            originData = json.load(f)
        with open('lotto645.json') as f:
            compareData = json.load(f)
        ret = data_compare.StoreInfoCompare().compareStores(originData["arr"], compareData["arr"], '서울', '강남구')
        print(ret)



class TestWinInfo(unittest.TestCase):
    # dataCompare = data_compare.WinHistoryInfoCompare()
    # save = jdbc_config.JDBCConfig()

    def test_win_info(self):
        first_win_info , second_win_info = lotto_config.LottoConfig().parseWinHistory()
        # print(first_win_info)
        # print(second_win_info)
        with open("./win_history.json", "w") as f:
            f.write(first_win_info.__str__())

        with open("./win_history_2.json", "w") as f:
            f.write(second_win_info.__str__())
    
    def test_query(self):
        with open("./win_history_부평구.json") as f:
            a = json.load(f)
            firstRankWinHistory = a
            # firstRankWinHistory = {}
            # firstRankWinHistory["lotto645"] = a
        with open("./win_history_부평구_2.json") as f:
            a = json.load(f)
            secondRankWinHistory = a
            # secondRankWinHistory = {}
            # secondRankWinHistory["lotto645"] = a
        lotto_config.LottoConfig().compareAndSaveWinHistory(firstRankWinHistory, secondRankWinHistory)
        
        # self.save.save_win_history_data(result)
    

    def test_regex(self):
        file_name = "adsasd.html"
        with open(f"./{file_name}","r") as f:
            response = f.read()
        #parse table tag
        p = re.compile("(?<=\<table class\=\"tbl_data tbl_data_col\">)(.*?)(?=<\/table>)",re.DOTALL)
        m = p.findall(response)
        trTags = {}
        key = {}
        for i in range(len(m)):
            m[i] = m[i].replace("\n","").replace("\t","").replace("\r","")
            #parse thead tag
            p = re.compile("(?<=\<thead>)(.*?)(?=<\/thead>)")
            thead = p.findall(m[i])[0]
            p = re.compile("(?<=\<th scope\=\"col\">)(.*?)(?=<\/th>)")
            key[str(i+1)+"st"] = p.findall(thead)
            #parse tbody tag
            p = re.compile("(?<=\<tbody>)(.*?)(?=<\/tbody>)")
            tbody = p.findall(m[i])[0]
            #parse tr tag
            p = re.compile("(?<=\<tr>)(.*?)(?=<\/tr>)")
            trTags[str(i+1)+"st"] = p.findall(tbody)
        tdTags = {}
        for k, v in trTags.items():
            #(\<tr>)(.*?)(<\/tr>) 전방탐색, 후방탐색을 사용하면 <td></td> 같은 경우 가져오지 못하고 뒤에것과 겹친다
            p = re.compile("(\<td>)(.*?)(<\/td>)")
            classLt = re.compile("(\<td\sclass=\"lt\">)(.*?)(\<\/td>)")
            latiLongi = re.compile("(\<a href=\"\#\" class=\"btn_search\" onClick=\"javascript\:showMapPage\(\\')(.*?)(\\'\)\")")
            tdTags[k] = []
            tdTag = {}
            for tr in range(len(v)):
                td = p.findall(v[tr])
                for i in range(len(td)):
                    if "javascript" in td[i][1]:
                        td[i] = latiLongi.findall(td[i][1])[0]
                    tdTag[key[k][i]] = td[i][1]
                td = classLt.findall(v[tr])
                for i in range(len(td)):
                    tdTag[key[k][2]] = td[i][1]
                tdTags[k].append(tdTag.copy())
                print(tdTags)
                print("========")
            
        print(tdTags)
    def test_long_lat(self):
        valueHistory = {1: ['1', '스파', '자동 ', '서울 노원구 동일로 1493 상계주공아파트(10단지) 주공10단지종합상가111', '11100773']}
        winInfo = lotto_win_history_crawling.WinInfoUtil()
        value = winInfo.get_latitude_longitude(1,valueHistory)
        print(value)
