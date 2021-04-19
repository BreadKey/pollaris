from handler import response
import requests
import json
from auth.model import *

with open("secret/dev.json") as jsonFile:
    secret = json.load(jsonFile)

HOST = "https://" + secret["domain"] + "/dev"

LAST_TOKENS: dict = {}

def signUp(id: str, nickname: str, password: str, role: Role = Role.User):
    response = requests.post(HOST + "/signUp", data=json.dumps(
        {"id": id, "password": password, "nickname": nickname, "roles": [role.name]}))

    assert response.status_code == 201, response.status_code


def signIn(id: str, password: str):
    response = requests.post(
        HOST + "/signIn", data=json.dumps({"id": id, "password": password}))

    assert response.status_code == 200, response.status_code
    LAST_TOKENS["accessToken"] = response.json()["accessToken"]

def page():
    response = requests.get(HOST + "/poll", headers={"Authorization": "bearer " + LAST_TOKENS.get("accessToken", "")})

    print(response.status_code)
    print(response.json())

def answer(userId: str, pollId: int, index: int):
    response = requests.post(HOST + "/answer", headers={"Authorization": "bearer " + LAST_TOKENS.get("accessToken", "")}, data=json.dumps({
        "userId": userId,
        "option": {
            "pollId": pollId,
            "index": index,
            "body": ""
        }
    }))

    assert response.status_code == 200, response.json()