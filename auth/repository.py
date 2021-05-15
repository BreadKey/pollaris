import os
from datetime import datetime, timedelta
from typing import List, Type

import pymysql
from pymysql.cursors import DictCursor
from db import POLLARIS_DB, querybuilder
from db.querybuilder import Expression

from auth.model import (AuthRecord, IdentifyMethod, Identity,
                        IdentityChallenge, Role, User, VerificationCode,
                        VerificationLog)

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
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(querybuilder.select(
            User, fields=__USER_FIELDS, where=[Expression("id", id)]))

        return __userFromRow(cursor.fetchone(), cursor)


def findUserByIdAndPassword(id: str, password: str) -> User:
    with POLLARIS_DB.cursor(DictCursor) as cursor:
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


def saveAuthRecord(record: AuthRecord):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.insert(AuthRecord, record.__dict__,
                                           onDuplicate=Expression("dateTime", record.dateTime)))
    POLLARIS_DB.commit()


def findAuthRecordByUserId(userId: str) -> AuthRecord:
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(querybuilder.select(
            AuthRecord, where=[Expression("userId", userId)]))

        row = cursor.fetchone()
        return AuthRecord(**row) if row else None


def removeAuthRecordByUserId(userId: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.delete(
            AuthRecord, where=[Expression("userId", userId)]))
    POLLARIS_DB.commit()


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
            f'drop event if exists {__buildRemoveEventName(VerificationCode, userId)}')

        query = ""
        if (after):
            query += f'create event if not exists {__buildRemoveEventName(VerificationCode, userId)} ' + \
                f'on schedule at date_add(now(), interval {after.seconds} second) do '

        query += querybuilder.delete(VerificationCode,
                                     where=[Expression("userId", userId)])

        cursor.execute(query)

    POLLARIS_DB.commit()


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
    with POLLARIS_DB.cursor(DictCursor) as cursor:
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
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(
            querybuilder.select(VerificationCode,
                                where=[Expression("userId", userId),
                                       Expression("code", code)],
                                encrypt={"code": __ENCRYPT_METHOD}))

        row = cursor.fetchone()
        if (row):
            return VerificationCode(**row)


def saveIdentity(identity: Identity):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.insert(
            Identity, identity.__dict__, onDuplicate=Expression("key", identity.key)))

    POLLARIS_DB.commit()


def findIdentityKeyByUserIdAndMethod(userId: str, method: IdentifyMethod) -> str:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.select(Identity, ["key"],
                                           where=[
            Expression("userId", userId),
            Expression("method", method)
        ]))

        return cursor.fetchone()[0]


def saveIdentityChallenge(challenge: IdentityChallenge):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            querybuilder.insert(IdentityChallenge,
                                challenge.__dict__,
                                encrypt={"value": __ENCRYPT_METHOD},
                                onDuplicate=Expression("value", challenge.value)))

    POLLARIS_DB.commit()


def hasIdentityChallenge(userId: str, value: str) -> bool:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.select(IdentityChallenge, where=[
            Expression("userId", userId),
            Expression("value", value)
        ], encrypt={"value": __ENCRYPT_METHOD}))

        return cursor.fetchone() is not None


def removeIdentityChallenge(userId: str, after: timedelta = None):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'drop event if exists {__buildRemoveEventName(IdentityChallenge, userId)}')
        query = ""
        if (after):
            query += f'create event if not exists {__buildRemoveEventName(IdentityChallenge, userId)} ' + \
                f'on schedule at date_add(now(), interval {after.seconds} second) do '

        query += querybuilder.delete(IdentityChallenge,
                                     where=[Expression("userId", userId)])

        cursor.execute(query)

    POLLARIS_DB.commit()


def __buildRemoveEventName(
    model: Type, userId: str) -> str: return f'remove{model.__name__}Of{userId}'
