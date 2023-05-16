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
        compare = []
        for k,v in total_data.items():
            compare.append(v)
        if len(compare) > 0:
            for data in data_list:
                for i in compare:
                    for j in i:
                        if j["상호명"] == data["상호명"] and j["winRound"] == data["winRound"] and j["번호"] == data["번호"]:
                            return total_data
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
    
    def _insertcheckMetropolitanCityOther(self, sido, data_list, total_data):
        self.winUtil.util.write_log_to_file("./log.log", f"sido: {sido}, Before total data: {total_data.__str__()}, dataList:{data_list.__str__()}")
        #주소 시/도 부분 수정하기 위함
        """
        소재지가 예를들어 대전서구, 대전광역시 서구, 대전시 중구, 대전 중구, 제주제주시 건입동 
        이런식으로 되어있기 때문에 분리
        """
        for data in data_list:
            sigugun = None
            address = data["소재지"]
            for s in self.urban[sido]:
                p = re.compile(f"{s}",re.DOTALL)
                if len(p.findall(address)) == 0:
                    if len(s.split()) > 1:
                        attach = f"{''.join(s.split())}"
                        p = re.compile(attach,re.DOTALL)
                        if len(p.findall(address)) == 0:
                            p = re.compile(s.split()[0],re.DOTALL)
                            if len(p.findall(address)) == 0:
                                self.winUtil.util.write_log_to_file("./log.log", f"There is no Match {address}, {s}")
                            else:
                                sigugun = ""
                        else:
                            sigugun = s
                            address = address.replace(sido,"")
                            address = address.replace(attach,"")
                            data["소재지"] = f"{sido} {sigugun} {address.lstrip()}"
                    else:
                        self.winUtil.util.write_log_to_file("./log.log", f"sigugun one: {address}, {s}")
                else:
                    sigugun = s
                    address = address.replace(sido,"")
                    address = address.replace(s,"")
                    data["소재지"] = f"{sido} {sigugun} {address.lstrip()}"
            if sigugun is None or len(sigugun) == 0:
                total_data[sido].append(data.copy())
            else:
                if (sido + " " + sigugun).strip() not in total_data.keys():
                    total_data[(sido + " " + sigugun).strip()] = []
                total_data[(sido + " " + sigugun).strip()].append(data.copy())
        self.winUtil.util.write_log_to_file("./log.log", f"sido: {sido}, After total data: {total_data.__str__()}")
        return total_data
    
    def _insertSidoOther(self, sido, data_list, total_data):
        """
            경북/경상북도, 경남/경상남도와 같이 도에서 분리되는 부분 데이터가공을 위한 함수
        """
        for data in data_list:
            data["소재지"] = data["소재지"].replace("  "," ")
            address = data["소재지"]
            addressArr = data["소재지"].split()
            if "동행복권" in address:
                continue
            sigugun = None
            for s in self.urban[sido]:
                p = re.compile(s)
                if len(p.findall(address)) == 0:
                    if len(s.split()) > 1:
                        attach = f"{''.join(s.split())}" #창원시 마포합천구가 창원시마포합천구로 붙어있는 경우
                        p = re.compile(attach,re.DOTALL)
                        if len(p.findall(address)) == 0:
                            p = re.compile(s.split()[0],re.DOTALL)#창원시 마포합천구가 창원시만 있는 경우
                            if len(p.findall(address)) == 0:
                                self.winUtil.util.write_log_to_file("./log.log", f"_insertSidoOther There is no Match {address}, {s}")
                            else:
                                #그냥 못찾은 경우와, 없는 경우를 구분해야함.
                                if address.index(sido) > -1: #경북/경상북도 구분
                                    p = re.compile(f"({sido})(.*?)(구)",re.DOTALL)
                                    if p.findall(address) == 0: #창원시 만 있는 경우
                                        sigugun = ""
                                        addressArr[0] = addressArr[0].replace(s.split()[0],"")
                                        address = " ".join(addressArr[1:])
                                        data["소재지"] = f"{sido} {address.lstrip()}"
                                        break
                                else:
                                    address = " ".join(addressArr[1:])
                                    data["소재지"] = f"{sido} {address.lstrip()}"
                                    break
                        else:
                            sigugun = s
                            if address.index(sido) > -1:
                                address = address.replace(sido,"")
                            else:
                                addressArr[0] = addressArr[0].replace(attach, "")
                                address = " ".join(addressArr[1:])
                            address = address.replace(attach,"")
                            data["소재지"] = f"{sido} {sigugun} {address.lstrip()}"
                    # else:
                    #     self.winUtil.util.write_log_to_file("./log.log", f"_insertSidoOther sigugun one: {address}, {s}")
                else:
                    sigugun = s
                    self.winUtil.util.write_log_to_file("./log.log", f"address: {address}, {sido}, {sigugun}, {data['소재지']}")
                    if address.index(sido) > -1:
                        address = address.replace(sido, "")
                    else:
                        address = " ".join(addressArr[1:])
                    address = address.replace(sigugun, "")
                    data["소재지"] = f"{sido} {sigugun} {address.lstrip()}"
                    self.winUtil.util.write_log_to_file("./log.log", f"After address: {data['소재지']}")
                    break
            if sigugun is None or len(sigugun) == 0:
                if len(total_data) == 0 or sido not in total_data.keys():
                    total_data[sido] = []
                total_data[sido].append(data.copy())
            else:
                if len(total_data) == 0 or sigugun not in total_data.keys(): 
                    total_data[sigugun] = []
                total_data[sigugun].append(data.copy())
        return total_data

    #method=topStore&pageGubun=L645
    def parseWinHistory(self, session, url, sido, headers, queryParam):
        """
            TODO. sido로만 파싱하는걸로 변경해야할듯 싶다.
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
        # for sigugun in self.urban[sido]:
        #광역시는 lotto645종류에서는 나오지 않고, sppetto,annual 복권에서만 나옴
        sidoOther = self.winUtil.checkMetropolitanCity(sido, queryParam["pageGubun"])
        # postData = self.winUtil.get_win_history_postdata(sido, "")
        #경북,경남,전북 등 경상북도/경북 으로 불릴수있는 지역들 재검색
        if areaOther != None:
            firstHistory.clear()
            secondHistory.clear()
            postDataOther = self.winUtil.get_win_history_postdata(areaOther, "")
            firstHistory, secondHistory = \
                self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)
            
            # firstSido[areaOther+" "+ sigugun] = firstHistory
            # secondSido[areaOther+" "+ sigugun] = secondHistory
        elif sidoOther != None:
            firstHistory.clear()
            secondHistory.clear()
            postData = self.winUtil.get_win_history_postdata(sidoOther, "")
            firstHistory, secondHistory = \
                self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)
            # self.winUtil.util.write_log_to_file("./log.log", f"sidoOther: {sidoOther}, After parseWinHistoryLogic: {secondHistory.__str__()}")
            # firstSido = self._insertcheckMetropolitanCityOther(sido, firstHistory, firstSido)
            # self.winUtil.util.write_log_to_file("./log.log", f"SECOND DATA MERGE")
            # secondSido = self._insertcheckMetropolitanCityOther(sido, secondHistory, secondSido)
            # self.winUtil.util.write_log_to_file("./log.log", f"sidoOther: {sidoOther}, After FUNCTION data: {secondSido.__str__()}")
        else:
            firstHistory.clear()
            secondHistory.clear()
            firstHistory, secondHistory = \
                    self.winUtil.parseWinHistoryLogic(session, url, 1, maxRound, postData, headers, queryParam)
            # firstSido[sido] = firstHistory.copy()
            # secondSido[sido] = secondHistory.copy()
        firstSido = self._insertSidoOther(sido, firstHistory, firstSido)
        secondSido = self._insertSidoOther(sido, secondHistory, secondSido)
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

    def parseWinHistoryLogic(self, session, url, initialRound, maxRound, postData, headers, queryParam):
        try:
            # postData = self.winUtil.get_win_history_postdata(sido, sigugun)
            firstHistory = []
            secondHistory = []
            duplicateFirst = None
            self.util.write_log_to_file("./log.log", f"winHistory maxRound: {maxRound}")
            for no in range(initialRound, int(maxRound)+1):
                postData["drwNo"] = str(no)
                duplicateSecond = None
                postData['nowPage'] = "1"
                is_1stDuplicate = False
                is_2stDuplicate = False
                #get last page
                response = session.request("POST",url,headers=headers, data=postData, params=queryParam)
                restxt = response.text
                # with open("./win_history_11.html","w") as f:
                    # f.write(restxt)
                p = re.compile("(\<a href=\"javascript\:void\(0\)\" onclick\=\"selfSubmit\([\d]\)\" \>)(.*?)(</a>)")
                m = p.findall(restxt)
                if len(m) > 0:
                    maxPage = int(m[len(m)-1][1])
                elif len(m) == 0:
                    maxPage = 1
                winRankFirstData = {}
                for i in range(maxPage):
                    breakCount = 0
                    response = session.request("POST",url,headers=headers, data=postData, params=queryParam)
                    restxt = response.text
                    #<td class="nodata" colspan="5">조회 결과가 없습니다.</td>
                    p = re.compile("(\<td class=\"nodata\" colspan=\"[\d]+\"\>)(.*?)(\<\/td\>)")
                    m = p.findall(restxt)
                    #1등 배출점, 2등 배출점 두 곳 다 nodata라고 되어있으면 빠져나가기 위함.
                    if m.__len__() == 2:
                        break
                    winHistoryValue = self.parse_win_history_data(restxt)
                    self.util.write_log_to_file("./log.log", f"ROUND:{postData['drwNo']}, {winHistoryValue.__str__()}")
                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    if len(winHistoryValue["1st"][0]) == 0:
                        breakCount += 1
                    else:
                        firstCompare = winHistoryValue["1st"][0].copy()
                        if duplicateFirst:
                            if duplicateFirst["상호명"] == firstCompare["상호명"] \
                            and duplicateFirst["번호"] == firstCompare["번호"]:
                                is_1stDuplicate = True
                            else:
                                duplicateFirst = firstCompare
                        else:
                            duplicateFirst = firstCompare.copy()
                    if len(winHistoryValue["2st"][0]) == 0:
                        breakCount += 1
                    else:
                        secondCompare = winHistoryValue["2st"][0].copy()
                        if duplicateSecond:
                            if duplicateSecond["상호명"] == secondCompare["상호명"]\
                            and duplicateSecond["번호"] == secondCompare["번호"]:
                                is_2stDuplicate = True
                            else:
                                duplicateSecond = secondCompare.copy()
                        else:
                            duplicateSecond = secondCompare.copy()
                    if breakCount == 2:
                        break
                    # if len(winRankFirstData) == 0:
                    #     winRankFirstData = winHistoryValue.copy()
                    # else:
                    #     for k,v in winHistoryValue.items():
                    #         for k1, v1 in winRankFirstData.items():
                    #         if v1["번호"] == v["번호"] and v1["상호명"] == v["상호명"]:
                                
                    #             break
                    if is_1stDuplicate:
                        winHistoryValue["1st"] = []
                    if is_2stDuplicate:
                        winHistoryValue["2st"] = []
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
        if len(historyValue) == 0 or len(historyValue[0]) == 0:
            return result
        if lotto_type == "L645":
            historyValue = self.get_latitude_longitude(historyValue)
        for value in historyValue:
            store = {}
            for k, v in value.items():
                # if k == "위치보기":
                #     store["위도경도"] = v
                # else:
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
            "schVal": (sido+" "+sigugun).strip().encode('euc-kr')
        }
        postData["schVal"] = postData["schVal"].rstrip()
        return postData
    
    def get_session(self):
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        return session