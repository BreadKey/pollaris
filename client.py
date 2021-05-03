import base64
import json
import os
from getpass import getpass

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import json

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

    assert response.status_code == 200, response.json()
    LAST_TOKENS["accessToken"] = response.json()["accessToken"]
    localData["accessToken"] = LAST_TOKENS["accessToken"]

    with open("local/data.json", 'w') as jsonFile:
        jsonFile.write(json.dumps(localData))


def getMe():
    response = requests.get(HOST + "/auth", headers=__buildAuthHeader())

    response.encoding = 'utf8mb4'
    assert response.status_code == 200, response.json()

    print(response.json())


def refreshAuth():
    response = requests.put(HOST + "/auth", headers=__buildAuthHeader())

    assert response.status_code == 200, response.json()
    LAST_TOKENS["accessToken"] = response.json()["accessToken"]
    localData["accessToken"] = LAST_TOKENS["accessToken"]

    with open("local/data.json", "w") as jsonFile:
        jsonFile.write(json.dumps(localData))


def signOut():
    response = requests.delete(HOST + "/auth", headers=__buildAuthHeader())

    assert response.status_code == 200, response.json()


def page():
    response = requests.get(
        HOST + "/poll", headers=__buildAuthHeader())

    response.encoding = 'utf8mb4'
    assert response.status_code == 200, response.json()

    print(json.loads((response.json())))


def getNewIdentityChallenge(userId: str) -> str:
    response = requests.get(
        HOST + "/auth/challenge", headers=__buildAuthHeader(), params={"userId": userId})

    assert response.status_code == 200, response.json()

    challenge = response.json()["challenge"]

    return challenge


def createPoll(userId: str):
    question = input("question: ")

    options = []
    index = 0
    while True:
        option = input(f"Option{index + 1}: ")
        if (option):
            options.append({"index": index, "body": option})
            index += 1
        else:
            break

    response = requests.post(
        HOST + "/poll", headers=__buildAuthHeader(), data=json.dumps({
            "userId": userId,
            "question": question,
            "options": options
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

    response.encoding = 'utf8mb4'
    assert response.status_code == 200, response.json()

    print(response.json())


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
