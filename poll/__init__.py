from dataclasses import dataclass

@dataclass
class __Constraints:
    maxQuestionLength: int
    minOptionCount: int
    maxOptionCount: int
    maxOptionBodyLength: int


CONSTRAINTS = __Constraints(100, 2, 5, 30)
