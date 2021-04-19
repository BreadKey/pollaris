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
    hasIdentity: bool
    roles: List[Role]

    def fromJson(json):
        json["roles"] = list(map(lambda name: Role(name), json["roles"]))
        return User(**json)

    def toJson(self) -> dict:
        json = self.__dict__
        json["roles"] = list(map(lambda role: role.name, self.roles))

        return json

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
