
import os

import pymysql

POLLARIS_DB = pymysql.connect(
    host=os.environ.get("host", "localhost"),
    user=os.environ.get("user", "root"),
    port=int(os.environ.get("port", 3306)),
    passwd=os.environ.get("password", ""),
    db=os.environ.get("database", "pollaris")
)
