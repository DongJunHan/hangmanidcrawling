import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import unittest
import json
import re
import requests
from html.parser import HTMLParser
from service.crwaling import thumnail_crawling, lotto_store_crawling, lotto_win_history_crawling, lotto_config
from service.compare import data_compare
from service.save import jdbc_config
from dto import util
import time

class TestStoreInfo(unittest.TestCase):
    def test_store_info(self):
        #parse, save storeinfo
        # storeInfo = lotto_config.LottoConfig().parseStoreInfo()
        # #save store lotto_type_handle
        # jdbc_config.JDBCConfig().save_store_data(storeInfo)
        # for stores in storeInfo:
        #     for store in stores:
        #         jdbc_config.JDBCConfig().save_store_lotto_types(store.lottoHandleList)
        #parse, save win_history
        # firstRankWinHistory , secondRankWinHistory = lotto_config.LottoConfig().parseWinHistory()
        # with open("./win_history.json", "w") as f:
        #     f.write(json.dumps(firstRankWinHistory,ensure_ascii=False))
        # with open("./win_history_2.json","w") as f:
        #     f.write(json.dumps(secondRankWinHistory, ensure_ascii=False))
        addresses = util.Variable().address_map
        for sido in addresses:
            with open(f"./test/win_history_dump/t_1_{sido}.json", "r") as f:
                firstRankWinHistory = json.load(f)
            with open(f"./test/win_history_dump/t_2_{sido}.json", "r") as f:
                secondRankWinHistory = json.load(f)
            
            lotto_config.LottoConfig().compareAndSaveWinHistory(firstRankWinHistory, secondRankWinHistory)
        """
        """
        # with open("./win_history_11.html","r") as f:
        #     restxt = f.read()
        # p = re.compile("(\<a href=\"javascript\:void\(0\)\" onclick\=\"selfSubmit\([\d]\)\" \>)(.*?)(</a>)")
        # m = p.findall(restxt)
        # print(m)
        # s = "경남 창원시 중앙동 대우증권빌딩 앞"
        # sido = util.Variable().address_map
        # for k,v in sido.items():
        #     for i in v:
        #         p = re.compile(f"{i}",re.DOTALL)
        #         if len(p.findall(s)) == 0:
        #             if len(i.split()) > 1:
        #                 p = re.compile(f"{''.join(i.split())}",re.DOTALL)
        #                 if len(p.findall(s)) == 0:
        #                     p = re.compile(i.split()[0],re.DOTALL)
        #                     if len(p.findall(s)):
        #                         print("Error Log plz")
        #         p.findall(s)

    
    def test_save_lotto_type(self):
        # jdbc_config.JDBCConfig().save_store_lotto_types()
        ret = jdbc_config.JDBCConfig().execute_query("select * from STORE;", True)
        print(ret)
    
    def test_parse_thumnail(self):
        s = "대박복권"
        with open("naverThumnail.json", "r") as fp:
            data = json.load(fp)
        arr = data["place"]["list"]
        for storeinfo in arr:
            storename = storeinfo["name"]
            if s != storename:
                continue
            thumnailUrls = storeinfo["thumUrls"]
            detail = storeinfo["businessStatus"]["status"]["detailInfo"]
            telDisplay = storeinfo["telDisplay"]
            print(f"storename={storename}, thumnailurl={thumnailUrls}, detail={detail}, tel={telDisplay}")
            for thumnail in thumnailUrls:
                arrs = thumnail.split("/")
                response = requests.request("GET", thumnail)
                with open(f"{arrs[4]}.jpg","wb") as f:
                    f.write(response.content)
            break
    
    def decodeUnicode(self):
        with open("./test/sql/data.sql") as f:
            data = f.read()
            # (?<=\<thead>)(.*?)(?=<\/thead>)
        print(data)
    
        # data = data.replace(",\n(", "),\n(")
        data = data.replace("')),", "'),")

        # p = re.compile("\\\\u[0-9a-fA-F]{4}")
        # m = p.findall(data)
        # for i in m:
        #     s = bytes(i, 'utf-8').decode('unicode-escape')

        #     data = data.replace(i, s)
        with open("./test/sql/data.sql", "w") as f:
            f.write(data)

    def test_thumnail(self):
        address_map = util.Variable().address_map
        naver = thumnail_crawling.ThumnailByNaver()
        # query = f"""select storeuuid, storename, storelongitude, storelatitude, storeaddress, storesido, 
        #          storesigugun from store where storeaddress='인천 부평구 마장로 387-1 1층'"""
        # result = jdbc_config.JDBCConfig().select_query(query, True)
        # for store in result:
        #     ret = naver.parseThumnailData(store)
        #     if ret != 200:
        #         print(f"result={result}")
        #         print(f"@@store={store}")
        #         return
        check = {}
        for i in address_map:
            check[i] = {}
            for j in address_map[i]:
                check[i][j] = False
        with open("save_thumnail.txt", "r") as f:
            saved_storeuuid = f.read().strip()
        while True:
            flag = False
            for sido in check.keys():
                for sigugun in check[sido].keys():
                    if check[sido][sigugun]:
                        continue
                    check[sido][sigugun] = True
                    query = f"""select storeuuid, storename, storelongitude, storelatitude, storeaddress, storesido, 
                    storesigugun from store where storesido='{sido}' and storesigugun='{sigugun}' order by storelatitude; """
                    result = jdbc_config.JDBCConfig().select_query(query, True)
                    for store in result:
                        if len(saved_storeuuid) != 0:
                            print(f"save = {saved_storeuuid}, uuid= {store['storeuuid']}")
                            if saved_storeuuid != store["storeuuid"]:
                                continue
                        ret = naver.parseThumnailData(store)
                        if ret != 200:
                            check[sido][sigugun] = False
                            print(f"@@store={store}")
                            with open("save_thumnail.txt", "w") as fp:
                                fp.write(store["storeuuid"])
                            saved_storeuuid = store["storeuuid"]
                            time.sleep(180)
                            break
            for sido in check.keys():
                for siggugun in check[sido].keys():
                    if check[sido][siggugun]:
                        flag = True
                    else:
                        flag = False
            if flag:
                return
                            
            

class TestCompareInfo(unittest.TestCase):
    def test_store_compare(self):
        with open('annual_부평구.json') as f:
            originData = json.load(f)
        with open('lotto645_부평구.json') as f:
            compareData = json.load(f)
        storeInfos = data_compare.StoreInfoCompare().compareStores(originData["arr"], compareData["arr"], '인천', '부평구')
        result = list()
        print(type(storeInfos))
        for i in storeInfos:
            query = f"select storeuuid,storename from store where storename='{i.storeName.rstrip()}' and storelatitude={float(i.storeLatitude)} and storelongitude={float(i.storeLongitude)};"
            ret = jdbc_config.JDBCConfig().select_query(query, True)
            # print(ret)
            if len(ret) == 0:
                print(query)
                result.append(None)
                continue
                # query = f"select storeuuid,storename from store where storename='{i.storeName.rstrip()}';"
            result.append(ret[0])
        for i in range(len(storeInfos)):
            if result[i] == None:
                continue
            handleList = storeInfos[i].lottoHandleList
            for j in handleList:
                print(f"before={j.storeUuid}")
                j.storeUuid = result[i]["storeuuid"]
                print(f"after={j.storeUuid}")


            ret = jdbc_config.JDBCConfig().save_store_lotto_types(handleList)



class TestWinInfo(unittest.TestCase):
    # dataCompare = data_compare.WinHistoryInfoCompare()
    # save = jdbc_config.JDBCConfig()
    def _insertSidoOther(self, sido, data_list, total_data):
        """
            경북/경상북도, 경남/경상남도와 같이 도에서 분리되는 부분 데이터가공을 위한 함수
            [lotto_type][current_round][data]
        """
        urban = util.Variable().address_map
        for lotto_type in data_list.keys():
            for cr, dataes in data_list[lotto_type].items():
                for data in dataes:
                    if len(data) == 0:
                        break
                    data["소재지"] = data["소재지"].replace("  "," ")
                    address = data["소재지"]
                    addressArr = data["소재지"].split()
                    data["winRound"] = cr
                    if "구분" in data.keys():
                        del data["구분"]
                    if "동행복권" in address:
                        continue
                    sigugun = None
                    for s in urban[sido]:
                        p = re.compile(s)
                        if len(p.findall(address)) == 0:
                            if len(s.split()) > 1:
                                attach = f"{''.join(s.split())}" #창원시 마포합천구가 창원시마포합천구로 붙어있는 경우
                                p = re.compile(attach,re.DOTALL)
                                if len(p.findall(address)) == 0:
                                    p = re.compile(s.split()[0],re.DOTALL)#창원시 마포합천구가 창원시만 있는 경우
                                    if len(p.findall(address)) == 0:
                                        print("")
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
                        else:
                            sigugun = s
                            # self.winUtil.util.write_log_to_file("./log.log", f"address: {address}, {sido}, {sigugun}, {data['소재지']}")
                            if address.index(sido) > -1:
                                address = address.replace(sido, "")
                            else:
                                address = " ".join(addressArr[1:])
                            address = address.replace(sigugun, "")
                            data["소재지"] = f"{sido} {sigugun} {address.lstrip()}"
                            # self.winUtil.util.write_log_to_file("./log.log", f"After address: {data['소재지']}")
                            break
                    if sigugun is None or len(sigugun) == 0:
                        if sido not in total_data[lotto_type].keys():
                            total_data[lotto_type][sido] = []
                        total_data[lotto_type][sido].append(data.copy())
                    else:
                        if sigugun not in total_data[lotto_type].keys(): 
                            total_data[lotto_type][sigugun] = []
                        total_data[lotto_type][sigugun].append(data.copy())
        return total_data
    def test_win_info(self):
        # first_win_info , second_win_info = lotto_config.LottoConfig().parseWinHistory()
        win_util = lotto_win_history_crawling.WinInfoUtil()
        total_1st = {}
        total_2st = {}
        addresses = util.Variable().address_map
        for sido in addresses:
            arr = []
            with open(f"./test/win_history_log/log_{sido}.log", "r") as f:
                res = f.read()
            arr = res.split("\n")
            lotto_type = None
            sido_1st = {}
            sido_2st = {}
            for i in arr:
                if i.find("maxRound:") > -1:
                    lotto_round = int(i[i.find("maxRound:") + len("maxRound:"):].strip())
                    if lotto_round == 1066:
                        lotto_type = "lotto645"
                    elif lotto_round == 158:
                        lotto_type = "annual"
                    elif lotto_round == 47:
                        lotto_type = "speetto2000"
                    elif lotto_round == 71:
                        lotto_type = "speetto1000"
                    elif lotto_round == 42:
                        lotto_type = "speetto500"
                    sido_1st[lotto_type] = {}
                    sido_2st[lotto_type] = {}
                    total_1st[lotto_type] = {}
                    total_2st[lotto_type] = {}
                if "ROUND" not in i:
                    continue
                if lotto_type not in sido_1st.keys() or lotto_type not in sido_2st.keys():
                    print(i)
                cur_round = int(i[i.find("ROUND:") + len("ROUND:"):i.find(",")].strip())
                sido_1st[lotto_type][cur_round] = []
                sido_2st[lotto_type][cur_round] = []
                i = i[i.find(","):].strip()
                history_1st = (i[i.find("1st")+ len("1st':"):i.find("]") + 1].strip())
                i = i[i.find("]")+1:]
                history_2st = (i[i.find("2st")+ len("2st':"):i.find("]") + 1].strip())
                history_1st = history_1st.replace("'", "\"")
                history_2st = history_2st.replace("'", "\"")
                history_1st = json.loads(history_1st)
                history_2st = json.loads(history_2st)
                #get latitude, longitude
                history_1st = win_util.get_latitude_longitude(history_1st)
                history_2st = win_util.get_latitude_longitude(history_2st)
                sido_1st[lotto_type][cur_round] = history_1st
                sido_2st[lotto_type][cur_round] = history_2st
            total_1st = self._insertSidoOther(sido, sido_1st, total_1st)
            total_2st = self._insertSidoOther(sido, sido_2st, total_2st)
            with open(f"./test/win_history_dump/win_history_{sido}.json", "w") as f:
                f.write(json.dumps(total_1st,ensure_ascii=False))
            with open(f"./test/win_history_dump/win_history_2_{sido}.json", "w") as f:
                f.write(json.dumps(total_2st,ensure_ascii=False))

        # print(first_win_info)
        # print(second_win_info)
        # with open("./win_history.json", "w") as f:
        #     f.write(first_win_info.__str__())

        # with open("./win_history_2.json", "w") as f:
        #     f.write(second_win_info.__str__())
    
    def test_query(self):
        with open("./win_history.json") as f:
            a = json.load(f)
            firstRankWinHistory = a
            # firstRankWinHistory = {}
            # firstRankWinHistory["lotto645"] = a
        with open("./win_history_2.json") as f:
            a = json.load(f)
            secondRankWinHistory = a
            # secondRankWinHistory = {}
            # secondRankWinHistory["lotto645"] = a
        lotto_config.LottoConfig().compareAndSaveWinHistory(firstRankWinHistory, secondRankWinHistory)
        
        # self.save.save_win_history_data(result)
    def test_parse_win_history_data(self):
        duplicateFirst = None
        firstHistory = []
        secondHistory = []
        file_name_list = ["win_history_res_L645_1.html", "win_history_res_L645_2.html",
        "win_history_res_L720_1.html", "win_history_res_SP500_1.html", "win_history_res_SP1000_1.html",
        "win_history_res_SP2000_1.html"]
        dataes = {}
        util = lotto_win_history_crawling.WinInfoUtil()
        #get html data
        for i in file_name_list:
            with open(i, "r") as f:
                dataes[i] = f.read()
        is_duplicate = False
        duplicate = False
        for k,v in dataes.items():
            duplicateSecond = None
            winHistoryValue = util.parse_win_history_data(v)
            if len(winHistoryValue["1st"][0]) == 0:
                with open("./log.log","a") as f:
                    f.write("winRank 1 noData\n")
            else:
                firstCompare = winHistoryValue["1st"][0].copy()
                if duplicateFirst:
                    if duplicateFirst["상호명"] == firstCompare["상호명"] \
                    and duplicateFirst["소재지"] == firstCompare["소재지"]:
                        is_duplicate = True
                        with open("./log.log","a") as f:
                            f.write(f"{k} : first Duplicate: {duplicateFirst}, {firstCompare}\n")
                    else:
                        duplicateFirst = firstCompare.copy()
                else:
                    duplicateFirst = firstCompare.copy()
            if len(winHistoryValue["2st"][0]) == 0:
                with open("./log.log","a") as f:
                    f.write("winRank 2 noData\n")
            else:
                secondCompare = winHistoryValue["2st"][0].copy()
                if duplicateSecond:
                    if duplicateSecond["상호명"] == secondCompare["상호명"]\
                    and duplicateSecond["소재지"] == secondCompare["소재지"]:
                        duplicate = True
                        with open("./log.log","a") as f:
                            f.write(f"{k} : second Duplicate: {duplicateSecond}, {secondCompare}\n")
                    else:
                        duplicateSecond = secondCompare.copy()
                else:
                    duplicateSecond = secondCompare.copy()
            if is_duplicate:
                winHistoryValue["1st"] = []
            if duplicate:
                winHistoryValue["2st"] = []
            firstHistory = util.get_win_info(winHistoryValue["1st"], k, 1, firstHistory)
            secondHistory = util.get_win_info(winHistoryValue["2st"], k, 1, secondHistory)
            with open("./log.log","a") as f:
                f.write(firstHistory.__str__()+"\n")
                f.write(secondHistory.__str__()+"\n")
        # with open("./history_test.json", "w") as f:
            # f.write(json.dumps(firstRankWinHistory,ensure_ascii=False))
        # with open("./history_test2.json","w") as f:
            # f.write(json.dumps(secondRankWinHistory, ensure_ascii=False))

    def test_regex(self):
        file_name = "adsasd.html"
        with open(f"./{file_name}","r") as f:
            response = f.read()
        #parse table tag
        p = re.compile("(?<=\<table class\=\"tbl_data tbl_data_col\">)(.*?)(?=<\/table>)",re.DOTALL)
        m = p.findall(response)
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
            tdTag = {}
            for tr in range(len(v)):
                td = p.findall(v[tr])
                for i in range(len(td)):
                    if "javascript" in td[i][1]:
                        td[i] = latiLongi.findall(td[i][1])[0]
                    tdTag[key[k][i]] = td[i][1]
                td = classLt.findall(v[tr])
                for i in range(len(td)):
                    tdTag[key[k][2]] = td[i][1]
                tdTags[k].append(tdTag.copy())
                print(tdTags)
                print("========")
            
        print(tdTags)
    def test_long_lat(self):
        # valueHistory = {1: ['1', '스파', '자동 ', '서울 노원구 동일로 1493 상계주공아파트(10단지) 주공10단지종합상가111', '11100773']}
        addresses = util.Variable().address_map
        winInfo = lotto_win_history_crawling.WinInfoUtil()
        for sido in addresses:
            with open(f"./test/win_history_dump/win_history_{sido}.json","r") as f:
                history_1st = json.load(f)
            with open(f"./test/win_history_dump/win_history_2_{sido}.json","r") as f:
                history_2st = json.load(f)
            lotto645_1st = history_1st["lotto645"][sido]
            lotto645_2st = history_2st["lotto645"][sido]
            if sido == "세종":
                value = winInfo.get_latitude_longitude(lotto645_1st)
                history_1st["lotto645"][sido] = value
                value = winInfo.get_latitude_longitude(lotto645_2st)
                history_2st["lotto645"][sido] = value
            else:
                for k,v in lotto645_1st.items():
                    value = winInfo.get_latitude_longitude(v)
                    history_1st["lotto645"][sido][k] = value
                for k,v in lotto645_2st.items():
                    value = winInfo.get_latitude_longitude(v)
                    history_2st["lotto645"][sido][k] = value
            with open(f"./test/win_history_dump/t_1_{sido}.json","w") as f:
                f.write(json.dumps(history_1st, ensure_ascii=False))
            with open(f"./test/win_history_dump/t_2_{sido}.json","w") as f:
                f.write(json.dumps(history_2st, ensure_ascii=False))
    def test_function_insertSidoOther(self):
        with open("win_history.json", "r") as f:
            res = json.load(f)
        data_list = res["speeto2000"]["경남"]
        total_data = {}
        total_data = lotto_win_history_crawling.WinHistoryAllByArea()._insertSidoOther("경남", data_list, total_data)
        util.Utils().write_log_to_file("./log.log", f"total_data: {total_data}")
        with open("./ss.json", "w") as f:
            f.write(json.dumps(total_data, ensure_ascii=False))
    
    def test_parse_win_history_by_file(self):
        addresses = util.Variable().address_map
        for sido in addresses:
            history_1st = None
            history_2st = None
            with open(f"./test/win_history_dump/win_history_{sido}.json", "r") as f:
                history_1st = json.load(f)
            
            with open(f"./test/win_history_dump/win_history_2_{sido}.json", "r") as f:
                history_2st = json.load(f)
            # other = data_compare.OtherWinInfoCompare()
            # db_1st, unknown_1st = other.compareHistoryToStoreInfo(1, history_1st)
            # db_2st, unknown_2st = other.compareHistoryToStoreInfo(2, history_2st)
            lotto645 = data_compare.Lotto645WinInfoCompare()
            db_1st, unknown_1st = lotto645.compareHistoryToStoreInfo(1, history_1st)
            db_2st, unknown_2st = lotto645.compareHistoryToStoreInfo(2, history_2st)
            util.Utils().write_log_to_file("./log.log", f"1 db: {db_1st}, \nunknown: {unknown_1st}")
            util.Utils().write_log_to_file("./log.log", f"2 db: {db_2st}, \nunknown: {unknown_2st}")
            # (SELECT COALESCE(GROUP_CONCAT(l.lottoname ORDER BY l.lottoname ASC SEPARATOR ','),'') AS lottonames
            #     FROM lotto_type_handle lh JOIN lotto_type l ON l.lottoid=lh.lottoid
            #     WHERE lh.storeuuid=s.storeuuid) AS lottonames,