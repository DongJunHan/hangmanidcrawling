import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import re
import requests
import json
import abc
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
    def parseWinHistory(self, session, url, headers, postData, queryParam:dict):
        """
            Args:
                session   : requests.Session
                url       : str
                headers   : dict
                postData  : dict
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
    
    def parseWinHistory(self, session, url, headers, postData, queryParam):
        """
            Args:
                session   : requests.Session
                url       : str
                headers   : dict
                postData  : dict
                queryParam: dict
            Return
                firstList: list
                secondList: List
        """
        firstList = []
        secondList = []
        maxRound = self.winUtil.find_max_round(session, url, headers, postData, queryParam)
        try:
            firstHistory = []
            secondHistory = []
            for no in range(int(maxRound), int(maxRound)+1):
                postData["drwNo"] = str(no)
                duplicateFirst = None
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
                    winHistoryKey, winHistoryValue = self.winUtil.parse_win_history_data(restxt)

                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    if len(winHistoryValue["1st"][1]) == 0:
                        breakCount += 1
                    else:
                        firstCompare = winHistoryValue["1st"][1][1]

                        if duplicateFirst:
                            if duplicateFirst == firstCompare:
                                breakCount += 1
                        else:
                            duplicateFirst = firstCompare
                        
                    if len(winHistoryValue["2st"][1]) == 0:
                        breakCount += 1
                    else:
                        secondCompare = winHistoryValue["2st"][1][1]
                        
                        if duplicateSecond:
                            if duplicateSecond == secondCompare:
                                breakCount += 1
                        else:
                            duplicateSecond = secondCompare
                    
                    if breakCount == 2:
                        break

                    firstHistory = self.winUtil.get_first_win_info(winHistoryKey["1st"], winHistoryValue["1st"], queryParam["pageGubun"], postData["drwNo"], firstHistory)
                    secondHistory = self.winUtil.get_second_win_info(winHistoryKey["2st"], winHistoryValue["2st"], queryParam["pageGubun"], postData["drwNo"], secondHistory)

                    postData["nowPage"] = str(int(postData["nowPage"]) + 1)
            # self.first_win_info[sido+" "+ sigugun] = firstHistory
            # self.second_win_info[sido+" "+ sigugun] = secondHistory
        except Exception as e:
            raise e   
        return firstHistory, secondHistory
class WinHistoryAllByArea(WinHistoryByArea):
    def __init__(self):
        self.winUtil = WinInfoUtil()
        # self.first_win_info = {}
        # self.second_win_info = {}
    
    #method=topStore&pageGubun=L645
    def parseWinHistory(self, session, url, headers, postData, queryParam):
        """
            Args:
                session   : requests.Session
                url       : str
                headers   : dict
                postData  : dict
                queryParam: dict
            Return
                firstList: list
                secondList: List
        """
        firstList = []
        secondList = []
        maxRound = self.winUtil.find_max_round(session, url, headers, postData, queryParam)
        try:
            firstHistory = []
            secondHistory = []
            for no in range(1, int(maxRound)+1):
                postData["drwNo"] = str(no)
                duplicateFirst = None
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
                    winHistoryKey, winHistoryValue = self.winUtil.parse_win_history_data(restxt)
                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    if len(winHistoryValue["1st"][1]) == 0:
                        breakCount += 1
                    else:
                        firstCompare = winHistoryValue["1st"][1][1]

                        if duplicateFirst:
                            if duplicateFirst == firstCompare:
                                breakCount += 1
                        else:
                            duplicateFirst = firstCompare
                        
                    if len(winHistoryValue["2st"][1]) == 0:
                        breakCount += 1
                    else:
                        secondCompare = winHistoryValue["2st"][1][1]
                        
                        if duplicateSecond:
                            if duplicateSecond == secondCompare:
                                breakCount += 1
                        else:
                            duplicateSecond = secondCompare
                    
                    if breakCount == 2:
                        break

                    firstHistory = self.winUtil.get_first_win_info(winHistoryKey["1st"], winHistoryValue["1st"], queryParam["pageGubun"], postData["drwNo"], firstHistory)
                    secondHistory = self.winUtil.get_second_win_info(winHistoryKey["2st"], winHistoryValue["2st"], queryParam["pageGubun"], postData["drwNo"], secondHistory)

                    postData["nowPage"] = str(int(postData["nowPage"]) + 1)
            # self.first_win_info[sido+" "+ sigugun] = firstHistory
            # self.second_win_info[sido+" "+ sigugun] = secondHistory
        except Exception as e:
            raise e   
        return firstHistory, secondHistory
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
        self.address_map = util.Variable().address_map
        self.util = util.Utils()
        self.get_latitude_longitude = self.util.retry_wrapper(self.get_latitude_longitude)


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

    def get_latitude_longitude(self, winRank, historyValue):
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
        for num, values in historyValue.items():
            if winRank == 1:
                value = values[4]
            elif winRank == 2:
                value = values[3]
            queryParam = f"method=topStoreLocation&gbn=lotto&rtlrId={value}"
            url = f"https://dhlottery.co.kr/store.do?{queryParam}"
            response = session.request("GET", url, headers=headers)
            restxt = response.text

            if latp.search(restxt) == None:
                raise WinParseException(f"위치보기 위도 파싱 실패=> {values}")
            
            if lonp.search(restxt) == None:
                raise WinParseException(f"위치보기 경도 파싱 실패=> {values}")
            
            if len(latp.findall(restxt)[0]) == 0:
                raise WinParseException(f"위치보기 위도 결과 값 없음=> {values}")
            if len(lonp.findall(restxt)[0]) == 0:
                raise WinParseException(f"위치보기 경도 결과 값 없음=> {values}")
            if winRank == 1:
                historyValue[num][4] = latp.findall(restxt)[0] + "," + lonp.findall(restxt)[0]
            elif winRank == 2:
                historyValue[num][3] = latp.findall(restxt)[0] + "," + lonp.findall(restxt)[0]
        session.close()
        return historyValue


    def get_first_win_info(self, historyKey, historyValue, lotto_type, lotto_round, result:list):
        """
            당첨결과에서 위도,경도 데이터는 lotto645밖에 없으므로 lotto645에서만 위도/경도를 구한다.
            Args:
                historyKey: list
                historyValue: dict
                lotto_type: str
                lotto_round: str
                result: list
            Return:
                result: list
        """
        if len(historyValue) == 0 or len(historyValue[1]) == 0:
            return result
        if lotto_type == "L645":
            historyValue = self.get_latitude_longitude(1, historyValue)
        store = {}
        for key, value in historyValue.items():
            for i in range(len(value)):
                if historyKey[i] == "위치보기":
                    store["위도경도"] = value[i]
                else:
                    store[historyKey[i]] = value[i]
            store["winRound"] = lotto_round
            result.append(store)
        return result
    
    def get_second_win_info(self, historyKey, historyValue, lotto_type, lotto_round, result:list):
        """
            ['상호명,소재지,위치등스피또5002등배출점안내', '번호', '상호명', '소재지', '조회결과가없습니다.']
            ['상호명,소재지,위치등스피또5001등배출점안내', '번호', '상호명', '소재지', '1', 'CU사상서부', '부산사상구사상로211번길121층']
        """
        if len(historyValue) == 0 or len(historyValue[1]) == 0:
            return result
        if lotto_type == "L645":
            historyValue = self.get_latitude_longitude(2, historyValue)
        store = {}
        for key, value in historyValue.items():
            for i in range(len(value)):
                if historyKey[i] == "위치보기":
                    store["위도경도"] = value[i]
                else:
                    store[historyKey[i]] = value[i]
            store["winRound"] = lotto_round
            result.append(store)
        return result
    
    def parse_win_history_data(self, response):
        """
            Args:
                response: str 응답
            Returns:
                key  : dict
                tdTeg: dict
        """
        p = re.compile("(?<=\<table class\=\"tbl_data tbl_data_col\">)(.*?)(?=<\/tbody>)",re.DOTALL)
        m = p.findall(response)
        trTag = []
        for i in m:
            i = i.replace("\n","").replace("\t","").replace("\r","")
            #parse tr tag
            p = re.compile("(?<=\<tr>)(.*?)(?=<\/tr>)")
            tr = p.findall(i)
            trTag.append(tr)
        key = {}
        tdTag = {}
        #parse th tag
        for i in range(len(trTag)):
            tdTag[str(i+1) + "st"] = {}
            for j in range(len(trTag[i])):
                p = re.compile("(?<=\<th scope\=\"col\">)(.*?)(?=<\/th>)")
                if p.search(trTag[i][j]):
                    key[str(i+1) + "st"] = p.findall(trTag[i][j])
                else:
                    #parse td tag
                    p = re.compile("(?<=\<td>)(.*?)(?=<\/td>)")
                    tdTag[str(i+1) + "st"][j] = p.findall(trTag[i][j])
                    if "class=\"lt\"" in trTag[i][j]:
                        classLt = re.compile("(?<=\<td\sclass=\"lt\">)(.*?)(?=\<\/td>)")
                        if len(classLt.findall(trTag[i][j])) > 0:
                            tdTag[str(i+1) + "st"][j] += classLt.findall(trTag[i][j])  

        
        #save data
        for k1,v1 in tdTag.items():
            for k, v in v1.items():
                p = re.compile("(?<=\<a href=\"\#\" class=\"btn_search\" onClick=\"javascript\:showMapPage\(\\')(.*?)(?=\\'\)\")")
                for i in range(len(v)):
                    if p.search(v[i]):
                        tdTag[k1][k][i] = p.findall(v[i])[0]
        return key, tdTag
    
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
        return postData
    
    def get_session(self):
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        return session