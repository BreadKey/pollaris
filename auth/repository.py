import os
from typing import List
from db import POLLARIS_DB, querybuilder
from db.querybuilder import Expression
from auth.model import Identity, Role, User, VerificationCode, VerificationLog
import pymysql
from datetime import datetime, timedelta

__ENCRYPT_METHOD = os.environ.get("encrypt", "MD5")

__USER_FIELDS = ["id", "nickname", "isVerified"]


def createUser(user: User, password: str):
    with POLLARIS_DB.cursor() as cursor:
        data = user.__dict__.copy()
        data["password"] = password

        roles: List[Role] = data.pop("roles")

        cursor.execute(querybuilder.insert(
            User, data, encrypt={"password": __ENCRYPT_METHOD}))

        for role in roles:
            roleData = {"userId": user.id, "name": role.name}
            cursor.execute(querybuilder.insert(Role, roleData))

    POLLARIS_DB.commit()


def findUserById(id: str) -> User:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(querybuilder.select(
            User, fields=__USER_FIELDS, where=[Expression("id", id)]))

        return __userFromRow(cursor.fetchone(), cursor)


def findUserByIdAndPassword(id: str, password: str) -> User:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            querybuilder.select(User, fields=__USER_FIELDS,
                                where=[
                                    Expression("id", id),
                                    Expression("password", password)],
                                encrypt={"password": __ENCRYPT_METHOD}))

        return __userFromRow(cursor.fetchone(), cursor)


def __userFromRow(userRow: dict, cursor: pymysql.cursors.Cursor) -> User:
    if (userRow):
        cursor.execute(
            querybuilder.select(Role, fields=["name"],
                                where=[Expression("userId", userRow["id"])])
        )

        roleRows = cursor.fetchall()

        userRow["roles"] = [Role(row["name"]) for row in roleRows]

        return User(**userRow)


def hasVerificationLog(userId: str, phoneNumber: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.select(VerificationLog,
                                where=[Expression("userId", userId),
                                       Expression("phoneNumber", phoneNumber)],
                                encrypt={"phoneNumber": __ENCRYPT_METHOD}))

        return cursor.fetchone() is not None


def hasVerificationCode(phoneNumber: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.select(VerificationCode,
                                where=[Expression("phoneNumber", phoneNumber)],
                                encrypt={"phoneNumber": __ENCRYPT_METHOD})
        )

        return cursor.fetchone() is not None


def createVerificationCode(userId: str, phoneNumber: str, code: str):
    with POLLARIS_DB.cursor() as cursor:
        now = datetime.utcnow()

        verificationCode = VerificationCode(
            None, userId, phoneNumber, code, now)

        cursor.execute(
            querybuilder.insert(VerificationCode, verificationCode.__dict__, encrypt={
                                "phoneNumber": __ENCRYPT_METHOD, "code": __ENCRYPT_METHOD})
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

        query += querybuilder.delete(VerificationCode,
                                     where=[Expression("userId", userId)])

        cursor.execute(query)

    POLLARIS_DB.commit()


def __buildRemoveEventName(userId: str) -> str: return f'removeCodeOf{userId}'


def isCorrectVerificationCode(userId: str, code: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.select(VerificationCode,
                                where=[Expression("userId", userId),
                                       Expression("code", code)],
                                encrypt={"code": __ENCRYPT_METHOD})
        )

        return cursor.fetchone() is not None


def setVerified(userId: str, isVerified: bool):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.update(
                User, {"isVerified": isVerified}, where=[Expression("id", userId)]))

    POLLARIS_DB.commit()


def createVerificationLog(userId: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.select(VerificationCode, ["phoneNumber"],
                                where=[Expression("userId", userId)])
        )
        encryptedPhoneNumber = cursor.fetchone()[0]
        now = datetime.utcnow()

        log = VerificationLog(None, userId, encryptedPhoneNumber, now)

        cursor.execute(
            querybuilder.insert(VerificationLog, log.__dict__)
        )

    POLLARIS_DB.commit()


def findLastVerificationLogByPhoneNumber(phoneNumber: str, encrypt: bool = True) -> VerificationLog:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            querybuilder.select(VerificationLog,
                                where=[Expression("phoneNumber", phoneNumber)],
                                encrypt={
                                    "phoneNumber": __ENCRYPT_METHOD} if encrypt else None,
                                orderBy=("dateTime", querybuilder.Order.Desc),
                                limit=1))

        row = cursor.fetchone()

        if (row):
            return VerificationLog(**row)


def findVerificationCodeByUserIdAndCode(userId: str, code: str) -> VerificationCode:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            querybuilder.select(VerificationCode,
                                where=[Expression("userId", userId),
                                       Expression("code", code)],
                                encrypt={"code": __ENCRYPT_METHOD}))

        row = cursor.fetchone()
        if (row):
            return VerificationCode(**row)


def hasIdentity(identity: Identity) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.select(Identity,
                                           where=[
                                               Expression(
                                                   "userId", identity.userId),
                                               Expression(
                                                   "method", identity.method),
                                               Expression("value", identity.value)],
                                           encrypt={"value": __ENCRYPT_METHOD}))
