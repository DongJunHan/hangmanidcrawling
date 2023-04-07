from dataclasses import dataclass, field
from typing import ClassVar
from typing import List

@dataclass(unsafe_hash=True)
class LottoType:
    lottoId        : int                                       #복권 PK
    lottoName      : str                                       #복권 이름
    def __init__(self):
        pass

@dataclass(unsafe_hash=True)
class LottoTypeHandle:
    storeUuid        : str                                       #상점 ID PK값
    lottoId          : int                                       #로또 타입 ID
    def __init__(self):
        pass

@dataclass(unsafe_hash=True)
class WinHistory:
    storeUuid        : str                                       #상점 ID PK값
    winRound       : int                                         #당첨 회차
    winRank        : int                                         #당첨 등수
    lottoId        : int                                         #로또 리스트 DTO
    def __init__(self, storeUuid = None, winRound = None, winRank = None, lottoId = None):
        self.storeUuid = storeUuid
        self.winRank = winRank
        self.winRound = winRound
        self.lottoId = lottoId
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
    lottoHandleList: List[LottoTypeHandle] = None              #취급 복권 리스트
    # winHistory     : WinHistory                                #당첨 내역
    def __init__(self):
        pass
    def __init__(self, storeUuid = None, storeName = None, storeAddress = None, storeLatitude = None,
                    storeLongitude = None, storeBizNo = None, storeTelNum = None,
                    storeMobileNum = None, storeOpenTime = None, storeCloseTime = None, 
                    lottoHandleList = None):
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
        self.lottoHandleList = lottoHandleList