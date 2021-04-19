from dataclasses import dataclass


@dataclass
class __Constraints:
    minIdLength: int
    maxIdLength: int
    minNicknameLength: int
    maxNicknameLength: int
    idRegex: str
    verificationCodeDigit: int
    responseWatingMinutes: int
    accessTokenExpireDays: int
    refreshTokenExpireDays: int


CONSTRAINTS = __Constraints(5, 20, 3, 10, r"[a-zA-Z][a-zA-Z0-9]+", 6, 5, 3, 5)


@dataclass
class Auth:
    accessToken: str
    refreashToken: str
