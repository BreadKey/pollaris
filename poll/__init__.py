class __Constraints:
    def __init__(self, maxQuestionLength: int, minOptionCount: int, maxOptionCount: int, maxOptionBodyLength: int):
        self.maxQuestionLength = maxQuestionLength
        self.minOptionCount = minOptionCount
        self.maxOptionCount = maxOptionCount
        self.maxOptionBodyLength = maxOptionBodyLength


CONSTRAINTS = __Constraints(100, 2, 5, 30)
