import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import re
import requests
import json
import abc
from datetime import datetime
from dto import util, hangmaniDTO

"""
    TODO. 
    1. 운영시 매주 한 번 프로그램을 돌려서 상점이 새로 추가됐는지, 기존의 상점이 없어졌는지 확인이 필요.
"""
class WinParseException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.value

class WinHistoryByArea(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parseWinHistory(self, session, url, sido, headers, queryParam:dict):
        """
            Args:
                session   : requests.Session
                url       : str
                sido      : str
                headers   : dict
                queryParam: dict
            Return
                firstList: list
                secondList: List
        """
        raise NotImplemented

class WinHistoryCurrentRoundByArea(WinHistoryByArea):
    def __init__(self):
        self.winUtil = WinInfoUtil()
        # self.first_win_info = {}
        # self.second_win_info = {}

    def _insertSigugun(self, sido, data_list, total_data):
        """
            Args:
                sido      : str
                data_list : list
                total_data: dict
            Return
                total_data: dict
        """
        for data in data_list:
            data["소재지"] = data["소재지"].replace("  "," ")
            addressArr = data["소재지"].split()
            if "동행복권" in addressArr[0]:
                continue
            if "북도" in addressArr[0] or "남도" in addressArr[0]:
                addressArr[0] = addressArr[0][0]+addressArr[0][2]
            elif "특별시" in addressArr[0]:
                addressArr[0] = addressArr[0].replace("특별시", "")
            
            if "광역시" in addressArr[0]:
                addressArr[0] = addressArr[0].replace("광역시","")
            elif addressArr[0] == "제주도":
                addressArr[0] = "제주"

            sigugunKey = addressArr[0] + " " + addressArr[1]
            if sigugunKey not in total_data.keys():
                total_data[sigugunKey] = []
            
            address = ""
            for i in range(len(addressArr)):
                address = address + " " + addressArr[i]
            data["소재지"] = address
            total_data[sigugunKey].append(data.copy())
        return total_data

    def parseWinHistory(self, session, url, sido, headers, queryParam):
        """
            Args:
                session   : requests.Session
                url       : str
                sido      : str
                headers   : dict
                queryParam: dict
            Return
                firstList: list
                secondList: List
        """
        firstSido = {}
        secondSido = {}
        postData = self.winUtil.get_win_history_postdata(sido, "")
        maxRound = self.winUtil.find_max_round(session, url, headers, postData, queryParam)
        sidoOther = self.winUtil.checkSidoArea(sido, queryParam["pageGubun"])
        firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, int(maxRound), maxRound, postData, headers, queryParam)
        
        firstSido = self._insertSigugun(sido, firstHistory, firstSido)
        secondSido = self._insertSigugun(sido, secondHistory, secondSido)
        if sidoOther != None:
            firstHistory.clear()
            secondHistory.clear()
            postData = self.winUtil.get_win_history_postdata(sidoOther, "")
            firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, int(maxRound), maxRound, postData, headers, queryParam)
            firstSido = self._insertSigugun(sidoOther, firstHistory, firstSido)
            secondSido = self._insertSigugun(sidoOther, secondHistory, secondSido)
        return firstSido, secondSido
class WinHistoryAllByArea(WinHistoryByArea):
    def __init__(self):
        self.winUtil = WinInfoUtil()
        self.urban = util.Variable().address_map
        # self.first_win_info = {}
        # self.second_win_info = {}
    
    def _insertcheckMetropolitanCityOther(self, sido, sigugun, data_list, total_data):
        for data in data_list:
            addressArr = data["소재지"].split()
            address = sido
            for i in range(1, len(addressArr)):
                address = address + " " + addressArr[i]
            data["소재지"] = address
            total_data[sido + " " + sigugun].append(data.copy())
        return total_data
    
    def _insertSidoOther(self, sido, data_list, total_data):
        for data in data_list:
            data["소재지"] = data["소재지"].replace("  "," ")
            addressArr = data["소재지"].split()
            if "동행복권" in addressArr[0]:
                continue
            if "북도" in addressArr[0] or "남도" in addressArr[0]:
                addressArr[0] = addressArr[0][0]+addressArr[0][2]
            elif "특별시" in addressArr[0]:
                addressArr[0] = addressArr[0].replace("특별시", "")
            
            if "광역시" in addressArr[0]:
                addressArr[0] = addressArr[0].replace("광역시","")
            elif addressArr[0] == "제주도":
                addressArr[0] = "제주"

            sigugunKey = addressArr[0] + " " + addressArr[1]
            if sigugunKey not in total_data.keys():
                total_data[sigugunKey] = []
            
            address = ""
            for i in range(len(addressArr)):
                address = address + " " + addressArr[i]
            data["소재지"] = address
            total_data[sigugunKey].append(data.copy())
        return total_data

    #method=topStore&pageGubun=L645
    def parseWinHistory(self, session, url, sido, headers, queryParam):
        """
            Args:
                session   : requests.Session
                url       : str
                sido      : str
                headers   : dict
                queryParam: dict
            Return
                firstList: list
                secondList: List
        """
        firstSido = {}
        secondSido = {}
        firstHistory = []
        secondHistory = []
        lottoType = self.winUtil.reverseLottoType.get(queryParam["pageGubun"])
        postData = self.winUtil.get_win_history_postdata(sido, "")
        maxRound = self.winUtil.find_max_round(session, url, headers, postData, queryParam)
        areaOther = self.winUtil.checkSidoArea(sido, queryParam["pageGubun"])
        
        for sigugun in self.urban[sido]:
            sidoOther = self.winUtil.checkMetropolitanCity(sido, queryParam["pageGubun"])
            postData = self.winUtil.get_win_history_postdata(sido, sigugun)
            if areaOther != None:
                postDataOther = self.winUtil.get_win_history_postdata(areaOther, sigugun)
                firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)
                firstSido = self._insertSidoOther(sido, firstHistory, firstSido)
                secondSido = self._insertSidoOther(sido, secondHistory, secondSido)
                # firstSido[areaOther+" "+ sigugun] = firstHistory
                # secondSido[areaOther+" "+ sigugun] = secondHistory
                firstHistory.clear()
                secondHistory.clear()

            firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)
            firstSido[sido+" "+ sigugun] = firstHistory
            secondSido[sido+" "+ sigugun] = secondHistory
            if sidoOther is None:
                continue
            firstHistory.clear()
            secondHistory.clear()
            
            postData = self.winUtil.get_win_history_postdata(sidoOther, sigugun)
            firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)

            firstSido = self._insertcheckMetropolitanCityOther(sido, sigugun, firstHistory, firstSido)
            secondSido = self._insertcheckMetropolitanCityOther(sido, sigugun, secondHistory, secondSido)
        
        return firstSido, secondSido
class WinInfoUtil:
    def __init__(self):
        """
            1등,2등 당첨지 파싱
        """
        self.lottoTypes = {
                "lotto645":"L645",
                "annual":"L720",
                "speetto500":"SP500",
                "speetto1000":"SP1000",
                "speetto2000":"SP2000"
            }
        self.reverseLottoType = {
                "L645":"lotto645",
                "L720":"annual",
                "SP500":"speetto500",
                "SP1000":"speetto1000",
                "SP2000":"speetto2000"
        }
        self.address_map = util.Variable().address_map
        self.util = util.Utils()
        self.get_latitude_longitude = self.util.retry_wrapper(self.get_latitude_longitude)

    def parseWinHistoryLogic(self, session, url, initialRound, maxRound, postData,headers, queryParam):
        try:
            # postData = self.winUtil.get_win_history_postdata(sido, sigugun)
            firstHistory = []
            secondHistory = []
            duplicateFirst = None
            for no in range(initialRound, int(maxRound)+1):
                postData["drwNo"] = str(no)
                duplicateSecond = None
                postData['nowPage'] = "1"
                for i in range(30):
                    breakCount = 0
                    response = session.request("POST",url,headers=headers, data=postData, params=queryParam)
                    restxt = response.text
                    #<td class="nodata" colspan="5">조회 결과가 없습니다.</td>
                    p = re.compile("(\<td class=\"nodata\" colspan=\"[\d]+\"\>)(.*?)(\<\/td\>)")
                    m = p.findall(restxt)
                    if m.__len__() == 2:
                        break
                    #TODO 2등배출점이 많아서 2페이지 이상이 될 때, 1등 배출점이 중복되어 응답에 달려오는 현상 발견.
                    #중복되는거 같으면  해당 회차를 전체로 조회를 한번 더 하는 방향으로 가야할듯
                    winHistoryValue = self.parse_win_history_data(restxt)
                    with open("./log.log","a") as f:
                        current = datetime.now()
                        f.write(f"[{current.strftime('%H:%M:%S')}]")
                        f.write(winHistoryValue.__str__())
                        f.write("\n")
                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    if len(winHistoryValue["1st"][0]) == 0:
                        breakCount += 1
                    else:
                        firstCompare = winHistoryValue["1st"][0]["상호명"]
                        if duplicateFirst:
                            if duplicateFirst == firstCompare:
                                breakCount += 1
                            else:
                                duplicateFirst = firstCompare
                        else:
                            duplicateFirst = firstCompare
                    if len(winHistoryValue["2st"][0]) == 0:
                        breakCount += 1
                    else:
                        secondCompare = winHistoryValue["2st"][0]["상호명"]
                        if duplicateSecond:
                            if duplicateSecond == secondCompare:
                                breakCount += 1
                            else:
                                duplicateSecond = secondCompare
                        else:
                            duplicateSecond = secondCompare
                    if breakCount == 2:
                        break
                    firstHistory = self.get_win_info(winHistoryValue["1st"], queryParam["pageGubun"], postData["drwNo"], firstHistory)
                    secondHistory = self.get_win_info(winHistoryValue["2st"], queryParam["pageGubun"], postData["drwNo"], secondHistory)
                    postData["nowPage"] = str(int(postData["nowPage"]) + 1)
            # self.first_win_info[sido+" "+ sigugun] = firstHistory
            # self.second_win_info[sido+" "+ sigugun] = secondHistory
        except Exception as e:
            raise e 
        return firstHistory, secondHistory
    
    def checkSidoArea(self, sido, lotto_type):
        koreaArea = {"경북":"경상","경남":"경상","전북":"전라","전남":"전라","충북":"충청","충남":"충청"}
        specialArea = ["서울", "세종"]
        if self.reverseLottoType.get(lotto_type) == "lotto645":
            return None
        
        if sido in specialArea:
            return sido+"특별시"

        for k, v in koreaArea.items():
            if sido != k:
                continue
            if "북" in sido:
                return v+"북도"
            else:
                return v+"남도"
        return None
        

    def checkMetropolitanCity(self, sido, lotto_type):
        metropolitanCity = ["인천","울산","광주","부산","제주","대전","대구"]
        sidoOther = None
        if (self.reverseLottoType.get(lotto_type) != "lotto645") and (sido in metropolitanCity):
            if sido == "제주":
                sidoOther = "제주도"
            else:
                sidoOther = sido + "광역시"
        return sidoOther

    def find_max_round(self, session, url, headers, postData, param):
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
            
            p = re.compile("(\<option value=\"[\d]+\" selected\>)(.*?)(\<\/option\>)")
            m = p.findall(restxt)
            maxRound = m[0][1]

        except WinParseException as e:
            date, time = self.util.get_current_time()
            with open(f"./log/error_log.log","a") as f:
                f.write(f"[{time}] schVal: {postData['schVal']}\n")
                f.write(f"[{time}] nowPage: {postData['nowPage']}\n")
            with open(f"./errorDump/{param['pageGubun']}_{date}.html","w") as f:
                f.write(f"{restxt}")
        return maxRound

    def get_latitude_longitude(self, historyValue):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Referer": "https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645"
        }
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        latp = re.compile("(?<=\<input type=\"hidden\" name=\"lat\" value = \")(.*?)(?=\">)")
        lonp = re.compile("(?<=\<input type=\"hidden\" name=\"lon\" value = \")(.*?)(?=\">)")
        for i in range(len(historyValue)):
            queryParam = f"method=topStoreLocation&gbn=lotto&rtlrId={historyValue[i]['위치보기']}"
            url = f"https://dhlottery.co.kr/store.do?{queryParam}"
            response = session.request("GET", url, headers=headers)
            restxt = response.text

            if latp.search(restxt) == None:
                raise WinParseException(f"위치보기 위도 파싱 실패=> {historyValue[i]}")
            
            if lonp.search(restxt) == None:
                raise WinParseException(f"위치보기 경도 파싱 실패=> {historyValue[i]}")
            
            if len(latp.findall(restxt)[0]) == 0:
                raise WinParseException(f"위치보기 위도 결과 값 없음=> {historyValue[i]}")
            if len(lonp.findall(restxt)[0]) == 0:
                raise WinParseException(f"위치보기 경도 결과 값 없음=> {historyValue[i]}")
            historyValue[i]['위치보기'] = latp.findall(restxt)[0] + "," + lonp.findall(restxt)[0]
        session.close()
        return historyValue


    def get_win_info(self, historyValue, lotto_type, lotto_round, result:list):
        """
            당첨결과에서 위도,경도 데이터는 lotto645밖에 없으므로 lotto645에서만 위도/경도를 구한다.
            Args:
                historyValue: list[dict]
                lotto_type: str
                lotto_round: str
                result: list
            Return:
                result: list
            [{}]
            [{'번호': '4', '상호명': '복권방', '소재지': '인천광역시 남동구 백범로273번길 1 (간석동) 1 1층'},...]
        """
        if len(historyValue[0]) == 0:
            return result
        if lotto_type == "L645":
            historyValue = self.get_latitude_longitude(historyValue)
        for value in historyValue:
            store = {}
            for k, v in value.items():
                if k == "위치보기":
                    store["위도경도"] = v
                else:
                    store[k] = v
                store["winRound"] = lotto_round
            result.append(store.copy())
            store.clear()
        return result
    
    def parse_win_history_data(self, response):
        """
            Args:
                response: str 응답
            Returns:
                key  : dict
                tdTeg: dict
        """
                #parse table tag
        p = re.compile("(?<=\<table class\=\"tbl_data tbl_data_col\">)(.*?)(?=<\/table>)",re.DOTALL)
        m = p.findall(response)
        with open("./adsasd.html","w") as f:
            f.write(response)
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
            for t in range(len(v)):
                tdTag = {}
                td = p.findall(v[t])
                for i in range(len(td)):
                    if "javascript" in td[i][1]:
                        td[i] = latiLongi.findall(td[i][1])[0]
                    tdTag[key[k][i]] = td[i][1]
                td = classLt.findall(v[t])
                for i in range(len(td)):
                    tdTag[key[k][2]] = td[i][1]
                tdTags[k].append(tdTag.copy())
                tdTag.clear()

        return tdTags
    
    def get_win_history_header(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        return headers
    
    def get_win_history_postdata(self, sido, sigugun):
        postData = {
            "method": "topStore",
            "nowPage": "1",
            "rangNo": "",
            "gameNo": "5133",
            "drwNo":"",
            "schKey": "area",
            "schVal": (sido+" "+sigugun).encode('euc-kr')
        }
        postData["schVal"] = postData["schVal"].rstrip()
        return postData
    
    def get_session(self):
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        return session