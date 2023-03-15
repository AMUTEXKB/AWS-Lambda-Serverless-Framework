import logging
import os
import sys

from helpers.dynamodb_helper import DynamoDbHelper
# pylint: disable=import-error
from helpers.response import ResponseHelper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record deleted successfully"

    try:
        # user_context = event["requestContext"]["authorizer"]
        user_id = event["pathParameters"]["user_id"]
        job_id = event["pathParameters"]["job_id"]

        is_allow_delete = True
        # if not convert_string_to_bool(user_context["is_admin"]) is True:
        #     job_record = DynamoDbHelper.get(os.environ['APPLICATION_TRACKER_TABLE_NAME'], \
        #                 { "id": job_id, "user_id": user_id })
        #     if not job_record is None and not job_record["user_id"] == user_context["id"]:
        #         is_allow_delete = False

        if is_allow_delete:
            is_item_found = DynamoDbHelper.delete(os.environ['APPLICATION_TRACKER_TABLE_NAME'], \
                                                  {"id": job_id, "user_id": user_id})

            if not is_item_found:
                message = "Record not found"
                status_code = 404
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

    return ResponseHelper.format_response(status_code, response)
