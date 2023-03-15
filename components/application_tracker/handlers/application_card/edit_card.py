import datetime
import json
import logging
import os
import sys

# pylint: disable=import-error
from helpers.dynamodb_helper import DynamoDbHelper
from helpers.response import ResponseHelper
from helpers.utils import convert_datetime_to_epoch

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record updated successfully"
    record = None

    try:
        # user_context = event["requestContext"]["authorizer"]
        user_id = event["pathParameters"]["user_id"]
        job_id = event["pathParameters"]["job_id"]
        job_record = DynamoDbHelper.get(os.environ['APPLICATION_TRACKER_TABLE_NAME'], \
                                        {"id": job_id, "user_id": user_id})

        if job_record is not None:
            is_allow_edit = True
            # if not convert_string_to_bool(user_context["is_admin"]) is True:
            #     if not job_record["user_id"] == user_context["id"]:
            #         is_allow_edit = False

            if is_allow_edit:
                body = json.loads(event['body'])
                record = edit_record(body, job_id, user_id, job_record)
            else:
                status_code = 403
                message = "You are not authorized to perform this action"
        else:
            status_code = 404
            message = "Given job doesn't not exists"
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


def edit_record(body, job_id, user_id, job_record):
    current_datetime = datetime.datetime.now()
    body["id"] = job_id
    body["updated_time"] = str(current_datetime)
    body["updated_time_epoch"] = int(convert_datetime_to_epoch(current_datetime))
    body["user_id"] = user_id

    job_record.update(body)
    DynamoDbHelper.insert(os.environ["APPLICATION_TRACKER_TABLE_NAME"], job_record)

    return job_record
