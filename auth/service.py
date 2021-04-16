from datetime import timedelta
import os
import random
from crypt import crypt

from pymysql.err import IntegrityError

from auth import CONSTRAINTS, error, repository
from auth.model import *

import re

__salt = os.environ.get("salt", "some salt")


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
        return repository.createUser(user, crypt(password, __salt))
    except IntegrityError as e:
        message: str = e.args[1]

        entry = message.split("'")[-2]

        if (entry.find("nickname") != -1):
            raise error.ConflictNicknameError

        raise error.ConflictIdError


def signIn(id: str, password: str) -> bool:
    return repository.findUserByIdAndPassword(id, crypt(password, __salt)) is not None


def requestVerifyIdentity(userId: str, phoneNumber: str):
    user = repository.findUserById(userId)

    cryptedPhoneNumber = crypt(phoneNumber, __salt)

    assert user is not None, "Invalid user"
    assert not user.hasIdentity, "Already verified user"
    assert not repository.hasVerificationLog(
        cryptedPhoneNumber), "Already verified phone number"
    assert not repository.hasVerificationCode(
        cryptedPhoneNumber), "Already requested"

    code = __generateVerificationCode()
    cryptedCode = crypt(code, __salt)

    repository.createVerificationCode(userId, cryptedPhoneNumber, cryptedCode)
    repository.removeVerifiactionCode(userId,
                                      timedelta(minutes=CONSTRAINTS.responseWatingMinutes))

    __sendVerificationCode(phoneNumber, code)


def __generateVerificationCode() -> str:
    return "".join(
        map(
            lambda _: str(random.randrange(0, 10)),
            range(0, CONSTRAINTS.verificationCodeDigit)))

def __sendVerificationCode(phoneNumber: str, code: str):
    print(code)

def verifyIdentity(userId: str, code: str):
    cryptedCode = crypt(code, __salt)

    assert repository.isCorrectVerificationCode(userId, cryptedCode), "Incorrect code"

    repository.createVerificationLog(userId)
    repository.removeVerifiactionCode(userId)
    repository.setHasIdentity(userId, True)
