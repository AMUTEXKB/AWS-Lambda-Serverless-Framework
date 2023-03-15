import sys
import json
import datetime
import logging
import os
import uuid
# pylint: disable=import-error
from helpers.response import ResponseHelper
from helpers.utils import convert_datetime_to_epoch
from helpers.dynamodb_helper import DynamoDbHelper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record added successfully"
    record_id = None

    try:
        user_context = event["requestContext"]["authorizer"]
        question_id = event["pathParameters"]["question_id"]
        community_id = event["pathParameters"]["community_id"]
        body = json.loads(event['body'])

        if DynamoDbHelper.is_exists(os.environ["QUESTION_TABLE_NAME"], question_id):
            question_record = \
                DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'],
                                   {"id": question_id, "community_id": community_id})[
                    "number_of_comments"]
            comments_number = question_record.get("number_of_comments", default=0)

            record_id = add_record(body, question_id, user_context, comments_number, community_id)
        else:
            status_code = 404
            message = "Given question doesn't exists"
    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not record_id is None:
        response["id"] = record_id

    return ResponseHelper.format_response(status_code, response)


def add_record(body, question_id, user_context, comments_number: int, community_id: str):
    current_datetime = datetime.datetime.now()
    body["id"] = str(uuid.uuid4())
    body["created_time"] = str(current_datetime)
    body["created_time_epoch"] = int(convert_datetime_to_epoch(current_datetime))
    body["question_id"] = question_id
    body["user_id"] = user_context["id"]
    body["user_email"] = user_context["email"]

    DynamoDbHelper.insert(os.environ["ANSWER_TABLE_NAME"], body)
    DynamoDbHelper.update_field(table_name=os.environ["QUESTION_TABLE_NAME"], key_name='id',
                                key_value=question_id,
                                field_name='number_of_comments', field_value=comments_number + 1,
                                community_id=community_id)

    return body["id"]
