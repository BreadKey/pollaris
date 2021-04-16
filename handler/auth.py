from auth.model import *
from handler import needData, request, response
from auth import service, error, CONSTRAINTS
import json

@needData
def signUp(event, cotext):
    data = request.getData(event)
    data["roles"] = list(map(lambda name: Role(name), data["roles"]))

    password = data["password"]
    data.pop("password")

    try:
        service.signUp(User(**data), password)
        return response.created()

    except error.ConflictIdError:
        return response.badRequest("Conflict id")
    except error.ConflictNicknameError:
        return response.badRequest("Conflict nickname")
    except AssertionError as e:
        return response.badRequest(e.__str__())


def getConstraints(event, context):
    return response.ok(json.dumps(CONSTRAINTS.__dict__))
