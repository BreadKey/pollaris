import os
from db import POLLARIS_DB
from auth.model import Role, User
import pymysql
from datetime import datetime, timedelta

__encrypt = os.environ.get("encrypt", "MD5")

__SELECT_USER = "select id, nickname, hasIdentity from Users"


def createUser(user: User, password: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'insert into Users(id, password, nickname, hasIdentity) values("{user.id}", {__encrypt}("{password}"), "{user.nickname}", {int(user.hasIdentity)})')
        for role in user.roles:
            cursor.execute(
                f'insert into Roles(userId, name) values("{user.id}", "{role.name}")')

    POLLARIS_DB.commit()


def findUserById(id: str) -> User:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            f'{__SELECT_USER} where id = "{id}"')

        return __userFromRow(cursor.fetchone(), cursor)


def findUserByIdAndPassword(id: str, password: str) -> User:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            f'{__SELECT_USER} where id = "{id}" and password = {__encrypt}("{password}")')

        return __userFromRow(cursor.fetchone(), cursor)


def __userFromRow(userRow: dict, cursor: pymysql.cursors.Cursor) -> User:
    if (userRow is None):
        return None

    cursor.execute(
        f'select name from Roles where userId = "{userRow["id"]}"')

    roleRows = cursor.fetchall()

    userRow["roles"] = list(map(lambda row: Role(row["name"]), roleRows))

    return User(**userRow)


def hasVerificationLog(phoneNumber: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'select * from VerificationLogs where phoneNumber = {__encrypt}("{phoneNumber}")')

        return cursor.fetchone() is not None


def hasVerificationCode(phoneNumber: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'select * from VerificationCodes where phoneNumber = {__encrypt}("{phoneNumber}")')

        return cursor.fetchone() is not None


def createVerificationCode(userId: str, phoneNumber: str, code: str):
    with POLLARIS_DB.cursor() as cursor:
        now = datetime.now()

        cursor.execute(
            f'insert into VerificationCodes(userId, phoneNumber, code, requestDateTime)' +
            f'values("{userId}", {__encrypt}("{phoneNumber}"), {__encrypt}("{code}"), "{now.isoformat()}")'
        )
    POLLARIS_DB.commit()


def removeVerifiactionCode(userId: str, after: timedelta = None):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'drop event if exists {__buildRemoveEventName(userId)}')

        query = ""
        if (after is not None):
            removeDateTime = datetime.now() + after
            query += f'create event if not exists {__buildRemoveEventName(userId)} on schedule at "{removeDateTime.isoformat()}" do '

        query += f'delete from VerificationCodes where userId = "{userId}"'

        cursor.execute(query)

    POLLARIS_DB.commit()


def __buildRemoveEventName(userId: str) -> str: return f'removeCodeOf{userId}'


def isCorrectVerificationCode(userId: str, code: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'select * from VerificationCodes where userId = "{userId}" and code = {__encrypt}("{code}")')

        return cursor.fetchone() is not None


def setHasIdentity(userId: str, hasIdentity: bool):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'update Users set hasIdentity = {int(hasIdentity)} where id = "{userId}"')

    POLLARIS_DB.commit()


def createVerificationLog(userId: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'select phoneNumber from VerificationCodes where userId = "{userId}"')
        encryptedPhoneNumber = cursor.fetchone()[0]
        now = datetime.now()
        cursor.execute(
            f'insert into VerificationLogs(userId, phoneNumber, dateTime) values("{userId}", "{encryptedPhoneNumber}", "{now.isoformat()}")')

    POLLARIS_DB.commit()
