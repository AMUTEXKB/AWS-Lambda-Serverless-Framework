import os
import uuid
from datetime import datetime
from utils import convert_datetime_to_epoch
from dynamodb_helper import DynamoDbHelper


def create_application_card(body, user_id):
    current_datetime = datetime.now()
    body['id'] = body.get('id', str(uuid.uuid4()))
    body['created_time'] = str(current_datetime)
    body['created_time_epoch'] = int(convert_datetime_to_epoch(current_datetime))
    body['user_id'] = user_id

    DynamoDbHelper.insert(os.environ['APPLICATION_TRACKER_TABLE_NAME'], body)

    return body['id']