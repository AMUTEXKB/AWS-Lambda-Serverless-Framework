import sys
import logging
import os
# pylint: disable=import-error
from helpers.response import ResponseHelper
from helpers.dynamodb_helper import DynamoDbHelper

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record found"
    record = None

    try:
        community_id = event["pathParameters"]["community_id"]
        question_id = event["pathParameters"]["question_id"]
        record = DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'], \
                                    {"id": question_id, "community_id": community_id})
    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not record is None:
        response['Item'] = record
    elif not status_code == 500:
        status_code = 404
        response["message"] = "Record not found"

    return ResponseHelper.format_response(status_code, response)
