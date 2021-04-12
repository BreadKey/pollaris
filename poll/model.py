from typing import List


class Option:
    def __init__(self, pollId: int, index: int, body: str, count: int):
        self.pollId = pollId
        self.index = index
        self.body = body
        self.count = count


class Poll:
    def __init__(self, userId: str, question: str, options: List[Option], id: int = 0):
        self.userId = userId
        self.question = question
        self.id = id
        self.options = options

    def toJson(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "question": self.question,
            "options": list(map(lambda option: option.__dict__, self.options))
        }


class Answer:
    def __init__(self, userId: str, option: Option):
        self.userId = userId
        self.option = option
