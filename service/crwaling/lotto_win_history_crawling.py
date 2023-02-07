import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from html.parser import HTMLParser
import re
import requests
import json
from dto import util, hangmaniDTO

"""
    TODO. 
    1. 운영시 매주 한 번 프로그램을 돌려서 상점이 새로 추가됐는지, 기존의 상점이 없어졌는지 확인이 필요.
    2. 당첨 결과 매주 업데이트 로직.
    3. 당첨 결과 262회부터 파싱.

"""

class WinHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_group_content = False
        self.firstResult = []
        self.secondResult = []
        self.first_win = False
        self.second_win = False
    def get_first_result(self):
        return self.firstResult
    def get_second_result(self):
        return self.secondResult
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
            data = data.replace("\n","").replace("\t","").replace(" ","").replace("\r","")
            if len(data) != 0:
                if self.first_win:
                    self.firstResult.append(data)
                elif self.second_win:
                    self.secondResult.append(data)


class WinParseException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.value

class WinInfo:
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
        self.first_win_info = {}
        self.second_win_info = {}
        self.address_map = util.Variable().address_map


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
            
            p = re.compile("(\<option value=\"[\d]+\" selected\>)(.*?)(\<\/option\>)")
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

    def _get_first_win_info(self, first_list, lotto_type, lotto_round, result:list):
        lottoFlag = False
        if lotto_type == "L645":
            lottoFlag = True
        if "조회결과가없습니다." in first_list:
            return result
        store = {}
        if lottoFlag:
            keys = [first_list[1], first_list[2], first_list[3], first_list[4], first_list[5]]
        else:
            keys = [first_list[1], first_list[2], first_list[3]]
        i = len(keys)
        while True:
            if len(first_list) <= i+1:
                break
            for k in keys:
                i += 1
                store[k] = first_list[i]
            if len(first_list) > i+1 and  "배출점" in first_list[i+1]:
                i += 1
            store["round"] = lotto_round
            result.append(store)
        return result
    def _get_second_win_info(self, second_list, lotto_type, lotto_round, result:list):
        lottoFlag = False
        """
            ['상호명,소재지,위치등스피또5002등배출점안내', '번호', '상호명', '소재지', '조회결과가없습니다.']
            ['상호명,소재지,위치등스피또5001등배출점안내', '번호', '상호명', '소재지', '1', 'CU사상서부', '부산사상구사상로211번길121층']
        """
        if lotto_type == "L645":
            lottoFlag = True
        if "조회결과가없습니다." in second_list:
            return result
        store = {}
        if lottoFlag:
            keys = [second_list[1], second_list[2], second_list[3], second_list[4]]#, second_list[5]]
        else:
            keys = [second_list[1], second_list[2], second_list[3]]
        i = len(keys)
        while True:
            if len(second_list) <= i+1:
                break
            for k in keys:
                i += 1
                store[k] = second_list[i]
            if len(second_list) <= i+1:
                break
            if len(second_list) > i+1 and "배출점" in second_list[i+1]:
                i += 1
            store["round"] = lotto_round
            result.append(store)
        return result
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
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
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
            "schVal": (sido+" "+sigugun).encode('euc-kr')
        }
        
        session = requests.Session()
        # session.verify = "FidderRootCertificate.crt"
        if maxRound is None:
            maxRound = self._find_max_round(session, url, headers, postData, param)
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
                    response = session.request("POST",url,headers=headers, data=postData, params=param)
                    restxt = response.text
                    #<td class="nodata" colspan="5">조회 결과가 없습니다.</td>
                    p = re.compile("(\<td class=\"nodata\" colspan=\"[\d]+\"\>)(.*?)(\<\/td\>)")
                    m = p.findall(restxt)
                    if m.__len__() == 2:
                        break
                    htmlParser = WinHTMLParser()
                    htmlParser.feed(restxt)

                    #중복페이지 조회 로직: 조회결과가없을때는 항상 카운터를 올린다.
                    if "조회결과가없습니다." in htmlParser.get_first_result():
                        breakCount += 1
                    else:
                        if queryString["pageGubun"] == "L645":
                            firstCompare = htmlParser.get_first_result()[6]
                        else:
                            firstCompare = htmlParser.get_first_result()[5]

                        if duplicateFirst:
                            if duplicateFirst == firstCompare:
                                breakCount += 1
                        else:
                            duplicateFirst = firstCompare
                        
                    if "조회결과가없습니다." in htmlParser.secondResult:
                        breakCount += 1
                    else:
                        if queryString["pageGubun"] == "L645":
                            secondCompare = htmlParser.get_second_result()[6]
                        else:
                            secondCompare = htmlParser.get_second_result()[5]
                        
                        if duplicateSecond:
                            if duplicateSecond == secondCompare:
                                breakCount += 1
                        else:
                            duplicateSecond = secondCompare
                    
                    if breakCount == 2:
                        break

                    firstHistory = self._get_first_win_info(htmlParser.get_first_result(), queryString["pageGubun"], postData["drwNo"], firstHistory)
                    secondHistory = self._get_second_win_info(htmlParser.get_second_result(), queryString["pageGubun"], postData["drwNo"], secondHistory)

                    postData["nowPage"] = str(int(postData["nowPage"]) + 1)
            self.first_win_info[sido+" "+ sigugun] = firstHistory
            self.second_win_info[sido+" "+ sigugun] = secondHistory
        except Exception as e:
            raise e
    def getWinInfo(self):
        queryString = {}
        firstResult = {}
        secondResult = {}
        queryString["method"] = "topStore"
        for key, value in self.lottoTypes.items():
            queryString["pageGubun"] = value
            for sido in self.address_map.keys():
                for sigugun in self.address_map[sido]:
                    # print(f"lottoType: {value}, sido: {sido}, sigugun: {sigugun}")
                    self._parseAllWinInfoByArea("https://dhlottery.co.kr/store.do" ,sido, sigugun, queryString)
            firstResult[key] = self.first_win_info
            secondResult[key] = self.second_win_info
            self.first_win_info.clear()
            self.second_win_info.clear()
        return firstResult, secondResult
        
        # print(self.first_win_info)
        # print(self.second_win_info)

    # def get_first_win_info(self):
    #     return self.first_win_info

    # def get_second_win_info(self):
    #     return self.second_win_info