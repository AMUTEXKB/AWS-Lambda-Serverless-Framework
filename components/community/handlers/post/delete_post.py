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
    message = "Record deleted successfully"

    try:
        user_context = event["requestContext"]["authorizer"]
        community_id = event["pathParameters"]["community_id"]
        question_id = event["pathParameters"]["question_id"]

        is_allow_delete = True
        if not convert_string_to_bool(user_context["is_admin"]) is True:
            question_record = DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'], \
                        { "id": question_id, "community_id": community_id })
            if not question_record is None and not question_record["user_id"] == user_context["id"]:
                is_allow_delete = False

        if is_allow_delete:
            is_item_found = DynamoDbHelper.delete(os.environ['QUESTION_TABLE_NAME'], \
                { "id": question_id, "community_id": community_id })
            answer_records = get_records(question_id)
            answer_keys = [ { "id": x["id"], "question_id": x["question_id"] } \
                for x in answer_records ]
            DynamoDbHelper.batch_delete(os.environ['ANSWER_TABLE_NAME'], answer_keys)

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

def get_records(question_id):
    params = {
        "KeyConditionExpression": "#question_id = :question_id and #created_time_epoch > :intZero",
        "ExpressionAttributeNames": {
            '#question_id': 'question_id',
            "#created_time_epoch": 'created_time_epoch'
        },
        "ExpressionAttributeValues": {
            ":question_id": question_id,
            ':intZero': 0,
        },
        "ScanIndexForward": False,
        "IndexName": "question_id_created_time_epoch_index"
    }
    return DynamoDbHelper.query(os.environ['ANSWER_TABLE_NAME'], params)
