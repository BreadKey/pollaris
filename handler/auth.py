from auth.model import *
from handler import needData, request, response
from auth import Auth, service, error, CONSTRAINTS
import json


@needData
def signUp(event, cotext):
    data = request.getData(event)
    data["roles"] = [Role(name) for name in data["roles"]]
    data["isVerified"] = False

    password = data.pop("password")

    try:
        service.signUp(User(**data), password)
        return response.created()

    except error.ConflictIdError:
        return response.badRequest("Conflict id")
    except error.ConflictNicknameError:
        return response.badRequest("Conflict nickname")
    except AssertionError as err:
        return response.badRequest(err.__str__())


@needData
def signIn(event, context):
    data = request.getData(event)

    result = service.signIn(data["id"], data["password"])
    if (result):
        return response.ok(result.__dict__)

    return response.unauthorized()


def getConstraints(event, context):
    return response.ok(CONSTRAINTS.__dict__)


def authorizeUser(event, context):
    try:
        auth = __getAuth(event)
        userId = service.authorize(auth, Role.User)
        return __generatePolicy(userId, 'Allow', event['methodArn'])

    except:
        raise Exception("Unauthorized")


@needData
def requestVerificationCode(event, context):
    data = request.getData(event)

    userId = data["userId"]
    phoneNumber = data["phoneNumber"]

    try:
        service.requestVerificationCode(userId, phoneNumber)

        return response.ok()
    except AssertionError as err:
        return response.badRequest(err.__str__())


@needData
def verifyIdentity(event, context):
    data = request.getData(event)

    userId = data["userId"]
    code = data["code"]

    try:
        service.verifyIdentity(userId, code)

        return response.ok()
    except AssertionError as err:
        return response.badRequest(err.__str__())


def authorizeVerifiedUser(event, context):
    try:
        auth = __getAuth(event)
        userId = service.authorize(auth, Role.User, True)

        return __generatePolicy(userId, 'Allow', event['methodArn'])

    except error.NotVerifiedError as err:
        userId = err.args[0]
        policy = __generatePolicy(userId, 'Deny', event['methodArn'])

        return policy

    except:
        raise Exception("Unauthorized")


@needData
def registerIdentity(event, context):
    data = request.getData(event)

    userId = data["userId"]
    method = IdentifyMethod(data["method"])
    key = data["key"]

    service.registerIdentity(Identity(userId, method, key))

    return response.created()


@needData
def getNewIdentityChallenge(event, context):
    data = request.getData(event)

    userId = data["userId"]

    return response.ok({"challenge": service.getNewIdentityChallenge(userId)})


def authorizeWithIdentity(event, context):
    try:
        auth = __getAuth(event)
        userId = service.authorizeWithIdentity(auth.accessToken)

        return __generatePolicy(userId, "Allow", event["methodArn"])

    except:
        raise Exception("Unauthorized")


def __getAuth(event: dict) -> Auth:
    token: str = event.get("authorizationToken")

    parts = token.split(' ')
    method = parts[0]
    accessToken = parts[1]

    assert method.lower() == "bearer"

    return Auth(accessToken, event.get("refreshToken"))


def __generatePolicy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }
    }
