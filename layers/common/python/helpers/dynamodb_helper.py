import sys
import logging
import boto3
import os
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMO_DB_CLIENT = boto3.resource('dynamodb')
DYNAMO_CLIENT = boto3.client('dynamodb')


class DynamoDbHelper:
    # todo refactor from static methods to class methods

    @staticmethod
    def get_table_client(table_name):
        return DYNAMO_DB_CLIENT.Table(table_name)

    @staticmethod
    def insert(table_name, item):
        table_client = DynamoDbHelper.get_table_client(table_name)
        table_client.put_item(Item=item)

    @staticmethod
    def update_field(table_name, key_name, key_value, field_name, field_value, **kwargs):
        table = DynamoDbHelper.get_table_client(table_name=table_name)

        keys = {key_name: key_value}
        if kwargs:
            for key, value in kwargs.items():
                keys[key] = value

        response = table.update_item(
            Key=keys,
            UpdateExpression="set " + field_name + "=:r",
            ExpressionAttributeValues={
                ':r': field_value,
            },
            ReturnValues="UPDATED_NEW"
        )
        return response

    @staticmethod
    def delete(table_name, key):
        is_item_found = True
        table_client = DynamoDbHelper.get_table_client(table_name)
        response = table_client.delete_item(Key=key, ReturnValues='ALL_OLD')
        if 'Attributes' not in response or not response['Attributes']:
            is_item_found = False
        return is_item_found

    @staticmethod
    def get(table_name, key):
        record = None

        try:
            table_client = DynamoDbHelper.get_table_client(table_name)
            response = table_client.get_item(Key=key)
            if 'Item' in response:
                record = response['Item']
        except DYNAMO_CLIENT.exceptions.ResourceNotFoundException as exception:
            logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())

        return record

    @staticmethod
    def query(table_name, params):
        table_client = DynamoDbHelper.get_table_client(table_name)
        is_data_pending = True
        response = table_client.query(**params)
        records = []

        while is_data_pending:
            is_data_pending = True if 'LastEvaluatedKey' in response else False

            if response['Count'] > 0:
                records.extend(response['Items'])

            if is_data_pending:
                params['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = table_client.query(**params)

        return records

    @staticmethod
    def is_exists(table_name, record_id):
        is_exists = False
        table_client = DynamoDbHelper.get_table_client(table_name)
        params = {
            "Select": "COUNT",
            "FilterExpression": Attr("id").eq(record_id)
        }
        response = table_client.scan(**params)
        if response['Count'] > 0:
            is_exists = True

        return is_exists

    @staticmethod
    def batch_delete(table_name, keys):
        table_client = DynamoDbHelper.get_table_client(table_name)
        chunk_size = 20

        for i in range(0, len(keys), chunk_size):
            chunk = keys[i:i + chunk_size]
            with table_client.batch_writer() as batch:
                for key in chunk:
                    batch.delete_item(
                        Key=key
                    )

    @staticmethod
    def get_user_record(user_id):
        params = {
            "KeyConditionExpression": "#code = :user_id",
            "ExpressionAttributeNames": {
                '#code': 'code',
            },
            "ExpressionAttributeValues": {
                ":user_id": user_id,
            },
            "ScanIndexForward": False,
            "IndexName": "code_index"
        }
        return DynamoDbHelper.query(os.environ['USER_TABLE_NAME'], params)