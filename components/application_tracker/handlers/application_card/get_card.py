import sys
import logging
import os
# pylint: disable=import-error
from helpers.response import ResponseHelper
from helpers.dynamodb_helper import DynamoDbHelper
from helpers.utils import convert_string_to_bool

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record found"
    record = None

    try:
        user_id = event["pathParameters"]["user_id"]
        job_id = event["pathParameters"]["job_id"]
        user_context = event["requestContext"]["authorizer"]

        is_allow_get = True
        if not convert_string_to_bool(user_context["is_admin"]) is True:
            if not user_id == user_context["id"]:
                is_allow_get = False

        if is_allow_get:
            record = DynamoDbHelper.get(os.environ['APPLICATION_TRACKER_TABLE_NAME'], \
                    { "id": job_id, "user_id": user_id })
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

    if not record is None:
        response['Item'] = record
    elif not status_code == 500 and not status_code == 403:
        status_code = 404
        response["message"] = "Record not found"

    return ResponseHelper.format_response(status_code, response)
