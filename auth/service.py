from datetime import timedelta
import os
import random
from hashlib import sha256

from pymysql.err import IntegrityError

from auth import CONSTRAINTS, error, repository
from auth.model import *

import re

__SALT = os.environ.get("salt", "some salt")
__STAGE = os.environ.get("stage", "dev")


def signUp(user: User, password: str):
    assert len(user.id) in range(CONSTRAINTS.minIdLength,
                                 CONSTRAINTS.maxIdLength), f"Id length not in range {CONSTRAINTS.minIdLength} ~ {CONSTRAINTS.maxIdLength}"
    assert re.fullmatch(
        CONSTRAINTS.idRegex, user.id) is not None, f"Id not match pattern {CONSTRAINTS.idRegex}"

    assert len(user.nickname) in range(CONSTRAINTS.minNicknameLength,
                                       CONSTRAINTS.maxNicknameLength), f"Nickname length not in range {CONSTRAINTS.minNicknameLength} ~ {CONSTRAINTS.maxNicknameLength}"

    user.hasIdentity = False

    if user.roles is None or len(user.roles) == 0:
        user.roles = [Role.User]

    try:
        return repository.createUser(user, crypt(password, __SALT))
    except IntegrityError as e:
        message: str = e.args[1]

        entry = message.split("'")[-2]

        if (entry.find("nickname") != -1):
            raise error.ConflictNicknameError

        raise error.ConflictIdError


def signIn(id: str, password: str) -> bool:
    return repository.findUserByIdAndPassword(id, crypt(password, __SALT)) is not None


def requestVerifyIdentity(userId: str, phoneNumber: str):
    user = repository.findUserById(userId)
    assert user is not None, "Invalid user"

    cryptedPhoneNumber = crypt(phoneNumber, __SALT)

    assert not __didUserVerifyWithPhoneNumber(
        user, cryptedPhoneNumber), "Already verified user"
    assert not repository.hasVerificationCode(
        cryptedPhoneNumber), "Already requested"

    code = __generateVerificationCode()
    cryptedCode = crypt(code, __SALT)

    repository.setHasIdentity(userId, False)
    repository.createVerificationCode(userId, cryptedPhoneNumber, cryptedCode)
    repository.removeVerifiactionCode(userId,
                                      timedelta(minutes=CONSTRAINTS.responseWatingMinutes))

    __sendVerificationCode(phoneNumber, code)


def __didUserVerifyWithPhoneNumber(user: User, cryptedPhoneNumber: str) -> bool:
    lastLog = repository.findLastVerificationLogByPhoneNumber(
        cryptedPhoneNumber)

    return user.hasIdentity and lastLog and lastLog.userId == user.id


def __generateVerificationCode() -> str:
    return "".join(
        map(
            lambda _: str(random.randrange(0, 10)),
            range(0, CONSTRAINTS.verificationCodeDigit)))


def __sendVerificationCode(phoneNumber: str, code: str):
    if (__STAGE == "prod"):
        pass
    else:
        print(code)


def verifyIdentity(userId: str, code: str):
    cryptedCode = crypt(code, __SALT)

    verificationCode = repository.findVerificationCodeByUserIdAndCode(
        userId, cryptedCode)

    assert verificationCode, "Incorrect code"

    lastLogWithPhoneNumber = repository.findLastVerificationLogByPhoneNumber(
        verificationCode.phoneNumber, encrypt=False)

    if (lastLogWithPhoneNumber and lastLogWithPhoneNumber.userId != userId):
        repository.setHasIdentity(lastLogWithPhoneNumber.userId, False)

    repository.createVerificationLog(userId)
    repository.removeVerifiactionCode(userId)
    repository.setHasIdentity(userId, True)


def crypt(word: str, salt: str) -> str:
    return sha256(str(word + salt).encode('utf-8')).hexdigest()
