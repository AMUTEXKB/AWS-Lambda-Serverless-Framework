import sys
import json
import datetime
import logging
import os
# pylint: disable=import-error
from helpers.response import ResponseHelper
from helpers.utils import convert_datetime_to_epoch, convert_string_to_bool
from helpers.dynamodb_helper import DynamoDbHelper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record updated successfully"
    record = None

    try:
        user_context = event["requestContext"]["authorizer"]
        community_id = event["pathParameters"]["community_id"]
        question_id = event["pathParameters"]["question_id"]
        question_record = DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'], \
                                             {"id": question_id, "community_id": community_id})

        if question_record is not None:
            body = json.loads(event['body'])
            is_allow_edit = True
            if not convert_string_to_bool(user_context["is_admin"]) is True:
                if not question_record["user_id"] == user_context["id"]:
                    is_allow_edit = False
                if list(body.keys()) == ['up_votes']:
                    is_allow_edit = True
                    body = up_vote(vote=body, user_id=question_record['user_id'],
                                   question_id=question_id)

            if is_allow_edit:
                record = edit_record(body, question_id, community_id, question_record)
            else:
                status_code = 403
                message = "You are not authorized to perform this action"
        else:
            status_code = 404
            message = "Given question doesn't not exists"
    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if record is not None:
        response["Item"] = record

    return ResponseHelper.format_response(status_code, response)


def edit_record(body, question_id, community_id, question_record):
    current_datetime = datetime.datetime.now()
    body["id"] = question_id
    body["updated_time"] = str(current_datetime)
    body["updated_time_epoch"] = int(convert_datetime_to_epoch(current_datetime))
    body["community_id"] = community_id

    question_record.update(body)
    DynamoDbHelper.insert(os.environ["QUESTION_TABLE_NAME"], question_record)

    return question_record


def up_vote(vote, user_id, question_id):
    COMMUNITY_VOTES_FIELD = 'community_votes'
    user_record = get_user_record(user_id)
    community_votes = user_record[COMMUNITY_VOTES_FIELD]
    if question_id in community_votes:
        vote['up_votes'] -= 1
        body = {COMMUNITY_VOTES_FIELD: community_votes.pop(question_id)}
    else:
        vote['up_votes'] += 1
        body = {COMMUNITY_VOTES_FIELD: community_votes.extend(question_id)}
    DynamoDbHelper.insert(os.environ["USER_TABLE_NAME"], body)
    return vote


def get_user_record(user_id):
    params = {
        "KeyConditionExpression": "#code = :user_id",
        "ExpressionAttributeNames": {
            '#code': 'code',
        },
        "ExpressionAttributeValues": {
            ":user_id": user_id,
        },
        "ScanIndexForward": False,
        "IndexName": "code_index"
    }
    return DynamoDbHelper.query(os.environ['USER_TABLE_NAME'], params)
