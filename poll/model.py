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
    userAnswerAt: int = None

    def toJson(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "question": self.question,
            "options": [option.__dict__ for option in self.options],
            "userAnswerAt": self.userAnswerAt
        }


@dataclass
class Answer:
    userId: str
    option: Option
    dateTime: datetime = None

@dataclass
class PollSubscription:
    pollId: int
    connectionId: str