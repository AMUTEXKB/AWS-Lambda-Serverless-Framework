import logging
import os
import sys

from helpers.dynamodb_helper import DynamoDbHelper
# pylint: disable=import-error
from helpers.response import ResponseHelper
from helpers.utils import convert_string_to_bool

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record(s) found"
    records = None

    try:
        user_id = event["pathParameters"]["user_id"]
        user_context = event["requestContext"]["authorizer"]

        is_allow_list = True
        if not convert_string_to_bool(user_context["is_admin"]) is True:
            if not user_id == user_context["id"]:
                is_allow_list = False

        if is_allow_list:
            records = get_records(user_id)
        else:
            status_code = 403
            message = "You are not authorized to perform this action"

    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not records is None and not len(records) == 0:
        response['Items'] = records
    elif not status_code == 500 and not status_code == 403:
        response["message"] = "Record(s) not found"

    return ResponseHelper.format_response(status_code, response)


def get_records(user_id):
    params = {
        "KeyConditionExpression": "#user_id = :user_id and \
                                 #created_time_epoch > :intZero",
        "ExpressionAttributeNames": {
            '#user_id': 'user_id',
            "#created_time_epoch": 'created_time_epoch'
        },
        "ExpressionAttributeValues": {
            ":user_id": user_id,
            ':intZero': 0,
        },
        "ScanIndexForward": False,
        "IndexName": "user_id_created_time_epoch_index"
    }
    return DynamoDbHelper.query(os.environ['APPLICATION_TRACKER_TABLE_NAME'], params)
