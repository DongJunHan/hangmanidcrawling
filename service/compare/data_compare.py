import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import uuid
import html
import re
from save import jdbc_config
from dto import hangmaniDTO
class StoreInfoCompare:

    def compare_longitude_and_latitude(self, originData, compareData):
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

    def _set_lottoType(self, ltype, name):
        """
            Args:
                ltype: str 복권 타입(정해져있음)
                name: str 복권명
            Return
                LottoType
        """
        lottoType = hangmaniDTO.LottoType()
        lottoType.lottoId = str(uuid.uuid1())
        lottoType.lottoCode = ltype
        lottoType.lottoName = name
        return lottoType
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
        storeInfo = hangmaniDTO.StoreInfo()
        lottoType = hangmaniDTO.LottoType()
        lottoHandle = hangmaniDTO.LottoHandleList()
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
            lottoHandle.storeUuid = storeInfo.storeUuid
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
            lottoHandle.storeUuid = storeInfo.storeUuid
            lottoHandle.lottoList = lottoList
            
            storeInfo.lottoHandle = lottoHandle
        return storeInfo
    
    def _compare_tel_num(self, originTelNum, compareTelNum):
        if originTelNum == None or compareTelNum == None:
            return False
        if originTelNum == compareTelNum:
            return True
        return False

    def compareStores(self, originData, compareData, sido, sigugun):
        """
            로또645판매점과 연금복권/즉석복권 판매점이 겹치는 경우가 있기 때문에 두 곳에서 가져온 정보를
            비교(위도/경도, 전화번호)하여 같은 상점이라고 판단되면 연금복권/즉석복권의 데이터가 더 많기 때문에 연금복권/즉석복권
            데이터를 넣는다.
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
                oriTelNum = originData[j]["TELEPHONE"]
                oriTude = [originData[j]["ADDR_LAT"], originData[j]["ADDR_LOT"]] #latitude, longitude
                oriTelNum = originData[j]["TELEPHONE"]
                if self.compare_longitude_and_latitude(oriTude, comTude):
                        equalFlag = True
                        break
                if self._compare_tel_num(oriTelNum, comTelNum):
                    equalFlag = True
                    break
                # if (comTelNum == None) or (oriTelNum == None):
                    # if self.compare_longitude_and_latitude(oriTude, comTude):
                        # equalFlag = True
                        # break
                # elif (comTelNum != None) and (oriTelNum != None):
                    # if comTelNum == oriTelNum:
                        # if self.compare_longitude_and_latitude(oriTude, comTude):
                            # equalFlag = True
                            # break

            if equalFlag == False:
                store = self._setting_storeinfo_object(compareData[i], sido, sigugun)
                result.append(store)
        for data in originData:
            store = self._setting_storeinfo_object(data, sido, sigugun)
            result.append(store)
        return result

class DataException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.values

class WinHistoryInfoCompare:
    def __init__(self):
        self.winHistory = hangmaniDTO.WinHistory()
        self.jdbcConfig = jdbc_config.JDBCConfig()
    def compareWinHistoryToStoreInfo(self, rank, win_history_info:dict):
        """
            Args:
                rank            : int 1등/2등
                win_history_info: dict
                {'lotto64' : {'sido sigugun' : [{'번호':'1','상호명':'','구분':'','소재지':'','위치보기':'','round':''}]}}
            Returns:
                list[hangmaniDTO.WinHistory]
                list[str] unknown Store
        """
        result = []
        unknownStoreList = []
        selectFlag = True
        for lottoType, value in win_history_info.items():
            lottoid = self.jdbcConfig.select_query(f"select lottoid from lotto_type where lottoname='{lottoType}'", 
                            selectFlag)[0]["lottoid"]
            # print(f"type: {type(lottoid)}, velue: {lottoid}")
            for sidoSigugun, v in value.items():
                sigunArr = sidoSigugun.split(" ")
                # print(f"len: {len(v)}")
                for i in range(len(v)):
                    """
                        1. 지번일 때 - 왠만하면 폐점인 것으로 보임
                        2. 도로명일 때 - 상호명은 굉장히 부정확할 확률이 많으므로 주소 'xx로'
                                        까지만 잘라서 쿼리에 날려본다
                    """
                    queryAddress = ""
                    """
                        like문으로 쿼리를 날릴 것이기 때문에 전체주소로 검색하지 않는다.
                        1. 먼저 지번을 걸러낸다.
                        2. 그리고 도로명주소는 xx로 뒤에 숫자까지만 파싱
                    """
                    addressSplit = v[i]["소재지"].split(" ")
                    if ("동" in addressSplit[2])\
                        and ("로" not in addressSplit[2]):
                        p = re.compile(f"({sigunArr[0]}\s{sigunArr[1]}\s)(.*?)(?=동)")
                        matchTuple = p.findall(v[i]["소재지"])
                        if len(matchTuple) > 0:
                            for j in range(len(matchTuple[0])):
                                queryAddress +=  matchTuple[0][j]
                        else:
                            queryAddress = v[i]["소재지"]
                    else:
                        # (서울\s노원구\s.*?)([\d])(?=[\D].?)
                        p = re.compile(f"({sigunArr[0]}\s{sigunArr[1]}\s.*?)([\d])(?=[\D].?)")
                        matchTuple = p.findall(v[i]["소재지"])
                        if len(matchTuple) > 0:
                            for j in range(len(matchTuple[0])):
                                queryAddress +=  matchTuple[0][j]
                        else:
                            queryAddress = v[i]["소재지"]
                    storeName = v[i]['상호명']

                    """
                        store 테이블의 상점명과 당첨내역 파싱한 상점명의 로또/복권 이라는 단어가
                        앞/뒤로 바뀌어있는 경우가 있어서 로또/복권은 빼고 like문으로 쿼리 날려보기 위함.
                    """
                    if "복권" in storeName:
                        p = re.compile("(.*)(복권)(.*)")
                        matchTuple = p.findall(storeName)
                        if len(matchTuple[0][0]) > len(matchTuple[0][2]):
                            storeName = matchTuple[0][0]
                        else:
                            storeName = matchTuple[0][2]
                    elif "로또" in storeName:
                        p = re.compile("(.*)(로또)(.*)")
                        matchTuple = p.findall(storeName)
                        if len(matchTuple[0][0]) > len(matchTuple[0][2]):
                            storeName = matchTuple[0][0]
                        else:
                            storeName = matchTuple[0][2]
                    
                    
                    if lottoType == "lotto645":
                        """
                            1. 위에서 수정한 주소로 쿼리를 날린다.
                            2. 위에서 수정한 상점명으로 쿼리를 날린다.
                            3. 경도/위도를 소수점 세번째자리까지 상세하게 검색한다.
                        """
                        latiLong = v[i]['위도경도'].split(",")
                        # and storename like ('%{storeName}%')\
                        query = f"select storeuuid, storename from store where \
                                storeaddress like ('{queryAddress}%') \
                                and storesido='{sigunArr[0]}'\
                                and storesigugun='{sigunArr[1]}'\
                                and storelatitude like ('{latiLong[0][:5]}%')\
                                and storelongitude like ('{latiLong[1][:5]}%');"
                                
                        queryResult = self.jdbcConfig.select_query(query, selectFlag)
                        
                        if len(queryResult) == 0 or len(queryResult) > 1:
                            query = f"select storeuuid, storename from store where \
                                storename like ('%{storeName}%')\
                                and storesido='{sigunArr[0]}'\
                                and storesigugun='{sigunArr[1]}'\
                                and storelatitude like ('{latiLong[0][:5]}%')\
                                and storelongitude like ('{latiLong[1][:6]}%');"
                            queryResult = self.jdbcConfig.select_query(query, selectFlag)
                            if len(queryResult) == 0 or len(queryResult) > 1 :
                                query = f"select storeuuid, storename from store where \
                                    storesigugun='{sigunArr[1]}'\
                                    and storelatitude like ('{latiLong[0][:6]}%')\
                                    and storelongitude like ('{latiLong[1][:7]}%');"
                                queryResult = self.jdbcConfig.select_query(query, selectFlag)
                    else:
                        query = f"select storeuuid, storename from store where storesido='{sigunArr[0]}' \
                                and storesigugun='{sigunArr[1]}' \
                                and storeaddress like ('{queryAddress}%');"
                        queryResult = self.jdbcConfig.select_query(query, selectFlag)

                    #select 결과가 2개 이상 나올 때 예외처리
                    if queryResult.__len__() > 1:
                        print(f"{queryResult}\n {v[i]}, winRank : {rank}, {query}")
                        for p in range(len(queryResult)):
                            print(queryResult[p]['storename'])
                            print(v[i]['상호명'])
                            if queryResult[p]["storename"].find(v[i]['상호명']) > -1:
                                queryResult = [queryResult[p]]
                        if len(queryResult) > 1:
                            raise DataException("같은 상호명이 두 곳 이상입니다.")
                    if len(queryResult) == 0:
                        #마지막으로 원본 주소로 쿼리를 날려본다.
                        query = f"select storeuuid, storename from store where \
                                storeaddress='{v[i]['소재지']}'\
                                and storesido='{sigunArr[0]}'\
                                and storesigugun='{sigunArr[1]}';"
                        queryResult = self.jdbcConfig.select_query(query, selectFlag)
                        if len(queryResult) == 0:
                            unknownStoreList.append(v[i])
                            print(f"no match store data: {v[i]}, query: {query}\n")
                            continue
                    winHistory = hangmaniDTO.WinHistory(queryResult[0]["storeuuid"], int(v[i]["winRound"]), rank, lottoid)
                    storeuuid = None
                    result.append(winHistory)
        return result, unknownStoreList