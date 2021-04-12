from poll import service, error
from poll.model import *

import json

import response


def createPoll(event, context):
    userId = event["userId"]
    question = event["question"]
    options = event["options"]

    poll = Poll(userId, question, list(map(lambda option: Option(
        None, option["index"], option["body"], None), options)))
    createdPoll = service.createPoll(poll)

    return response.created(json.dumps(createdPoll.toJson()))

def answer(event, context):
    try:
        option = event["option"]
        option["count"] = None
        service.answer(Answer(event["userId"], Option(**option)))
        return response.ok()
    except error.AlreadyAnsweredError:
        return response.conflict("You have already answered")