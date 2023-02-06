import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.save import jdbc
class StoreInfoSave:
    def _escape_query_string(self, value:str):
        if "'" in value:
            value = value.replace("'", "''")
        return value

    def save_store_data(self, storeDataes):
        key = list()
        value = list()
        for data in storeDataes:
            key = []
            value = []
            data_dict = data.__dict__
            for k, v in data_dict.items():
                if k == "lottoHandle":
                    continue
                key.append(k)
                if v == None:
                    v = "NULL"
                value.append(self._escape_query_string(v))
            columnName = ",".join(key)
            columnValues = ",".join("'{}'".format(i) for i in value)
            jdbc.execute(f"insert into store({columnName}) values({columnValues});")