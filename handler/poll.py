from poll import CONSTRAINTS, service, error
from poll.model import *

import json

from handler import request, response, needData


@needData
def create(event, context):
    data = request.getData(event)

    userId = data["userId"]
    question = data["question"]
    options = data["options"]

    poll = Poll(userId, question, list(map(lambda option: Option(
        None, option["index"], option["body"], None), options)))

    try:
        createdPoll = service.createPoll(poll)
        return response.created(json.dumps(createdPoll.toJson()))
    except AssertionError as e:
        return response.badRequest(e.__str__())


def getConstraints(event, context):
    return response.ok(json.dumps(CONSTRAINTS.__dict__))


@needData
def answer(event, context):
    data = request.getData(event)
    option = data["option"]
    option["count"] = None
    userId = data["userId"]

    try:
        service.answer(Answer(userId, Option(**option)))
        return response.ok()
    except error.AlreadyAnsweredError:
        return response.conflict("User already answered")

def page(event, context):
    data = request.getData(event)

    fromId = data.get("from", None)
    count = data.get("count", 10)

    return response.ok(
        json.dumps(
            list(
                map(
                    lambda poll: poll.toJson(), service.page(fromId, count)
                )
            )
        )
    )
