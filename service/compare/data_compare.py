import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import uuid
import html
from save import jdbc
from dto import hangmaniDTO
class StoreInfoCompare:

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
                if self._compare_longitude_and_latitude(oriTude, comTude):
                        equalFlag = True
                        break
                if self._compare_tel_num(oriTelNum, comTelNum):
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
        for data in originData:
            store = self._setting_storeinfo_object(data, sido, sigugun)
            result.append(store)
        return result


class WinHistoryInfoCompare:
    def compareWinHistory(self, win_history_info:dict):
        """
            Args:
                lotto_type: str
                win_history_info: dict
                {'lotto64' : {'sido sigugun' : [{'번호':'1','상호명':'','구분':'','소재지':'','위치보기':'','round':''}]}}
            Returns:
                None
        """
        selectFlag = True
        for lottoType, value in win_history_info.items():
            lottoid = jdbc.execute(f"select lottoid from lotto_type where lottoname='{lottoType}'", selectFlag)[0]["lottoid"]
            print(f"type: {type(lottoid)}, velue: {lottoid}")
            for sido_sigugun, v in value.items():
                address = sido_sigugun.split(" ")
                for data in v:
                    queryResult = jdbc.execute(
                    f"select storeuuid, storename, storeaddress from store where storesido='{address[0]}' and storesigugun='{address[1]}' and storename='{data['상호명']}';",
                    selectFlag)
                    print(queryResult)
            # for i in value:
                