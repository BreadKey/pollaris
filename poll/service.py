from poll.model import *
from poll import repository, error


def createPoll(poll: Poll) -> Poll:

    return repository.createPoll(poll)


def answer(answer: Answer):
    try:
        repository.createAnswer(answer)
    except:
        raise error.AlreadyAnsweredError


def page(fromId: int, count: int) -> List[Poll]:
    return repository.orderByDescFrom(fromId, count)
