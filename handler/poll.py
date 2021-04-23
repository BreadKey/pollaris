from poll import CONSTRAINTS, service, error
from poll.model import *

import json

from handler import private, request, response, needData


@private
def create(event, context):
    data = request.getData(event)

    userId = data["userId"]
    question = data["question"]
    options = data["options"]

    poll = Poll(userId, question, [Option(
        None, option["index"], option["body"], None) for option in options])

    try:
        createdPoll = service.createPoll(poll)
        return response.created(json.dumps(createdPoll.toJson()))
    except AssertionError as e:
        return response.badRequest(e.__str__())


def getConstraints(event, context):
    return response.ok(json.dumps(CONSTRAINTS.__dict__))


@private
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
    except error.PollNotExistError:
        return response.badRequest("Poll not exist")

def page(event, context):
    data = request.getData(event)

    fromId = data.get("from", None)
    count = data.get("count", 10)

    return response.ok(
        json.dumps(
            [poll.toJson() for poll in service.page(fromId, count)]
        )
    )
