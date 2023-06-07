from jaydebeapi import connect
import pymysql
import yaml
import os
import abc

class Connection(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def connect_jdbc(self, connect_param):
        """
            Args
                connect_param: dict
            Return:
                connect
        """
        raise NotImplemented
    @abc.abstractmethod
    def execute(self, conn, query, selectFlag=False):
        """
            Args: 
                conn: connect
                query: str
                selectFlag: bool #select시 나오는 결과 데이터를 받기 위함.
            Return
                list
        """
        raise NotImplemented
    @abc.abstractmethod
    def execute_many(self, conn, queryString, values, selectFlag=False):
        """
            Args
                conn       : jaydebeapi.connect
                queryString: str ex. select * from table where a = ?
                values     : list
            Return
                list 
        """
        raise NotImplemented

class H2Connection(Connection):
    def connect_jdbc(self, connectParam):
        try:
            conn = connect(jclassname=connectParam["jclassname"],
                            url=connectParam["url"],
                            driver_args=[connectParam["username"], connectParam["password"]],
                            jars=[connectParam["dbjarpath"]])
        except Exception as e:
            raise e
        return conn
    
    def execute(self, conn, query, selectFlag=False):
        result = None
        cursor = None
        dbUtil = DBUtil()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if selectFlag:
                result = dbUtil.convert_to_schema(cursor)
            else:
                result = cursor.rowcount
        except Exception as e:
            raise e
        finally:
            if cursor != None:
                cursor.close()
        return result
    
    def execute_many(self, conn, queryString, values, selectFlag=False):
        """
            Args
                conn       : jaydebeapi.connect
                queryString: str ex. select * from table where a = ?
                values     : list
            Return
                list 
        """
        result = None
        cursor = None
        dbUtil = DBUtil()
        try:
            cursor = conn.cursor()
            cursor.executemany(queryString, values)
            if selectFlag:
                result = dbUtil.convert_to_schema(cursor)
        except Exception as e:
            raise e
        finally:
            if cursor != None:
                cursor.close()
        return result
class MySQLConnection(Connection):
    def connect_jdbc(self, connectParam):
        try:
            conn = pymysql.connect(
	            user=connectParam["username"],
	            password=connectParam["password"],
	            host=connectParam["host"],
	            port=connectParam["port"],
	            database=connectParam["database"],
                charset=connectParam["charset"],
                autocommit=False)
        except Exception as e:
            raise e
        return conn
    
    def execute(self, conn, query, selectFlag=False):
        result = None
        cursor = None
        dbUtil = DBUtil()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if selectFlag:
                result = dbUtil.convert_to_schema(cursor)
        except Exception as e:
            raise e
        finally:
            if cursor != None:
                cursor.close()
        return result
    
    def execute_many(self, conn, queryString, values, selectFlag=False):
        raise Exception("mysql no support")

class DBUtil:
    def convert_to_schema(self, cursor):
        column_names = [record[0].lower() for record in cursor.description]
        column_and_values = [dict(zip(column_names, record)) for record in cursor.fetchall()]
        return column_and_values

    def get_config_data(self):
        config = dict()
        if os.path.isfile("./config/config.yaml"):
            with open("config/config.yaml", "r",encoding="utf-8") as file:
                yaml_object = yaml.load(file,Loader=yaml.FullLoader)
                for key, value in yaml_object.items():
                    config[key] = value
        else:
            print(f"[ERROR] config.yaml 파일이 없습니다. 현재 경로: [{os.getcwd()}]")
            return None
        return config
    
