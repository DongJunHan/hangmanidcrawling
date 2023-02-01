from jaydebeapi import connect

def _convert_to_schema(cursor):
    column_names = [record[0].lower() for record in cursor.description]
    column_and_values = [dict(zip(column_names, record)) for record in cursor.fetchall()]
    print(f"names: {column_names}, value: {column_and_values}")
    # return ExoplanetSchema().load(column_and_values, many=True)
    return column_and_values

def execute(query, selectFlag=False):
    """
        Args: 
            query: str
            selectFlag: bool #select시 나오는 결과 데이터를 받기 위함.
        Return
            list
    """
    result = None
    conn = connect(jclassname="org.h2.Driver",
                           url="jdbc:h2:tcp://localhost/~/test",
                           driver_args=["sa", ""],jars=['/Users/handongjun/Downloads/h2/bin/h2-1.4.200.jar'])
    cursor = conn.cursor()
    cursor.execute(query)
    # cursor.execute("SELECT * FROM MEMBER where member_id='member'")
    # cursor.execute("select * from member")
    if selectFlag:
        result = _convert_to_schema(cursor)

    cursor.close()
    conn.close()
    return result