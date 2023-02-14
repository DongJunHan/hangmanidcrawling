import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from dto import hangmaniDTO
from service.save import jdbcImpl, jdbc
class JDBCConfig:
    def __init__(self):
        self.jdbcObject = jdbcImpl.ConnectImpl(jdbc.H2Connection())
    def _escape_query_string(self, value:str):
        if "'" in value:
            value = value.replace("'", "''")
        return value

    
    def save_store_data(self, store_dataes):
        conn = self.jdbcObject.connect()
        key = list()
        value = list()
        try:
            for dataes in store_dataes:
                for data in dataes:
                    key = []
                    value = []
                    data_dict = data.__dict__
                    for k, v in data_dict.items():
                        if k == "lottoHandle":
                            continue
                        key.append(k.upper())
                        
                        if v == None:
                            v = "NULL"
                        value.append(self._escape_query_string(v))
                        # if k.upper() == "STORECLOSETIME":
                        #     key.append("STOREISACTIVITY")
                        #     value.append(1)
                            
                    columnName = ",".join(key)
                    columnValues = ",".join("'{}'".format(i) for i in value)
                    # """
                    #     #len(value) 갯수대로 하면  에러에 하나 더 늘어나 있음
                    #     org.h2.jdbc.org.h2.jdbc.JdbcSQLSyntaxErrorException: org.h2.jdbc.JdbcSQLSyntaxErrorException: 
                    #     Column count does not match; SQL statement:

                    #     insert into store(STOREUUID,STORENAME,STOREADDRESS,STORELATITUDE,STORELONGITUDE,
                    #     STOREBIZNO,STORETELNUM,STOREMOBILENUM,STOREOPENTIME,STORECLOSETIME,STOREISACTIVITY,STORESIDO,
                    #     STORESIGUGUN) 
                    #     values('?','?','?','?','?','?','?','?','?','?','?','?','?','?'); 
                    #     [21002-200]
                    #     그렇다고 len - 1 하게되면  Invalid index 에러가 발생.
                    # """
                    # columnValues = ",".join("?" for _ in range(len(value))) 
                    result = self.jdbcObject.execute(
                        conn, f"insert into store({columnName}) values({columnValues});", 
                        False)
        except Exception as e:
            raise e
        finally:
            if conn != None:
                conn.commit()
                conn.close()
        
        
    def select_query(self, query, flag):
        conn = self.jdbcObject.connect()
        result = self.jdbcObject.execute(conn, query, flag)
        if conn != None:
            conn.commit()
            conn.close()
        return result
    def save_win_history_data(self, win_history_data):
        """
            Args:
                win_history_data: list[hangmaniDTO.WinHistory]
        """
        conn = self.jdbcObject.connect()
        try:
            for data in win_history_data:
                self.jdbcObject.execute(conn, f"insert into win_history values('{data.storeUuid}','{data.lottoId}','{data.winRound}','{data.winRank}')", False)  
        except Exception as e:
            raise e
        finally:
            conn.commit()
            conn.close()