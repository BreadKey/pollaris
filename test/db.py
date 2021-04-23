import pymysql, os
from collections import deque


TEST_DB = pymysql.connect(
    host="localhost",
    user="root",
    port=3306,
    passwd=""
)
TEST_DB_NAME = "pollaris_test"
TEST_DB_VERSION = 1

def setUp():
    with TEST_DB.cursor() as cursor:
        cursor.execute("drop database if exists " + TEST_DB_NAME)
        cursor.execute("create database " + TEST_DB_NAME)
        cursor.execute("use " + TEST_DB_NAME)
        with open(f"db/v{TEST_DB_VERSION}.sql", 'r') as sqlFile:
            sql = sqlFile.read()

        requests = deque(sql.split(';'))
        requests.popleft() # pop create database
        requests.popleft() # pop use database

        for request in requests:
            if (request):
                cursor.execute(request)
    TEST_DB.commit()
    os.environ["database"] = TEST_DB_NAME

def tearDown():
    with TEST_DB.cursor() as cursor:
        cursor.execute("drop database " + TEST_DB_NAME)
    TEST_DB.commit()