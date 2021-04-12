from poll import service, error
from poll.model import *

import json

import response
import request


def createPoll(event, context):
    data = request.getData(event)

    userId = data["userId"]
    question = data["question"]
    options = data["options"]

    poll = Poll(userId, question, list(map(lambda option: Option(
        None, option["index"], option["body"], None), options)))
    createdPoll = service.createPoll(poll)

    return response.created(json.dumps(createdPoll.toJson()))


def answer(event, context):
    data = request.getData(event)

    try:
        option = data["option"]
        option["count"] = None
        service.answer(Answer(data["userId"], Option(**option)))
        return response.ok()
    except error.AlreadyAnsweredError:
        return response.conflict("You have already answered")


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
