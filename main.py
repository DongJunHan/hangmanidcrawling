import lotto_store_crawling
from jaydebeapi import connect

def _convert_to_schema(cursor):
    column_names = [record[0].lower() for record in cursor.description]
    column_and_values = [dict(zip(column_names, record)) for record in cursor.fetchall()]
    print(f"names: {column_names}, value: {column_and_values}")
    # return ExoplanetSchema().load(column_and_values, many=True)
    return column_and_values, column_names

def _execute(query, flag=False):
    conn = connect(jclassname="org.h2.Driver",
                           url="jdbc:h2:tcp://localhost/~/test",
                           driver_args=["sa", ""],jars=['/Users/handongjun/Downloads/h2/bin/h2-1.4.200.jar'])
    cursor = conn.cursor()
    cursor.execute(query)
    # cursor.execute("SELECT * FROM MEMBER where member_id='member'")
    # cursor.execute("select * from member")
    if flag:
        name, value = _convert_to_schema(cursor)
    cursor.close()
    conn.close()
if __name__ == "__main__":

    parse_store = lotto_store_crawling.ParseStore()
    parse_store.getStoreData()
    # parse_store.test()
    

    # print(cursor.fetchall())
