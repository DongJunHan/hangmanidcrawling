"""
1. 시/도 로 군들을 검색 (https://dhlottery.co.kr/store.do?method=searchGUGUN)
2. 군들을 통해서 주소 검색 (https://dhlottery.co.kr/store.do?method=sellerInfo645Result)
or
1. 시/도, 도/군들을 가지고 있다가 바로 2번을 수행
"""
from dataclasses import dataclass, field
from typing import List
import json
@dataclass(unsafe_hash=True)
class StoreInfo:
    storeId        : str                                       #상점 ID PK값
    storeName      : str                                       #상점 이름
    storeAddress   : str                                       #상점 주소
    storeLatitude  : float                                     #상점 위도
    storeLongitude : float                                     #상점 경도
    businessNumber : str                                       #사업자 번호
    storeTel       : str                                       #상점 전화번호
    storeMobil     : str                                       #상점 핸드폰번호
    openHours      : str                                       #영업 시작 시간
    closeHours     : str                                       #영업 폐점 시간
    storeCloseFlag : bool = False                              #폐점 여부
    lottoHandleList: LottoHandleList                           #취급 복권 리스트
    winHistory     : WinHistory                                #당첨 내역

@dataclass(unsafe_hash=True)
class LottoHandleList:
    storeId        : str                                       #상점 ID PK값
    lottoList      : lottoList                                 #로또 리스트 DTO

@dataclass(unsafe_hash=True)
class LottoList:
    lottoId        : int                                       #복권 PK
    lottoCode      : str                                       #복권 종류 코드
    lottoName      : str                                       #복권 이름

@dataclass(unsafe_hash=True)
class WinHistory:
    storeId        : str                                       #상점 ID PK값
    winRound       : int                                       #당첨 회차
    winRank        : int                                       #당첨 등수
    lottoList      : LottoList                                 #로또 리스트 DTO

address_map = {
    "서울" : ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구","노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구",
            "성동구","성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"],
    "경기" : ["가평군","고양시 덕양구","고양시 일산동구","고양시 일산서구","과천시","광명시","광주시","구리시","군포시","김포시","남양주시","동두천시",
            "부천시","성남시 분당구","성남시 수정구","성남시 중원구","수원시 권선구","수원시 영통구","수원시 장안구","수원시 팔달구","시흥시","안산시 단원구",
            "안산시 상록구","안성시","안양시 동안구","안양시 만안구","양주시","양평군","여주시","연천군","오산시","용인시 기흥구","용인시 수지구","용인시 처인구",
            "의왕시","의정부시","이천시","파주시","평택시","포천시","하남시","화성시"],
    "부산" : ["강서구","금정구","기장군","남구","동구","동래구","부산진구","북구","사상구","사하구","서구","수영구","연제구","영도구","중구","해운대구"],
    "대구" : ["남구","달서구","달성군","대덕구","동구","북구","서구","수성구","유성구","중구"],
    "인천" : ["강화군","계양구","남동구","동구","미추홀구","부평구","서구","연수구","옹진군","중구"],
    "대전" : ["대덕구","동구","서구","유성구","중구"],
    "울산" : ["남구","동구","북구","울주군","중구"],
    "강원" : ["강릉시","고성군","동해시","삼척시","속초시","양구군","양양군","영월군","원주시","인제군","정선군","철원군","춘천시","태백시","평창군",
            "홍천군","화천군","횡성군"],
    "충북" : ["괴산군","단양군","보은군","영동군","옥천군","음성군","제천시","증평군","진천군","청주시 상당구","청주시 서원구","청주시 청원구",
            "청주시 흥덕구","충주시"],
    "충남" : ["계룡시","공주시","금산군","논산시","당진시","보령시","부여군","서산시","서천군","아산시","예산군","천안시 동남구","천안시 서북구",
            "청양군","태안군","홍성군"],
    "광주" : ["광산구","남구","동구","북구","서구"],
    "전북" : ["고창군","군산시","김제시","남원시","무주군","부안군","순창군","완주군","익산시","임실군","장수군","전주시 덕진구","전주시 완산구",
            "정읍시","진안군"],
    "전남" : ["강진군","고흥군","곡성군","광양시","구례군","나주시","담양군","목포시","무안군","보성군","순천시","신안군","여수시","영광군","영암군",
            "완도군","장성군","장흥군","진도군","함평군","해남군","화순군"],
    "경북" : ["경산시","경주시","고령군","구미시","군위군","김천시","문경시","봉화군","상주시","성주군","안동시","영덕군","영양군","영주시","영천시",
            "예천군","울릉군","울진군","의성군","청도군","청송군","칠곡군","포항시 남구","포항시 북구"],
    "경남" : ["거제시","거창군","고성군","김해시","남해군","밀양시","사천시","산청군","양산시","의령군","진주시","창녕군","창원시 마산합포구","창원시 마산회원구",
            "창원시 성산구","창원시 의창구","창원시 진해구","통영시","하동군","함안군","함양군","합천군"],
    "제주" : ["서귀포시","제주시"],
    "세종" : []
}
import requests
import json
class ParseStore:

    def compareStores(self, originData, compareData):
        """
            Args:
                originData : dict
                compareData : dict
            Return:
                dict
        """
        for i in range(len(compareData)):
            comTelNum = compareData[i]["RTLRSTRTELNO"] #tel number
            comTude = [str(compareData[i]["LATITUDE"]), str(compareData[i]["LONGITUDE"])] #latitude, longitude
            equalFlag = False
            for j in range(len(originData)):
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

            """
                TODO. 
                equalFlag값이 False이면 두 데이터들 중에 같은게 없다는 뜻이므로 각각 따로 저장하나
                    True이면 같은 상점 정보이기 때문에 정보량이 더 많은 speetto데이터만 저장한다.
            """
            if equalFlag == False:
                #try save lotto645 data
                pass

            #try save speetto data

            
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




    def parseStoreInfo(self, url, gugun, sido, queryString:dict=None):
        """
            Args:
                url : str
                gugun : str 주소 구/군
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
            "sltGUGUN": gugun,
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
                if "SHOP_NM" in jsonData["arr"][0].keys():
                    validateInfo = jsonData["arr"][0]["SHOP_NM"]
                else:
                    validateInfo = jsonData["arr"][0]["FIRMNM"]
            
            postData["nowPage"] = str(int(postData["nowPage"]) + 1)
            for i in jsonData["arr"]:
                result.append(i)

        return result
        
    def getStoreData(self):
        url = "https://dhlottery.co.kr/store.do"
        for key in address_map.keys():
            sido = key
            for gugun in address_map[key]:
                speetto = self.parseStoreInfo(url, gugun, sido, {"method":"sellerInfoPrintResult"})
                lotto645 = self.parseStoreInfo(url, gugun, sido, {"method":"sellerInfo645Result"})
                result = self.compareStores(speetto, lotto645)

    def test(self):
        with open("./test/sellerInfo645Result_강남구_Result_.json","r") as file:
            lotto645 = json.load(file)
        with open("./test/sellerInfoPrintResult_강남구_Result_.json","r") as file:
            speetto = json.load(file)
        
        self.compareStores(speetto, lotto645)
        
