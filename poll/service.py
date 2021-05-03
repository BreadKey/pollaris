from pymysql.constants import ER
from pymysql.err import IntegrityError

from poll import CONSTRAINTS, error, repository
from poll.model import *


def createPoll(poll: Poll) -> Poll:
    assert len(poll.question) in range(
        1, CONSTRAINTS.maxQuestionLength), f"Question length not in range 1 ~ {CONSTRAINTS.maxQuestionLength}"

    assert len(poll.options) in range(CONSTRAINTS.minOptionCount,
                                      CONSTRAINTS.maxOptionCount), f"Option count not in range {CONSTRAINTS.minOptionCount} ~ {CONSTRAINTS.maxOptionCount}"

    for option in poll.options:
        assert len(option.body) in range(
            1, CONSTRAINTS.maxOptionBodyLength), f"Body length at option {option.index} not in rage 1 ~ {CONSTRAINTS.maxOptionBodyLength}"

    return repository.createPoll(poll)


def answer(answer: Answer) -> Poll:
    try:
        repository.createAnswer(answer)
        poll = repository.findPollById(answer.option.pollId)
        poll.hasUserAnswer = True
        return poll
    except IntegrityError as err:
        if err.args[0] == ER.NO_REFERENCED_ROW_2:
            raise error.PollNotExistError
        raise error.AlreadyAnsweredError


def page(fromId: int, count: int, userId: str) -> List[Poll]:
    polls = repository.orderByDescFrom(fromId, count)
    repository.mergeHasUserAnswer(polls, userId)
    return polls


def subscribe(pollId: int, connectionId: str):
    repository.createSubscpriotn(PollSubscription(pollId, connectionId))


def unsubscribe(connectionId: str):
    repository.removeSubscriptionByConnectionId(connectionId)


def findSubscriptionsById(pollId: int) -> List[PollSubscription]:
    return repository.findSubscriptionsById(pollId)
