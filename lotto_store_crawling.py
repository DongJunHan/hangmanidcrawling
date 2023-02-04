"""
1. 시/도 로 군들을 검색 (https://dhlottery.co.kr/store.do?method=searchGUGUN)
2. 군들을 통해서 주소 검색 (https://dhlottery.co.kr/store.do?method=sellerInfo645Result)
or
1. 시/도, 도/군들을 가지고 있다가 바로 2번을 수행
"""
from dataclasses import dataclass, field
from typing import ClassVar
from typing import List
import jdbc
import uuid
from datetime import datetime
import re


@dataclass(unsafe_hash=True)
class LottoType:
    lottoId        : str                                       #복권 PK
    lottoCode      : str                                       #복권 종류 코드
    lottoName      : str                                       #복권 이름
    def __init__(self):
        pass

@dataclass(unsafe_hash=True)
class LottoHandleList:
    storeId        : str                                       #상점 ID PK값
    lottoList      : list                                      #로또 리스트 DTO
    def __init__(self):
        pass

@dataclass(unsafe_hash=True)
class WinHistory:
    storeId        : str                                       #상점 ID PK값
    winRound       : int                                       #당첨 회차
    winRank        : int                                       #당첨 등수
    lottoType      : ClassVar[LottoType]                       #로또 리스트 DTO
    def __init__(self):
        pass

@dataclass(unsafe_hash=True)
class StoreInfo:
    storeUuid      : str                                       #상점 ID PK값
    storeName      : str                                       #상점 이름
    storeAddress   : str                                       #상점 주소
    storeLatitude  : float                                     #상점 위도
    storeLongitude : float                                     #상점 경도
    storeBizNo     : str                                       #사업자 번호
    storeTelNum    : str                                       #상점 전화번호
    storeMobileNum : str                                       #상점 핸드폰번호
    storeOpenTime  : str                                       #영업 시작 시간
    storeCloseTime : str                                       #영업 폐점 시간
    storesido      : str                                       #상점 시/도
    storesigugun   : str                                       #상점 시구군
    storeisActivity: bool = False                              #폐점 여부
    lottoHandle    : ClassVar[LottoHandleList]                 #취급 복권 리스트
    # winHistory     : WinHistory                                #당첨 내역

    def __init__(self, storeUuid = None, storeName = None, storeAddress = None, storeLatitude = None,
                    storeLongitude = None, storeBizNo = None, storeTelNum = None,
                    storeMobileNum = None, storeOpenTime = None, storeCloseTime = None, 
                    lottoHandle = None):
        self.storeUuid = storeUuid
        self.storeName = storeName
        self.storeAddress = storeAddress
        self.storeLatitude = storeLatitude
        self.storeLongitude = storeLongitude
        self.storeBizNo = storeBizNo
        self.storeTelNum = storeTelNum
        self.storeMobileNum = storeMobileNum
        self.storeOpenTime = storeOpenTime
        self.storeCloseTime = storeCloseTime
        self.lottoHandle = lottoHandle
        



address_map = {
    # "서울" : ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구","노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구",
    #         "성동구","성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"],
    # "경기" : ["가평군","고양시 덕양구","고양시 일산동구","고양시 일산서구","과천시","광명시","광주시","구리시","군포시","김포시","남양주시","동두천시",
    #         "부천시","성남시 분당구","성남시 수정구","성남시 중원구","수원시 권선구","수원시 영통구","수원시 장안구","수원시 팔달구","시흥시","안산시 단원구",
    #         "안산시 상록구","안성시","안양시 동안구","안양시 만안구","양주시","양평군","여주시","연천군","오산시","용인시 기흥구","용인시 수지구","용인시 처인구",
    #         "의왕시","의정부시","이천시","파주시","평택시","포천시","하남시","화성시"],
    # "부산" : ["강서구","금정구","기장군","남구","동구","동래구","부산진구","북구","사상구","사하구","서구","수영구","연제구","영도구","중구","해운대구"],
    # "대구" : ["남구","달서구","달성군","동구","북구","서구","수성구","중구"],
    # "인천" : ["강화군","계양구","남동구","동구","미추홀구","부평구","서구","연수구","옹진군","중구"],
    # "대전" : ["대덕구","동구","서구","유성구","중구"],
    # "울산" : ["남구","동구","북구","울주군","중구"],
    # "강원" : ["강릉시","고성군","동해시","삼척시","속초시","양구군","양양군","영월군","원주시","인제군","정선군","철원군","춘천시","태백시","평창군",
    #         "홍천군","화천군","횡성군"],
    # "충북" : ["괴산군","단양군","보은군","영동군","옥천군","음성군","제천시","증평군","진천군","청주시 상당구","청주시 서원구","청주시 청원구",
    #         "청주시 흥덕구","충주시"],
    # "충남" : ["계룡시","공주시","금산군","논산시","당진시","보령시","부여군","서산시","서천군","아산시","예산군","천안시 동남구","천안시 서북구",
    #         "청양군","태안군","홍성군"],
    # "광주" : ["광산구","남구","동구","북구","서구"],
    # "전북" : ["고창군","군산시","김제시","남원시","무주군","부안군","순창군","완주군","익산시","임실군","장수군","전주시 덕진구","전주시 완산구",
    #         "정읍시","진안군"],
    # "전남" : ["강진군","고흥군","곡성군","광양시","구례군","나주시","담양군","목포시","무안군","보성군","순천시","신안군","여수시","영광군","영암군",
    #         "완도군","장성군","장흥군","진도군","함평군","해남군","화순군"],
    # "경북" : ["경산시","경주시","고령군","구미시","군위군","김천시","문경시","봉화군","상주시","성주군","안동시","영덕군","영양군","영주시","영천시",
    #         "예천군","울릉군","울진군","의성군","청도군","청송군","칠곡군","포항시 남구","포항시 북구"],
    # "경남" : ["거제시","거창군","고성군","김해시","남해군","밀양시","사천시","산청군","양산시","의령군","진주시","창녕군","창원시 마산합포구","창원시 마산회원구",
    #         "창원시 성산구","창원시 의창구","창원시 진해구","통영시","하동군","함안군","함양군","합천군"],
    "제주" : ["서귀포시","제주시"],
    "세종" : []
}
import requests
import json
import html
from html.parser import HTMLParser
"""
    TODO. 
    1. 운영시 매주 한 번 프로그램을 돌려서 상점이 새로 추가됐는지, 기존의 상점이 없어졌는지 확인이 필요.
    2. 당첨 결과 매주 업데이트 로직.
    3. 당첨 결과 262회부터 파싱.

"""
class WinHTMLParser(HTMLParser):
    is_group_content = False
    first_result = []
    second_result = []
    first_win = False
    second_win = False
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_group_content = False
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            for i in attrs:
                if i[0] == "class" and i[1] == "group_content":
                    self.is_group_content = True
    
    def handle_endtag(self, tag):
        if tag == "table":
            self.is_group_content = False
    
    def handle_data(self, data):
        if self.is_group_content == True:
            if data == "1등 배출점":
                self.first_win = True
                self.second_win = False
                return
            if data == "2등 배출점":
                self.first_win = False
                self.second_win = True
                return
            data = data.replace("\n","").replace("\t","").replace(" ","")
            if len(data) != 0:
                if self.first_win:
                    self.first_result.append(data)
                elif self.second_win:
                    self.second_result.append(data)
class Utils:
    def get_current_time():
        """
            Args:
                None
            Returns:
                timeformat: str
                dateformat: str
        """
        current = datetime.now()
        time = current.strftime("%H:%M:S")
        date = current.strftime("%y%m%d")
        return date,time
class ParseStore:
    def _remove_special_symbol(self, text):
        """
            Args:
                text: str
            Return:
                result: str
        """
        escape = html.parser
        while "&#" in text:
            text = escape.unescape(text)
        return text

    def compareStores(self, originData, compareData, sido, sigugun):
        """
            Args:
                originData  : dict
                compareData : dict
                sido        : str
                sigugun     : str
            Return:
                list[StoreInfo]
        """
        result = list()
        for i in range(len(compareData)):
            comTelNum = compareData[i]["RTLRSTRTELNO"] #tel number
            comTude = [str(compareData[i]["LATITUDE"]), str(compareData[i]["LONGITUDE"])] #latitude, longitude
            equalFlag = False
            for j in range(len(originData)):
                settingData = originData
                oriTude = [originData[j]["ADDR_LAT"], originData[j]["ADDR_LOT"]] #latitude, longitude
                oriTelNum = originData[j]["TELEPHONE"]
                if self._compare_longitude_and_latitude(oriTude, comTude):
                        equalFlag = True
                        break
                # if (comTelNum == None) or (oriTelNum == None):
                    # if self._compare_longitude_and_latitude(oriTude, comTude):
                        # equalFlag = True
                        # break
                # elif (comTelNum != None) and (oriTelNum != None):
                    # if comTelNum == oriTelNum:
                        # if self._compare_longitude_and_latitude(oriTude, comTude):
                            # equalFlag = True
                            # break

            if equalFlag == False:
                store = self._setting_storeinfo_object(compareData[i], sido, sigugun)
                result.append(store)
                # print(store.__str__())
                #try save lotto645 data
                pass
        for data in originData:
            store = self._setting_storeinfo_object(data, sido, sigugun)
            result.append(store)
            # print(store.__str__())
        return result
    """
    lotto645
        {
        "BPLCLOCPLC3": "역삼동",
        "BPLCLOCPLC2": "강남구",
        "BPLCLOCPLC1": "서울",
        "FIRMNM": "투싼",
        "DEALSPEETO": "N",
        "LONGITUDE": 127.048325,
        "BPLCLOCPLC4": null,
        "RECORDNO": 53,
        "BPLCLOCPLCDTLADRES": "755 한솔필리아 1층 127호",
        "RTLRID": "11140733",
        "RTLRSTRTELNO": null,
        "DEAL645": "1",
        "BPLCDORODTLADRES": "서울 강남구 역삼로 310 한솔필리아 1층 127호",
        "DEAL520": "N",
        "LATITUDE": 37.499457
        }
    speetto
        {
            "BPLCLOCPLC3": "언주로147길",
            "BPLCLOCPLC2": "강남구",
            "BPLCLOCPLC1": "서울",
            "TELEPHONE": null,
            "BIZ_NO": "2110623717",
            "SHOP_NM": "GS25강남나누리점",
            "BIZ_TYPE": null,
            "ADDR_LOT": "127.033405",
            "BPLCLOCPLC4": "10 1층",
            "RECORDNO": 59,
            "BPLCLOCPLCDTLADRES": null,
            "USE_YN": "Y",
            "FAX_NO": null,
            "POPCORN_YN": "N",
            "DEALER_ID": null,
            "VENDOR_CODE": "71165364",
            "BIZ_ITEM": "GS",
            "ADDR_LAT": "37.519995",
            "MOB_NO": "01089216285",
            "LOTT_YN": "Y",
            "ANNUITY_YN": "Y",
            "SPEETTO500_YN": "Y",
            "SPEETTO1000_YN": "Y",
            "SPEETTO2000_YN": "Y"
        }   
    """
    def _setting_storeinfo_object(self, storeData:dict, sido, sigugun):
        """
            Args:
                storeData: dict #json으로 응답받은 상점정보
                sido     : str
                sigugun  : str
            Return:
                StoreInfo
        """
        storeInfo = StoreInfo()
        lottoType = LottoType()
        lottoHandle = LottoHandleList()
        lottoList = list()
        storeInfo.storeOpenTime = None
        storeInfo.storeCloseTime = None
        storeInfo.storesido = sido
        storeInfo.storesigugun = sigugun
        #set uuid
        storeInfo.storeUuid = str(uuid.uuid1())
        if "LONGITUDE" in storeData.keys():
            #lotto645
            storeInfo.storeName = self._remove_special_symbol(storeData["FIRMNM"])
            storeInfo.storeAddress = self._remove_special_symbol(storeData["BPLCDORODTLADRES"])
            storeInfo.storeLatitude = str(storeData["LATITUDE"])
            storeInfo.storeLongitude = str(storeData["LONGITUDE"])
            storeInfo.storeBizNo = None
            storeInfo.storeMobileNum = None
            storeInfo.storeTelNum = storeData["RTLRSTRTELNO"]
            #set LottoType  Object
            lottoList.append(self._set_lottoType("001", "로또645"))
            
            #set LottoHandleList Object
            lottoHandle.storeId = storeInfo.storeUuid
            lottoHandle.lottoList = lottoList
            
            storeInfo.lottoHandle = lottoHandle
        else:
            #speetto
            address = []
            address.append(storeData["BPLCLOCPLC1"])
            address.append(storeData["BPLCLOCPLC2"])
            address.append(storeData["BPLCLOCPLC3"])
            address.append(storeData["BPLCLOCPLC4"])
            storeInfo.storeName = self._remove_special_symbol(storeData["SHOP_NM"])
            try:
                if None in address:
                    for i in address:
                        if i is None:
                            address.remove(i)
                storeInfo.storeAddress = self._remove_special_symbol(" ".join(address))
            except Exception as e:
                print(f"ERROR storeData: {storeData}")
                raise e
            storeInfo.storeLatitude = str(storeData["ADDR_LAT"])
            storeInfo.storeLongitude = str(storeData["ADDR_LOT"])
            storeInfo.storeBizNo = storeData["BIZ_NO"]
            storeInfo.storeMobileNum = storeData["MOB_NO"]
            storeInfo.storeTelNum = storeData["TELEPHONE"]

            if storeData["LOTT_YN"] == "Y":
                lottoList.append(self._set_lottoType("001", "로또645"))
            elif storeData["ANNUITY_YN"] == "Y":
                lottoList.append(self._set_lottoType("002", "연금복권"))
            elif storeData["SPEETTO500_YN"] == "Y":
                lottoList.append(self._set_lottoType("003", "스피또500"))
            elif storeData["SPEETTO1000_YN"] == "Y":
                lottoList.append(self._set_lottoType("004", "스피또1000"))
            elif storeData["SPEETTO2000_YN"] == "Y":
                lottoList.append(self._set_lottoType("005", "스피또2000"))

            #set LottoHandleList Object
            lottoHandle.storeId = storeInfo.storeUuid
            lottoHandle.lottoList = lottoList
            
            storeInfo.lottoHandle = lottoHandle
        return storeInfo

    def _set_lottoType(self, ltype, name):
        """
            Args:
                ltype: str 복권 타입(정해져있음)
                name: str 복권명
            Return
                LottoType
        """
        lottoType = LottoType()
        lottoType.lottoId = str(uuid.uuid1())
        lottoType.lottoCode = ltype
        lottoType.lottoName = name
        return lottoType

    def _escape_query_string(self, value:str):
        if "'" in value:
            value = value.replace("'", "''")
        return value

    def save_store_data(self, storeDataes):
        key = list()
        value = list()
        for data in storeDataes:
            key = []
            value = []
            data_dict = data.__dict__
            for k, v in data_dict.items():
                if k == "lottoHandle":
                    continue
                key.append(k)
                if v == None:
                    v = "NULL"
                value.append(self._escape_query_string(v))
            columnName = ",".join(key)
            columnValues = ",".join("'{}'".format(i) for i in value)
            jdbc.execute(f"insert into store({columnName}) values({columnValues});")

                   
    def _compare_longitude_and_latitude(self, originData, compareData):
        """
            Args:
                originData : list 0:latitude, 1:longitude
                compareData: list 0:latitude, 1:longitude
            Return:
                bool
        """
        ret = True
        for i in range(len(originData)):
            ori = originData[i].split(".")
            com = compareData[i].split(".")

            if int(ori[0]) != int(com[0]):
                #not equal data 각각 처리
                ret = False
                break
            if abs(int(ori[1][:4]) - int(com[1][:4])) > 4:
                #not equal data 각각 처리 오차가 5이상 나기 시작하면 다른 가게라고 판단
                ret = False
                break
        return ret




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
                u = Utils()
                date, time = u.get_current_time()
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
        for key in address_map.keys():
            sido = key
            for sigugun in address_map[key]:
                speetto = self.parseStoreInfo(url, sido, sigugun, {"method":"sellerInfoPrintResult"})
                lotto645 = self.parseStoreInfo(url, sido, sigugun, {"method":"sellerInfo645Result"})
                storeDataes = self.compareStores(speetto, lotto645, sido, sigugun)
                self.save_store_data(storeDataes)

class WinParseException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.value

class WinInfo:
    """
        1등,2등 당첨지 파싱
    """
    lottoTypes = {
            "lotto645":"L645",
            "annual":"L720",
            "speetto500":"SP500",
            "speetto1000":"SP1000",
            "speetto2000":"SP2000"
        }
    first_win_info = []
    second_win_info = []


    def _find_max_round(self, session, url, headers, postData, param):
        """
            Args:
                session: requests.session
                url: str
                headers: dict
                postData: dict
                param: dirc
            Return:
                str
        """
        maxRound = None
        try:
            response = session.request("POST",url,headers=headers, data=postData, params=param)
            restxt = response.text
            if "drwNo" not in restxt:
                raise WinParseException("회차 파싱 오류: can't find 'drwNo'")
            
            p = re.compile("(\<option value=\"[\d]+\"\>)(.*?)(\<\/option\>)")
            m = p.findall(restxt)
            maxRound = m[0][1]

        except WinParseException as e:
            u = Utils()
            date, time = u.get_current_time()
            with open(f"./log/error_log.log","a") as f:
                f.write(f"[{time}] schVal: {postData['schVal']}\n")
                f.write(f"[{time}] nowPage: {postData['nowPage']}\n")
            with open(f"./errorDump/{param['pageGubun']}_{date}.html","w") as f:
                f.write(f"{restxt}")
        return maxRound

    def _get_first_win_info(self, first_list):
        if "조회결과가없습니다" in first_list[9]:
            return None
        store = {}
        keys = [first_list[4], first_list[5],first_list[6], first_list[7],first_list[8]]
        i = 8
        while True:
            if len(first_list) <= i:
                break
            for k in keys:
                i += 1
                store[k] = first_list[i]
            self.first_win_info.append(store)
    def _get_second_win_info(self, second_list):
        if "조회결과가없습니다" in second_list[9]:
            return None
        store = {}
        keys = [second_list[4], second_list[5],second_list[6], second_list[7],second_list[8]]
        i = 8
        while True:
            if len(second_list) <= i:
                break
            for k in keys:
                i += 1
                store[k] = second_list[i]
            self.second_win_info.append(store)
    #method=topStore&pageGubun=L645
    def _parseAllWinInfoByArea(self, url, sido, sigugun, queryString):
        """
            Args:
                url : str
                sido : str
                sigugun: str
                queryString: dict
                maxRound: dict
            Return
                firstList: list
                secondList: List
        """
        firstList = []
        secondList = []

        maxRound = None
        headers = {
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding" : "gzip, deflate, br",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        param = {}
        if queryString is not None:
            for key, value in queryString.items():
                param[key] = value
        
        postData = {
            "method": "topStore",
            "nowPage": "1",
            "rangNo": "",
            "gameNo": "5133",
            "drwNo":"",
            "schKey": "area",
            "schVal": str(sido.encode('euc-kr'),'euc-kr')+" "+str(sigugun.encode('euc-kr'),'euc-kr')
        }
        
        session = requests.Session()
        session.verify = "FidderRootCertificate.crt"
        if maxRound is None:
            maxRound = self._find_max_round(session, url, headers, postData, param)
        try:
            for no in range(1, int(maxRound)+1):
                postData["drwNo"] = str(no)
                duplicateFirst = None
                duplicateSecond = None
                breakCount = 0
                for i in range(30):
                    response = session.request("POST",url,headers=headers, data=postData, params=param)
                    restxt = response.text
                    #<td class="nodata" colspan="5">조회 결과가 없습니다.</td>
                    p = re.compile("(\<td class=\"nodata\" colspan=\"[\d]+\"\>)(.*?)(\<\/td\>)")
                    m = p.findall(restxt)
                    if m.__len__() == 2:
                        break
                    with open(f"./test/{sido}_{sigugun}_{postData['nowPage']}_{postData['gameNo']}.html","w") as f:
                        f.write(restxt)
                    htmlParser = WinHTMLParser()
                    htmlParser.feed(restxt)
                    
                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    print(htmlParser.first_result[9])
                    if "조회결과가없습니다" in htmlParser.first_result[9]:
                        print("first NO")
                        breakCount += 1
                    else:
                        if duplicateFirst:
                            if duplicateFirst == htmlParser.first_result[10]:
                                breakCount += 1
                        else:
                            duplicateFirst = htmlParser.first_result[10]
                    print(htmlParser.second_result[9])
                    if "조회결과가없습니다" in htmlParser.second_result[9]:
                        print("second NO")
                        breakCount += 1
                    else:
                        if duplicateSecond:
                            if duplicateSecond == htmlParser.second_result[10]:
                                breakCount += 1
                        else:
                            duplicateSecond = htmlParser.second_result[10]
                    
                    if breakCount == 2:
                        break
                    breakCount = 0

                    self._get_first_win_info(htmlParser.first_result)
                    self._get_second_win_info(htmlParser.second_result)

                    postData["nowPage"] = str(int(postData["nowPage"]) + 1)

        except Exception as e:
            raise e
    def getWinInfo(self):
        queryString = {}
        queryString["method"] = "topStore"
        for key, value in self.lottoTypes.items():
            queryString["pageGubun"] = value
            for sido in address_map.keys():
                for sigugun in address_map[sido]:
                    print(f"lottoType: {value}, sido: {sido}, sigugun: {sigugun}")
                    self._parseAllWinInfoByArea("https://dhlottery.co.kr/store.do" ,sido, sigugun, queryString)

        
        print(self.first_win_info)
        print(self.second_win_info)