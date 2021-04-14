from pymysql import NULL
from auth.model import *
from auth import CONSTRAINTS, repository
from auth import error
from pymysql.err import IntegrityError
from crypt import crypt
import os

__salt = os.environ.get("salt", "some salt")


def signUp(user: User, password: str):
    assert len(user.id) in range(CONSTRAINTS.minIdLength,
                                 CONSTRAINTS.maxIdLength), f"Id length not in range {CONSTRAINTS.minIdLength} ~ {CONSTRAINTS.maxIdLength}"
    assert len(user.nickname) in range(CONSTRAINTS.minNicknameLength,
                                       CONSTRAINTS.maxNicknameLength), f"Nickname length not in range {CONSTRAINTS.minNicknameLength} ~ {CONSTRAINTS.minNicknameLength}"

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
