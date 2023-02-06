"""
1. 시/도 로 군들을 검색 (https://dhlottery.co.kr/store.do?method=searchGUGUN)
2. 군들을 통해서 주소 검색 (https://dhlottery.co.kr/store.do?method=sellerInfo645Result)
or
1. 시/도, 도/군들을 가지고 있다가 바로 2번을 수행
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import uuid
from datetime import datetime
import re
import requests
import json
import html
from dto import hangmaniDTO, util
from compare import data_compare
from save import DB_save


class ParseStore:
    def __init__(self):
        self.address_map = util.Variable().address_map
        self.util = util.Utils()

    def parseStoreInfo(self, url, sido, sigugun, queryString:dict=None):
        """
            Args:
                url : str
                sigugun : str 주소 구/군
                sido : str 주소 시/도
                queryString : dict
            Return:
                list
        """
        result = []
        headers = {
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate, br",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"

        }
        postData = {
            "searchType":"1",
            "nowPage": "1",
            "rtlrSttus": "001",
            "sltGUGUN": sigugun,
            "sltSIDO": sido
        }
        param = {}
        if queryString is not None:
            for key, value in queryString.items():
                param[key] = value
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        validateInfo = None
        for i in range(20):
            response = session.request("POST",url,headers=headers, data=postData, params=param)
            jsonData = response.json()
            # with open("log.log", "a") as f:
                # f.write(f"[{sido}][{sigugun}] nowPage: {postData['nowPage']}, query string: {param['method']}\n")
            try:
                if validateInfo is not None:
                    if "SHOP_NM" in jsonData["arr"][0].keys():
                        if validateInfo == jsonData["arr"][0]["SHOP_NM"]:
                            break
                        else:
                            validateInfo = jsonData["arr"][0]["SHOP_NM"]
                    else:
                        if validateInfo == jsonData["arr"][0]["FIRMNM"]:
                            break
                        else:
                            validateInfo = jsonData["arr"][0]["FIRMNM"]
                else:
                    if len(jsonData["arr"]) == 0:
                        break
                    if "SHOP_NM" in jsonData["arr"][0].keys():
                        validateInfo = jsonData["arr"][0]["SHOP_NM"]
                    else:
                        validateInfo = jsonData["arr"][0]["FIRMNM"]

                postData["nowPage"] = str(int(postData["nowPage"]) + 1)
                for i in jsonData["arr"]:
                    result.append(i)
            except Exception as e:
                date, time = self.util.get_current_time()
                with open(f"./log/error_log.log","a") as f:
                    f.writ(f"[{time}] {sigugun},{queryString['method']},{postData['nowPage']}")

                with open(f"./errorDump/{sigugun}_{queryString['method']}_{date}.json","w") as f:
                    f.write(json.dumps(jsonData))
                """
                    TODO 개발자가 알 수 있도록 알람을 띄워야할거같음
                """
                raise e
        return result
        
    def getStoreData(self):
        url = "https://dhlottery.co.kr/store.do"
        for key in self.address_map.keys():
            sido = key
            for sigugun in self.address_map[key]:
                speetto = self.parseStoreInfo(url, sido, sigugun, {"method":"sellerInfoPrintResult"})
                lotto645 = self.parseStoreInfo(url, sido, sigugun, {"method":"sellerInfo645Result"})
                storeDataes = data_compare.StoreInfoCompare().compareStores(speetto, lotto645, sido, sigugun)
                DB_save.StoreInfoSave().save_store_data(storeDataes)

