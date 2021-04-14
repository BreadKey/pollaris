from poll.model import *
from poll import repository, error, CONSTRAINTS
from pymysql.err import IntegrityError

def createPoll(poll: Poll) -> Poll:
    assert len(
        poll.question) in range(1, CONSTRAINTS.maxQuestionLength), f"Question length not in range 1 ~ {CONSTRAINTS.maxQuestionLength}"
    assert len(poll.options) in range(CONSTRAINTS.minOptionCount,
                                      CONSTRAINTS.maxOptionCount), f"Option count not in range {CONSTRAINTS.minOptionCount} ~ {CONSTRAINTS.maxOptionCount}"

    for option in poll.options:
        assert len(option.body) in range(
            1, CONSTRAINTS.maxOptionBodyLength), f"Body length at option {option.index} not in rage 1 ~ {CONSTRAINTS.maxOptionBodyLength}"

    return repository.createPoll(poll)


def answer(answer: Answer):
    try:
        repository.createAnswer(answer)
    except IntegrityError:
        raise error.AlreadyAnsweredError


def page(fromId: int, count: int) -> List[Poll]:
    return repository.orderByDescFrom(fromId, count)
