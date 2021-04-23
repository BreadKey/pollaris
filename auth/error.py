class ConflictIdError(Exception):
    pass

class ConflictNicknameError(Exception):
    pass

class InvalidAuthError(Exception):
    pass

class ExpiredAuthError(Exception):
    pass

class NotVerifiedError(Exception):
    pass

class NotGrantedError(Exception):
    pass