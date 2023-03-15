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
        question_id = event["pathParameters"]["question_id"]
        answer_id = event["pathParameters"]["answer_id"]
        answer_record = DynamoDbHelper.get(os.environ['ANSWER_TABLE_NAME'], \
                    { "id": answer_id, "question_id": question_id })
        if not answer_record is None:
            is_allow_edit = True
            if not convert_string_to_bool(user_context["is_admin"]) is True:
                if not answer_record["user_id"] == user_context["id"]:
                    is_allow_edit = False
            if is_allow_edit:
                body = json.loads(event['body'])
                record = edit_record(body, question_id, answer_id, answer_record)
            else:
                status_code = 403
                message = "You are not authorized to perform this action"
        else:
            status_code = 404
            message = "Given answer doesn't not exists"

    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not record is None:
        response["Item"] = record

    return ResponseHelper.format_response(status_code, response)

def edit_record(body, question_id, answer_id, answer_record):
    current_datetime = datetime.datetime.now()
    body["id"] = answer_id
    body["updated_time"] = str(current_datetime)
    body["updated_time_epoch"] = int(convert_datetime_to_epoch(current_datetime))
    body["question_id"] = question_id

    answer_record.update(body)
    DynamoDbHelper.insert(os.environ["ANSWER_TABLE_NAME"], answer_record)

    return answer_record
