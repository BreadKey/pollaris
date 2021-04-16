from dataclasses import dataclass
from typing import List


@dataclass
class Option:
    pollId: int
    index: int
    body: str
    count: int

@dataclass
class Poll:
    userId: str
    question: str
    options: List[Option]
    id: int = 0

    def toJson(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "question": self.question,
            "options": list(map(lambda option: option.__dict__, self.options))
        }


@dataclass
class Answer:
    userId: str
    option: Option