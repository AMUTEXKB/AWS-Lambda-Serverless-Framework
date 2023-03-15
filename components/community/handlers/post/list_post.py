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
    message = "Record(s) found"
    records = None

    try:
        community_id = event["pathParameters"]["community_id"]
        records = get_records(community_id)
    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not records is None and not len(records) == 0:
        response['Items'] = records
    elif not status_code == 500:
        response["message"] = "Record(s) not found"

    return ResponseHelper.format_response(status_code, response)

def get_records(community_id):
    params = {
        "KeyConditionExpression": "#community_id = :community_id and \
                                 #created_time_epoch > :intZero",
        "ExpressionAttributeNames": {
            '#community_id': 'community_id',
            "#created_time_epoch": 'created_time_epoch'
        },
        "ExpressionAttributeValues": {
            ":community_id": community_id,
            ':intZero': 0,
        },
        "ScanIndexForward": False,
        "IndexName": "community_id_created_time_epoch_index"
    }
    return DynamoDbHelper.query(os.environ['QUESTION_TABLE_NAME'], params)
