from dataclasses import dataclass
from enum import Enum
from typing import List
from datetime import datetime


class Role(Enum):
    User = "User"
    Admin = "Admin"


@dataclass
class User:
    id: str
    nickname: str
    isVerified: bool
    roles: List[Role]

    def fromJson(json):
        json["roles"] = [Role(name) for name in json["roles"]]
        return User(**json)

    def toJson(self) -> dict:
        json = self.__dict__
        json["roles"] = [role.name for role in self.roles]

        return json


@dataclass
class AuthRecord:
    userId: str
    dateTime: datetime

@dataclass
class VerificationCode:
    id: int
    userId: str
    phoneNumber: str
    code: str
    requestDateTime: datetime


@dataclass
class VerificationLog:
    id: int
    userId: str
    phoneNumber: str
    dateTime: datetime

    def fromJson(json: dict):
        json["dateTime"] = datetime.fromisoformat(json["dateTime"])

        return VerificationLog(**json)


class IdentifyMethod(Enum):
    Password = "Password"
    Pattern = "Pattern"
    Fingerprint = "Fingerprint"


@dataclass
class Identity:
    userId: str
    method: IdentifyMethod
    key: str

@dataclass
class IdentityChallenge:
    userId: str
    value: str