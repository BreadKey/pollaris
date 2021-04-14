class __Constraints:
    def __init__(self, minIdLength: int, maxIdLength: int, minNicknameLength: int, maxNicknameLength: int):
        self.minIdLength = minIdLength
        self.maxIdLength = maxIdLength
        self.minNicknameLength = minNicknameLength
        self.maxNicknameLength = maxNicknameLength


CONSTRAINTS = __Constraints(5, 20, 3, 10)
