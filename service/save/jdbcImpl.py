import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from service.save import jdbc

class ConnectException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.value

class ConnectImpl:
    def __init__(self, jdbcObject:jdbc.Connection):
        self.jdbcObject = jdbcObject
        self.jdbcUtil = jdbc.DBUtil()
    
    def connect(self):
        
        connect_param = self.jdbcUtil.get_config_data()
        return self.jdbcObject.connect_jdbc(connect_param)
    
    def execute(self, conn, query, flag):
        if conn == None:
            raise ConnectException("connection이 없습니다.")

        try:
            result = self.jdbcObject.execute(conn, query, flag)
        except Exception as e:
            raise e  
        return result
    
    def execute_many(self, conn, queryString, values, flag):
        if conn == None:
            raise ConnectException("connection이 없습니다.")

        try:
            result = self.jdbcObject.execute_many(conn, queryString, values, flag)
        except Exception as e:
            raise e  
        return result