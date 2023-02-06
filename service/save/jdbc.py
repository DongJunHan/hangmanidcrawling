from jaydebeapi import connect
# import pymysql
import yaml
import os

def _convert_to_schema(cursor):
    column_names = [record[0].lower() for record in cursor.description]
    column_and_values = [dict(zip(column_names, record)) for record in cursor.fetchall()]
    # return ExoplanetSchema().load(column_and_values, many=True)
    return column_and_values

def _get_config_data():
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


def execute(query, selectFlag=False):
    """
        Args: 
            query: str
            selectFlag: bool #select시 나오는 결과 데이터를 받기 위함.
        Return
            list
    """
    result = None
    cursor = None
    conn = None
    config = _get_config_data()
    if config == None:
        raise Exception("[ERROR] can't find yaml file")
    try:
        # conn = connect(jclassname=config["jclassname"],
                            #   url=config["url"],
                            #   driver_args=[config["username"], config["password"]],jars=[config["dbjarpath"]])
        conn = pymysql.connect(
	        user=config["username"],
	        password=config["password"],
	        host=config["host"],
	        port=config["port"],
	        database=config["database"],
            charset=config["charset"],
            autocommit=False)
        cursor = conn.cursor()
        cursor.execute(query)
        if selectFlag:
            result = _convert_to_schema(cursor)
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if cursor != None:
            cursor.close()
        if conn != None:
            conn.close()
    return result
