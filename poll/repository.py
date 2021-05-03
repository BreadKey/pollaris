from db import POLLARIS_DB, querybuilder
from db.querybuilder import Expression
from pymysql.cursors import Cursor, DictCursor

from poll.model import *


def createPoll(poll: Poll) -> Poll:
    with POLLARIS_DB.cursor() as cursor:
        pollData = poll.__dict__.copy()
        pollData.pop("options")
        pollData.pop("hasUserAnswer")

        cursor.execute(
            querybuilder.insert(Poll, pollData)
        )
        id = cursor.lastrowid

        for option in sorted(poll.options, key=lambda option: option.index):
            option.count = 0
            option.pollId = id
            cursor.execute(
                querybuilder.insert(Option, option.__dict__)
            )
    POLLARIS_DB.commit()

    return Poll(poll.userId, poll.question, [Option(id, option.index, option.body, 0) for option in poll.options], id)


def findPollById(id: int) -> Poll:
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(querybuilder.select(Poll, where=[Expression("id", id)]))
        row = cursor.fetchone()

        return __pollFromRow(row, cursor)

def createAnswer(answer: Answer):
    with POLLARIS_DB.cursor() as cursor:
        data = {"userId": answer.userId,
                "pollId": answer.option.pollId,
                "index": answer.option.index,
                "dateTime": datetime.utcnow()}
        cursor.execute(
            querybuilder.insert(Answer, data)
        )

        cursor.execute(
            querybuilder.update(
                Option,
                {"count": Expression("count", 1, '+')},
                where=[Expression("pollId", answer.option.pollId),
                       Expression("index", answer.option.index)])
        )
    POLLARIS_DB.commit()


def orderByDescFrom(id: int, count: int) -> List[Poll]:
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(
            querybuilder.select(
                Poll,
                where=[Expression("id", id, "<")] if id else None,
                orderBy=("id", querybuilder.Order.Desc),
                limit=count)
        )

        rows = cursor.fetchall()

        polls = []

        for row in rows:
            polls.append(__pollFromRow(row, cursor))

    return polls

def __pollFromRow(row, cursor: Cursor) -> Poll:
    if row:
        id = row["id"]
        cursor.execute(querybuilder.select(
            Option, where=[Expression("pollId", id)]))
        row["options"] = [Option(**optionRow)
                            for optionRow in cursor.fetchall()]

        return Poll(**row)

    return None

def mergeHasUserAnswer(polls: List[Poll], userId: str):
    with POLLARIS_DB.cursor() as cursor:
        for poll in polls:
            cursor.execute(querybuilder.select(
                Answer, where=[Expression("pollId", poll.id), Expression("userId", userId)]))
            poll.hasUserAnswer = cursor.fetchone() is not None


def createSubscpriotn(subscription: PollSubscription):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.insert(
            PollSubscription, subscription.__dict__))
    POLLARIS_DB.commit()


def removeSubscriptionByConnectionId(connectionId: str):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(querybuilder.delete(PollSubscription, where=[
            Expression("connectionId", connectionId)
        ]))
    POLLARIS_DB.commit()


def findSubscriptionsById(pollId: int) -> List[PollSubscription]:
    with POLLARIS_DB.cursor(DictCursor) as cursor:
        cursor.execute(querybuilder.select(PollSubscription,
                                           where=[Expression("pollId", pollId)]))
        subscriptions = [PollSubscription(**row) for row in cursor.fetchall()]
        return subscriptions
