import base64
import json
import os
from datetime import datetime, timedelta
from getpass import getpass
from typing import List

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

UTF8 = 'utf-8'

with open("secret/dev.json", 'r') as jsonFile:
    secret = json.load(jsonFile)

HOST = "https://" + secret["domain"] + "/dev"

LAST_TOKENS: dict = {}

try:
    with open("local/data.json", 'r') as jsonFile:
        localData: dict = json.load(jsonFile)

        LAST_TOKENS["accessToken"] = localData.get("accessToken")

except:
    os.mkdir("local")
    with open("local/data.json", 'w') as jsonFile:
        jsonFile.write("{}")
        localData = {}


def signUp():
    id = input("Id: ")
    nickname = input("Nickname: ")
    role = input("Role(User): ")
    role = role if role else "User"
    password = getpass("Password: ")
    response = requests.post(HOST + "/signUp", data=json.dumps(
        {"id": id, "password": password, "nickname": nickname, "roles": [role]}))

    assert response.status_code == 201, response.status_code


def signIn():
    id = input("Id: ")
    password = getpass("Password: ")
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

    print(response.json())


def getNewIdentityChallenge(userId: str) -> str:
    response = requests.get(
        HOST + "/auth/challenge", headers=__buildAuthHeader(), params={"userId": userId})

    assert response.status_code == 200, response.json()

    challenge = response.json()["challenge"]

    return challenge


def createPoll(userId: str, question: str, options: List[str]):
    response = requests.post(
        HOST + "/poll", headers=__buildAuthHeader(), data=json.dumps({
            "userId": userId,
            "question": question,
            "options": [{"index": index, "body": option} for index, option in enumerate(options)]
        }))

    assert response.status_code == 201, response.json()


def answer(userId: str, pollId: int, index: int):
    response = requests.post(HOST + "/answer", headers=__buildIdentityHeader(userId), data=json.dumps({
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


def registerIdentity(userId: str):
    decryptKey = RSA.generate(1024)
    encryptKey = decryptKey.publickey()

    response = requests.post(HOST + "/auth/identity", headers=__buildAuthHeader(), data=json.dumps({
        "userId": userId,
        "method": "Fingerprint",
        "key": decryptKey.exportKey().decode(UTF8)
    }))

    assert response.status_code == 201, response.json()

    localData["identityKey"] = encryptKey.exportKey().decode(UTF8)
    with open("local/data.json", 'w') as jsonFile:
        jsonFile.write(json.dumps(localData))


def __buildAuthHeader():
    return {"Authorization": "bearer " + LAST_TOKENS.get("accessToken", "")}


def __buildIdentityHeader(userId: str):
    challenge = getNewIdentityChallenge(userId)

    encryptKey = RSA.importKey(localData.get("identityKey").encode(UTF8))

    cipher = PKCS1_OAEP.new(encryptKey)

    content = {
        "userId": userId,
        "method": "Fingerprint",
        "challenge": base64.encodebytes(cipher.encrypt(challenge.encode(UTF8))).decode(UTF8)
    }

    return {"Authorization": "bearer " + base64.b64encode(json.dumps(content).encode(UTF8)).decode(UTF8)}
