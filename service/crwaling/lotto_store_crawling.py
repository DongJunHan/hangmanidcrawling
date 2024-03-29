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
import abc
from dto import hangmaniDTO, util
from compare import data_compare
from save import jdbc_config
class StoreInfoByArea(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parseStoreInfo(self, session, url, headers, postData, queryParam):
        raise NotImplemented

class StoreInfoAllByArea(StoreInfoByArea):
    def __init__(self):
        self.storeUtil = StoreInfoUtil()

    def parseStoreInfo(self, session, url, headers, postData, queryParam):
        """
            Args:
                session: requests.Session
                url : str
                headers : dict 
                postData : dict
                queryParam : dict
            Return:
                list
        """
        result = []
        
        validateInfo = None
        #check total Page
        response = session.request("POST",url,headers=headers, data=postData, params=queryParam)
        jsonData = response.json()
        if "totalPage" not in jsonData.keys():
            return result
        for i in range(1, int(jsonData["totalPage"])+1):
            # if queryParam['method'] == 'sellerInfo645Result':
            #     with open("lotto645_부평구.json", 'a') as fp:
            #         json.dump(jsonData['arr'], fp, ensure_ascii=False)
            # elif queryParam['method'] == 'sellerInfoPrintResult':
            #     with open("annual_부평구.json", 'a') as fp:
            #         json.dump(jsonData['arr'], fp, ensure_ascii=False)
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

                postData["nowPage"] = str(i + 1)
                for i in jsonData["arr"]:
                    result.append(i)
                response = session.request("POST",url,headers=headers, data=postData, params=queryParam)
                jsonData = response.json()
            except Exception as e:
                date, time = self.storeUtil.util.get_current_time()
                with open(f"./log/error_log.log","a") as f:
                    f.writ(f"[{time}] {sigugun},{queryParam['method']},{postData['nowPage']}")

                with open(f"./errorDump/{sigugun}_{queryParam['method']}_{date}.json","w") as f:
                    f.write(json.dumps(jsonData))
                """
                    TODO 개발자가 알 수 있도록 알람을 띄워야할거같음
                """
                raise e
        
        return result

class StoreInfoUtil:
    def __init__(self):
        self.address_map = util.Variable().address_map
        self.util = util.Utils()
    
    def get_storeinfo_Headers(self):
        headers = {
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate, br",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        return headers

    def get_lotto645_storeinfo_postdata(self, sido, sigugun):
        postData = {
            "searchType":"3",
            "nowPage": "1",
            "rtlrSttus": "001",
            "sltGUGUN2": sigugun,
            "sltSIDO2": sido
        }
        return postData
    def get_other_storeinfo_postdata(self, sido, sigugun):
        postData = {
            "searchType":"1",
            "nowPage": "1",
            "rtlrSttus": "001",
            "sltGUGUN": sigugun,
            "sltSIDO": sido
        }
        return postData

    def get_session(self):
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        return session

