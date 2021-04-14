from auth.model import *
from handler import request, response
from auth import service, error, CONSTRAINTS
import json


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
    except AssertionError as e:
        return response.badRequest(e.__str__())


def getConstraints(event, context):
    return response.ok(json.dumps(CONSTRAINTS.__dict__))
