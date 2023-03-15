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
    question_record = None

    try:
        user_context = event["requestContext"]["authorizer"]
        community_id = event["pathParameters"]["community_id"]
        question_id = event["pathParameters"]["question_id"]
        question_record = DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'], \
                                             {"id": question_id, "community_id": community_id})

        if question_record is not None:
            body = json.loads(event['body'])
            votes = up_vote(votes_number=body, user_id=user_context['id'],
                            question_id=question_id)
            DynamoDbHelper.update_field(table_name=os.environ["QUESTION_TABLE_NAME"], key_name='id',
                                        key_value=question_id,
                                        field_name='up_votes', field_value=votes, community_id=community_id)

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

    if question_record is not None:
        response["Item"] = question_record

    return ResponseHelper.format_response(status_code, response)


def up_vote(votes_number, user_id, question_id):
    COMMUNITY_VOTES_FIELD = 'community_votes'
    user_record = DynamoDbHelper.get_user_record(user_id)[0]
    community_votes = user_record.get(COMMUNITY_VOTES_FIELD)
    votes_number = int(votes_number['up_votes'])
    if not community_votes:
        votes_number += 1
        community_votes = [question_id]
    else:
        if question_id in community_votes:
            votes_number -= 1
            community_votes.remove(question_id)
        else:
            votes_number += 1
            community_votes.append(question_id)
    DynamoDbHelper.update_field(table_name=os.environ["USER_TABLE_NAME"], key_name='id', key_value=user_record['id'],
                                field_name=COMMUNITY_VOTES_FIELD, field_value=community_votes)
    return votes_number
