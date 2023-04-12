import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import abc
from save import jdbc_config
import time
from datetime import datetime
class Thumnail(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parseThumnailData(self, store):
        raise NotImplemented

class ThumnailByNaver(Thumnail):
    def parseThumnailData(self, store):
        latitude = store["storelatitude"]
        longitude = store["storelongitude"]
        address = store["storeaddress"]
        store_name = store["storename"]
        store_uuid = store["storeuuid"]
        db = jdbc_config.JDBCConfig()
        url = "https://map.naver.com/v5/api/addresses/"+str(longitude)+","+str(latitude)
        #get Session
        session = requests.Session()
        param = self.setParams(address)
        response = session.request("GET", url, params=param)
        # self.log(f"url={url}, param={param}, storeuuid={store['storeuuid']}, status={response.status_code}")
        if response.status_code == 503:
            self.log(f"first url fail={response.status_code}, content={response.content}")
            print(f"fail={response.status_code}")
            return response.status_code
        jsonData = response.json()
        if store_name not in response:
            time.sleep(5)
            print("for loop sleep 1")
            param = self.setParams(jsonData["address"]["address"])
            url = "https://map.naver.com/v5/api/addresses/"+ str(jsonData["address"]["x"]) +","+ str(jsonData["address"]["y"])
            response = session.request("GET", url, params=param)
            # self.log(f"Re url={url}, param={param}, storeuuid={store['storeuuid']}, status={response.status_code}")
            if response.status_code == 200:
                print(f"success={response.status_code}")
            else:
                return response.status_code
            jsonData = response.json()
        if "place" not in jsonData.keys():
            print("no place key\n")
            with open(f"error_{store['storename']}.json","w") as fp:
                json.dump(jsonData, fp, ensure_ascii=False)
            return response.status_code
        print("yes place key")
        place = jsonData["place"]["list"]
        with open(f"test/thumnailjson/{store_uuid}_{store_name}.json", "w") as fp:
            json.dump(jsonData, fp, ensure_ascii=False)
        for store_info in place:
            self.log(store_info)
            compare_storename = store_info["name"]
            if store_name.strip() != compare_storename.strip():
                if store_name.strip() != store_info["display"].strip():
                    continue
            thumnailUrls = store_info["thumUrls"]
            detail = store_info["businessStatus"]["status"]["detailInfo"]
            telDisplay = store_info["telDisplay"]
            self.log(f"storeuuid={store_uuid}, detail={detail}, tel={telDisplay}")
            self.log(f"thumnailUrls={', '.join(thumnailUrls)}")
            for thumnailUrl in thumnailUrls:
                self.log(thumnailUrl)
                saved_name, original_name = self.getImageNameByUrl(store, thumnailUrl)
                time.sleep(3)
                print("for loop sleep 2")
                response = session.request("GET", thumnailUrl)
                if response.status_code == 200:
                    print(f"success={response.status_code}")
                else:
                    self.log(f"get thumnail image fail, {store_uuid}, {store_name}, {response.status_code}")
                    return response.status_code
                with open(f"test/thumnail/{saved_name}.jpg","wb") as f:
                    f.write(response.content)
                    content_size = len(response.content)
                insert_query = f"""insert into store_attachment(original_file_name,saved_file_name, file_size, storeuuid)
                    values('{original_name}', '{saved_name}', {content_size}, \'{store['storeuuid']}\')"""
                self.log(insert_query)
                ret = db.execute_query(
                    insert_query, 
                    False)

            break
        # self.log("for loop place end!!")
        time.sleep(3)
        self.log("=====end of parseThumnailData=====")
        return response.status_code
    def setParams(self, address):
        return {
            "address": address,
            "lang" : "ko",
            "detail" : "true"
        }
    
    def getImageNameByUrl(self, store, url:str):
        """
            ThumnailUrl ex) https://ldb-phinf.pstatic.net/20150901_281/1441105406787GfVgC_JPEG/166653555863554_0.jpeg
            Args:
                url : str
            Returns:
                saved_file_name : str
                original_file_name: str
        """
        thumnail_arrs = url.split("/")
        self.log(f"thumnailUrl={url}, storeuuid={store['storeuuid']}")
        file_names = thumnail_arrs[len(thumnail_arrs) - 1].split(".")
        saved_file_name = file_names[0]
        arr = saved_file_name.split("_")
        original_file_name = f"{store['storesido']}_{store['storesigugun']}_{store['storename']}_{arr[0]}"
        self.log(f"saved_file_name={saved_file_name}, original_file_name={original_file_name}")
        return saved_file_name, original_file_name

    def get_current_time(self):
        """
            Args:
                None
            Returns:
                timeformat: str
                dateformat: str
        """
        current = datetime.now()
        time = current.strftime("%H:%M:%S")
        date = current.strftime("%y-%m-%d")
        return date,time

    def log(self, message):
        date, time = self.get_current_time()
        if type(message) == dict:
            with open('log.log',"a") as f:
                json.dump(message, f, ensure_ascii=False)
            convert_message = ""
        elif type(message) == list:
            convert_message = ", ".join(message)
        elif type(message) == str:
            convert_message = message
        elif type(message) == int:
            convert_message = str(message)
        elif type(message) == float:
            convert_message = str(message)
        with open('log.log',"a") as f:
            f.write(f"[{date} {time}] {convert_message}\n")

