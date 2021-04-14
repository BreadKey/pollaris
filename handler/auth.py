from auth.model import *
from handler import request, response
from auth import service, error


def signUp(event, cotext):
    data = request.getData(event)
    data["roles"] = list(map(lambda name: Role(name), data["roles"]))

    password = data["password"]
    data.pop("password")

    try:
        service.signUp(User(**data), password)
        return response.created()

    except error.ConflictIdError:
        return response.badRequest("Conflict Id")
    except error.ConflictNicknameError:
        return response.badRequest("Conflict Nickname")
