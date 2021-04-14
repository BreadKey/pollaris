import os
from db import POLLARIS_DB
from auth.model import Role, User
import pymysql

__encrypt = os.environ.get("encrypt", "MD5")


def createUser(user: User, password: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'insert into Users(id, password, nickname, hasIdentity) values("{user.id}", {__encrypt}("{password}"), "{user.nickname}", {int(user.hasIdentity)})')
        for role in user.roles:
            cursor.execute(
                f'insert into Roles(userId, name) values("{user.id}", "{role.name}")'
            )
    POLLARIS_DB.commit()


def findUserByIdAndPassword(id: str, password: str) -> User:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            f'select id, nickname, hasIdentity from Users where id = "{id}" and password = {__encrypt}("{password}")'
        )
        userRow = cursor.fetchone()

        if (userRow is None):
            return None

        cursor.execute(
            f'select name from Roles where userId = "{id}"'
        )

        roleRows = cursor.fetchall()

        userRow["roles"] = list(map(lambda row: Role(row["name"]), roleRows))

    return User(**userRow)
