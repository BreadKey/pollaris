from handler import response
import requests
import json
from auth.model import *

with open("secret/dev.json", 'r') as jsonFile:
    secret = json.load(jsonFile)

HOST = "https://" + secret["domain"] + "/dev"

LAST_TOKENS: dict = {}

with open("local/data.json", 'r') as jsonFile:
    localData: dict = json.load(jsonFile)

    LAST_TOKENS["accessToken"] = localData.get("accessToken")


def signUp(id: str, nickname: str, password: str, role: Role = Role.User):
    response = requests.post(HOST + "/signUp", data=json.dumps(
        {"id": id, "password": password, "nickname": nickname, "roles": [role.name]}))

    assert response.status_code == 201, response.status_code


def signIn(id: str, password: str):
    response = requests.post(
        HOST + "/signIn", data=json.dumps({"id": id, "password": password}))

    assert response.status_code == 200, response.status_code
    LAST_TOKENS["accessToken"] = response.json()["accessToken"]
    localData["accessToken"] = LAST_TOKENS["accessToken"]

    with open("local/data.json", 'w') as jsonFile:
        jsonFile.write(json.dumps(localData))


def page():
    response = requests.get(
        HOST + "/poll", headers=__buildAuthHeader())

    assert response.status_code == 200, response.json()


def getNewIdentityChallenge(userId: str) -> str:
    response = requests.get(
        HOST + "/challenge", headers=__buildAuthHeader(), params={"userId": userId})

    assert response.status_code == 200, response.json()

    challenge = response.json()["challenge"]


def answer(userId: str, pollId: int, index: int):
    challenge = getNewIdentityChallenge(userId)

    response = requests.post(HOST + "/answer", headers=__buildAuthHeader(), data=json.dumps({
        "userId": userId,
        "option": {
            "pollId": pollId,
            "index": index,
            "body": ""
        }
    }))

    assert response.status_code == 200, response.json()


def requestVerificationCode(userId: str, phoneNumber: str):
    response = requests.get(HOST + "/auth/verification",
                            params={"userId": userId, "phoneNumber": phoneNumber}, headers=__buildAuthHeader())

    assert response.status_code == 200, response.json()


def verifyIdentity(userId: str, code: str):
    response = requests.post(HOST + "/auth/verification", headers=__buildAuthHeader(), data=json.dumps({
        "userId": userId,
        "code": code
    }))

    assert response.status_code == 200, response.json()


def __buildAuthHeader():
    return {"Authorization": "bearer " + LAST_TOKENS.get("accessToken", "")}
