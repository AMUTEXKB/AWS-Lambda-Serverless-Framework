import datetime
import json
import logging
import os
import sys

import boto3
import botocore
# pylint: disable=import-error
from helpers.airtable_helper import update_applicants_base
from helpers.response import ResponseHelper
from helpers.upload_file import create_application_card
from helpers.upload_file import upload_to_s3_bucket

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = "JOB_APPLICATION_TABLE_NAME"

cfg = botocore.config.Config(retries={'max_attempts': 0}, read_timeout=840, connect_timeout=600)
client = boto3.client('lambda', config=cfg)

DYNAMO_DB_CLIENT = boto3.resource('dynamodb')
DYNAMO_CLIENT = boto3.client('dynamodb')


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = "Record added successfully"
    ddb_record_id = None
    airtable_record_id = None

    try:
        user_context = event["requestContext"]["authorizer"]
        user_id = event['pathParameters']['user_id']
        body = json.loads(event['body'])

        card_id = create_application_card(body, user_id)
        cv_file_name = f'{body["first_name"]}-{body["last_name"]}-{body["job_name"]}.pdf'
        cv_link = upload_to_s3_bucket(file_data=body['file'], bucket_name=os.environ['ATTACHMENTS_BUCKET'],
                                      s3_file=f'cv/{cv_file_name}')
        ddb_record_id = add_record(body=body, user_context=user_context, tracker_card_id=card_id, cv_link=cv_link)
        # airtable_record_id = update_applicants_base() // todo provide parameters

    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = "Process has encountered an internal server exception."

    response = {
        "message": message
    }

    if not ddb_record_id is None:
        response["ddb_id"] = ddb_record_id
        response["airtable_record_id"] = airtable_record_id

    return ResponseHelper.format_response(status_code, response)


def add_record(body, user_context, tracker_card_id, cv_link):
    current_datetime = datetime.datetime.now()
    body["id"] = user_context["id"] + '_' + body["job_id"]
    body["user_id"] = user_context["id"]
    body["tracker_card_id"] = tracker_card_id
    body["created_time"] = str(current_datetime)
    body["cv"] = cv_link

    insert(os.environ[TABLE_NAME], body)
    return body["id"]


def insert(table_name, item):
    table_client = DYNAMO_DB_CLIENT.Table(table_name)
    table_client.put_item(Item=item)
