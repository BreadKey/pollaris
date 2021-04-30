import os
import boto3
from poll import CONSTRAINTS, service, error
from poll.model import *

import json

from handler import private, request, response, needData


@private
@needData
def create(event, context):
    """
    authorizer: authorizeUser 
    """
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
@needData
def answer(event, context):
    """
    authorizer: authorizeWithIdentity
    """
    data = request.getData(event)
    option = data["option"]
    option["count"] = None
    userId = data["userId"]

    try:
        answer = Answer(userId, Option(**option))
        service.answer(answer)

        subscriptions = service.findSubscriptionsById(answer.option.pollId)
        if subscriptions:
            __publishAnswer(subscriptions, answer)

        return response.ok()
    except error.AlreadyAnsweredError:
        return response.conflict("User already answered")
    except error.PollNotExistError:
        return response.badRequest("Poll not exist")

def __publishAnswer(subscriptions: List[PollSubscription], answer: Answer):
    endpointUrl = f"https://{os.environ.get('websocketId')}.execute-api.{os.environ.get('region')}.amazonaws.com/{os.environ.get('stage')}"
    gatewayApi = boto3.client(
        "apigatewaymanagementapi", endpoint_url=endpointUrl)
    for subscription in subscriptions:
        try:
            gatewayApi.post_to_connection(
                ConnectionId=subscription.connectionId, Data=json.dumps({"index": answer.option.index}).encode('utf-8'))
        except:
            service.unsubscribe(subscription.connectionId)

def page(event, context):
    """
    authorizer: authorizeUser 
    """
    data = request.getData(event)

    fromId = data.get("from", None)
    count = data.get("count", 10)

    userId = event["requestContext"]["authorizer"]["principalId"]

    return response.ok(
        json.dumps(
            [poll.toJson() for poll in service.page(fromId, count, userId)]
        )
    )


@needData
def webSocketConnectionManager(event, context):
    connectionId = event["requestContext"]["connectionId"]
    eventType = event["requestContext"]["eventType"]

    if eventType == "CONNECT":
        data = request.getData(event)
        pollId = data["pollId"]
        service.subscribe(pollId, connectionId)
        return response.ok()
    elif eventType == "DISCONNECT":
        service.unsubscribe(connectionId)
        return response.ok()
