import sys
import json
import datetime
import logging
import uuid
import os
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
        community_id = event["pathParameters"]["community_id"]
        body = json.loads(event['body'])
        record_id = add_record(body, community_id, user_context)
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

def add_record(body, community_id, user_context):
    current_datetime = datetime.datetime.now()
    body["id"] = str(uuid.uuid4())
    body["created_time"] = str(current_datetime)
    body["created_time_epoch"] = int(convert_datetime_to_epoch(current_datetime))
    body["community_id"] = community_id
    body["user_id"] = user_context["id"]
    body["user_email"] = user_context["email"]

    DynamoDbHelper.insert(os.environ["QUESTION_TABLE_NAME"], body)

    return body["id"]
