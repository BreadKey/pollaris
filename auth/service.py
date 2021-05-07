import base64
import json
import os
import random
import re
import string
from datetime import timedelta
from hashlib import sha256
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

import jwt
from pymysql.err import IntegrityError

from auth import CONSTRAINTS, Auth, error, repository
from auth.model import *

__SALT = os.environ.get("salt", "some salt")
__STAGE = os.environ.get("stage", "dev")
__JWT_KEY = os.environ.get("jwtKey", "jwt key")
__JWT_ALGORITHM = os.environ.get("jwtAlgorithm", "HS256")


def signUp(user: User, password: str):
    assert len(user.id) in range(CONSTRAINTS.minIdLength,
                                 CONSTRAINTS.maxIdLength), f"Id length not in range {CONSTRAINTS.minIdLength} ~ {CONSTRAINTS.maxIdLength}"
    assert re.fullmatch(
        CONSTRAINTS.idRegex, user.id), f"Id not match pattern {CONSTRAINTS.idRegex}"

    assert len(user.nickname) in range(CONSTRAINTS.minNicknameLength,
                                       CONSTRAINTS.maxNicknameLength), f"Nickname length not in range {CONSTRAINTS.minNicknameLength} ~ {CONSTRAINTS.maxNicknameLength}"

    user.isVerified = False

    if not user.roles:
        user.roles = [Role.User]

    try:
        return repository.createUser(user, crypt(password, __SALT))
    except IntegrityError as e:
        message: str = e.args[1]

        entry = message.split("'")[-2]

        if (entry.find("nickname") != -1):
            raise error.ConflictNicknameError

        raise error.ConflictIdError


def signIn(id: str, password: str) -> Auth:
    if repository.findUserByIdAndPassword(id, crypt(password, __SALT)):
        return __publishAuth(id)

    return None

def getMe(id: str) -> User:
    return repository.findUserById(id)

def refreshAuth(userId: str) -> Auth:
    return __publishAuth(userId)


def __publishAuth(userId: str) -> Auth:
    now = datetime.utcnow().replace(microsecond=0)
    payload = {
        "userId": userId,
        "exp": now + timedelta(days=CONSTRAINTS.accessTokenExpireDays)
    }

    accessToken = jwt.encode(payload, __JWT_KEY, __JWT_ALGORITHM)

    repository.saveAuthRecord(AuthRecord(userId, now))

    return Auth(accessToken)

def signOut(userId: str):
    repository.removeAuthRecordByUserId(userId)

def requestVerificationCode(userId: str, phoneNumber: str):
    phoneNumber = re.sub(r"-| ", '', phoneNumber)

    assert re.fullmatch(CONSTRAINTS.phoneNumberRegex,
                        phoneNumber), f"Phone number not match pattern {CONSTRAINTS.phoneNumberRegex}"

    user = repository.findUserById(userId)
    assert user, "Invalid user"

    cryptedPhoneNumber = crypt(phoneNumber, __SALT)

    assert not __isVerifiedUser(
        user, cryptedPhoneNumber), "Already verified user"

    assert not repository.hasVerificationCode(
        cryptedPhoneNumber), "Already requested"

    code = __generateVerificationCode()
    cryptedCode = crypt(code, __SALT)

    __sendVerificationCode(phoneNumber, code)
    repository.setVerified(userId, False)
    repository.createVerificationCode(userId, cryptedPhoneNumber, cryptedCode)
    repository.removeVerifiactionCode(userId,
                                      timedelta(minutes=CONSTRAINTS.responseWatingMinutes))


def __isVerifiedUser(user: User, cryptedPhoneNumber: str) -> bool:
    lastLog = repository.findLastVerificationLogByPhoneNumber(
        cryptedPhoneNumber)

    return user.isVerified and lastLog and lastLog.userId == user.id


def __generateVerificationCode() -> str:
    return "".join(
        [str(random.randrange(0, 10)) for _ in
            range(0, CONSTRAINTS.verificationCodeDigit)])


def __sendVerificationCode(phoneNumber: str, code: str):
    if (__STAGE != "local"):
        import boto3
        import logging

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        sns = boto3.client('sns', os.environ.get(
            'snsRegion', 'ap-northeast-1'))
        sns.publish(
            PhoneNumber=phoneNumber,
            Message=__buildVeirificationCodeMessage(code),
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'Pollaris'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
    else:
        print(code)


def __buildVeirificationCodeMessage(code: str):
    return f"[Pollaris] 인증번호 [{code}]를 입력해주세요."


def verifyIdentity(userId: str, code: str):
    cryptedCode = crypt(code, __SALT)

    verificationCode = repository.findVerificationCodeByUserIdAndCode(
        userId, cryptedCode)

    assert verificationCode, "Incorrect code"

    lastLogWithPhoneNumber = repository.findLastVerificationLogByPhoneNumber(
        verificationCode.phoneNumber, encrypt=False)

    if (lastLogWithPhoneNumber and lastLogWithPhoneNumber.userId != userId):
        repository.setVerified(lastLogWithPhoneNumber.userId, False)

    repository.createVerificationLog(userId)
    repository.removeVerifiactionCode(userId)
    repository.setVerified(userId, True)


def crypt(word: str, salt: str) -> str:
    return sha256(str(word + salt).encode('utf-8')).hexdigest()


def authorize(auth: Auth, role: Role = None, needVerification: bool = False) -> str:
    try:
        payload = jwt.decode(auth.accessToken, __JWT_KEY,
                             options={"verify_exp": True},
                             algorithms=[__JWT_ALGORITHM])

        userId = payload["userId"]
        if (needVerification or role):
            user = repository.findUserById(userId)

            if needVerification and not user.isVerified:
                raise error.NotVerifiedError(userId)

            if role and not role in user.roles:
                raise error.NotGrantedError(userId)

        lastRecord = repository.findAuthRecordByUserId(userId)

        if lastRecord:
            exp = datetime.fromtimestamp(payload["exp"])
            if exp - timedelta(days=CONSTRAINTS.accessTokenExpireDays) != lastRecord.dateTime:
                raise error.ExpiredAuthError
        else:
            raise error.ExpiredAuthError

        return userId

    except (jwt.InvalidAlgorithmError, jwt.InvalidSignatureError):
        raise error.InvalidAuthError
    except jwt.ExpiredSignatureError:
        raise error.ExpiredAuthError


def registerIdentity(identity: Identity):
    repository.saveIdentity(identity)


def getNewIdentityChallenge(userId: str) -> str:
    challenge = "".join(random.choices(
        string.ascii_lowercase + string.digits, k=8))
    repository.saveIdentityChallenge(
        IdentityChallenge(userId, crypt(challenge, __SALT)))
    repository.removeIdentityChallenge(userId,
                                       after=timedelta(seconds=CONSTRAINTS.challengeHoldingSeconds))
    return challenge


def authorizeWithIdentity(rawToken: str) -> str:
    try:
        content = json.loads(base64.b64decode(rawToken).decode('utf-8'))
        userId = content["userId"]
        method = content["method"]
        challenge = content["challenge"]

        key = repository.findIdentityKeyByUserIdAndMethod(
            userId, IdentifyMethod(method))

        decryptKey = RSA.importKey(key.encode('utf-8'))

        cipher = PKCS1_OAEP.new(decryptKey)

        challengeBytes = base64.decodebytes(
            challenge.encode('utf-8'))

        decryptedChallenge = cipher.decrypt(challengeBytes).decode('utf-8')

        if (repository.hasIdentityChallenge(userId, crypt(decryptedChallenge, __SALT))):
            repository.removeIdentityChallenge(userId)
            return userId

        raise error.InvalidAuthError

    except:
        raise error.InvalidAuthError
