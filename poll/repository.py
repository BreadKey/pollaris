from poll.model import *

from db import POLLARIS_DB

import pymysql


def createPoll(poll: Poll) -> Poll:
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'insert into Polls (userId, question) values("{poll.userId}", "{poll.question}")'
        )
        id = cursor.lastrowid

        for option in sorted(poll.options, key=lambda option: option.index):
            cursor.execute(
                f'insert into Options (pollId, `index`, body, count) values({id}, {option.index}, "{option.body}", 0)'
            )
    POLLARIS_DB.commit()

    return Poll(poll.userId, poll.question, list(map(lambda option: Option(id, option.index, option.body, 0), poll.options)), id)


def createAnswer(answer: Answer):
    with POLLARIS_DB.cursor() as cursor:
        cursor.execute(
            f'insert into Answers (userId, pollId, `index`) values("{answer.userId}", {answer.option.pollId}, {answer.option.index})'
        )
        cursor.execute(
            f'update Options set count = count + 1 where pollId = {answer.option.pollId} and `index` = {answer.option.index}'
        )
    POLLARIS_DB.commit()


def orderByDescFrom(id: int, count: int) -> List[Poll]:
    with POLLARIS_DB.cursor(pymysql.cursors.DictCursor) as cursor:
        query = 'select * from Polls'

        if (id is not None):
            query += f' where id < {id}'

        query += f' order by id desc limit {count}'

        cursor.execute(query)
        rows = cursor.fetchall()

        polls = []

        for row in rows:
            id = row["id"]
            cursor.execute(f"select * from Options where pollId = {id}")
            options = list(map(lambda optionRow: Option(
                **optionRow), cursor.fetchall()))

            polls.append(Poll(row["userId"], row["question"], options, id))

    return polls
