"""
1. 시/도 로 군들을 검색 (https://dhlottery.co.kr/store.do?method=searchGUGUN)
2. 군들을 통해서 주소 검색 (https://dhlottery.co.kr/store.do?method=sellerInfo645Result)
or
1. 시/도, 도/군들을 가지고 있다가 바로 2번을 수행
"""
from dataclasses import dataclass, field
from typing import List
@dataclass(unsafe_hash=True)
class StoreInfo:
    storeId        : int                                       #상점 ID PK값
    storeName      : str                                       #상점 이름
    storeAddress   : str                                       #상점 주소
    storeLatitude  : float                                     #상점 위도
    storeLongitude : float                                     #상점 경도
    storeTel       : str                                       #상점 전화번호
    storeMobil     : str                                       #상점 핸드폰번호
    operatingHours : str                                       #영업 시간
    storeCloseFlag : bool = False                              #폐점 여부
    lotteHandleFlag: List[bool] = field(default_factory=list)  #취급로또 여부 리스트
    rankPriorty    : StoreRank

@dataclass(unsafe_hash=True)
class StoreRank:
    rankOne        : int                                       #1등 당첨 횟수
    rankTwo        : int                                       #2등 당첨 횟수
    
    # lotto645Flag: bool = False    #로또645 취급여부
    # annuityFlag: bool = False     #연금복권 취급여부
    # speetto500Flag: bool = False  #스피또500 취급여부
    # speetto1000Flag: bool = False #스피또1000 취급여부
    # speetto2000Flag: bool = False #스피또2000 취급여부
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
    url = "https://dhlottery.co.kr/store.do"
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept" : "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding" : "gzip, deflate, br",
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"

    }
    data = {
        "searchType":"1",
        "nowPage": "1",
        "rtlrSttus": "001"
    }
    param = {"method":"sellerInfo645Result"}
    session = requests.Session()
    session.verify = "FidderRootCertificate.crt"
    for key in address_map.keys():
        data["sltSIDO"] = key
        #new page 갱신해가면서 정보 수집
        for gugun in address_map[key]:
            data["sltGUGUN"] = gugun
            """
                self,
                method,
                url,
                params=None,
                data=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None,
            """
            response = session.request("POST",url,headers=headers, data=data, params=param)
            print(response.json())
            print(response.cookies.items())
        
