from poll.model import *

from db import POLLARIS_DB, querybuilder
from db.querybuilder import Expression

import pymysql


def createPoll(poll: Poll) -> Poll:
    with POLLARIS_DB.cursor() as cursor:
        pollData = poll.__dict__.copy()
        pollData.pop("options")

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

    return Poll(poll.userId, poll.question, list(map(lambda option: Option(id, option.index, option.body, 0), poll.options)), id)


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
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
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
            id = row["id"]
            cursor.execute(querybuilder.select(
                Option, where=[Expression("pollId", id)]))
            row["options"] = list(map(lambda optionRow: Option(
                **optionRow), cursor.fetchall()))

            polls.append(Poll(**row))

    return polls
