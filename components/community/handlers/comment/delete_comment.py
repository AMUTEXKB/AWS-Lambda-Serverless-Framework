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
        question_id = event["pathParameters"]["question_id"]
        community_id = event["pathParameters"]["community_id"]
        answer_id = event["pathParameters"]["answer_id"]

        is_allow_delete = True
        if not convert_string_to_bool(user_context["is_admin"]) is True:
            answer_record = DynamoDbHelper.get(os.environ['ANSWER_TABLE_NAME'], \
                                               {"id": answer_id, "question_id": question_id})
            if not answer_record is None and not answer_record["user_id"] == user_context["id"]:
                is_allow_delete = False

        if is_allow_delete:
            comments_number = \
                DynamoDbHelper.get(os.environ['QUESTION_TABLE_NAME'],
                                   {"id": question_id, "community_id": community_id})[
                    "number_of_comments"]

            is_item_found = DynamoDbHelper.delete(os.environ['ANSWER_TABLE_NAME'], \
                                                  {"id": answer_id, "question_id": question_id})
            if is_item_found:
                DynamoDbHelper.update_field(table_name=os.environ["QUESTION_TABLE_NAME"], key_name='id',
                                            key_value=question_id,
                                            field_name='number_of_comments', field_value=comments_number - 1,
                                            community_id=community_id)
            else:
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
