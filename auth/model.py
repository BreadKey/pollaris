from enum import Enum
from typing import List


class Role(Enum):
    User = "User"
    Admin = "Admin"


class User:
    def __init__(self, id: str, nickname: str, hasIdentity: bool, roles: List[Role]):
        self.id = id
        self.nickname = nickname
        self.hasIdentity = hasIdentity
        self.roles = roles

    def fromJson(json):
        json["roles"] = list(map(lambda name: Role(name), json["roles"]))
        return User(**json)

    def toJson(self) -> dict:
        json = self.__dict__
        json["roles"] = list(map(lambda role: role.name, self.roles))

        return json
