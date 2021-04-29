from dataclasses import dataclass
from datetime import datetime
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
    id: int = None
    hasUserAnswer: bool = False

    def toJson(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "question": self.question,
            "options": [option.__dict__ for option in self.options],
            "hasUserAnswer": self.hasUserAnswer
        }


@dataclass
class Answer:
    userId: str
    option: Option
    dateTime: datetime = None
