import json
import logging
import sys

from helpers.create_application_card import create_application_card
from helpers.response import ResponseHelper

# pylint: disable=import-error

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    status_code = 200
    message = 'Record added successfully'
    record_id = None

    try:
        # user_context = event['requestContext']['authorizer']
        user_id = event['pathParameters']['user_id']
        body = json.loads(event['body'])

        is_allow_edit = True
        # if not convert_string_to_bool(user_context['is_admin']) is True:
        #     if not user_id == user_context['id']:
        #         is_allow_edit = False

        if is_allow_edit:
            record_id = create_application_card(body, user_id)
        else:
            status_code = 403
            message = 'You are not authorized to perform this action'

    except Exception as exception:
        logger.error('Exception: {}'.format(exception), exc_info=sys.exc_info())
        status_code = 500
        message = 'Process has encountered an internal server exception.'

    response = {
        'message': message
    }

    if not record_id is None:
        response['id'] = record_id

    return ResponseHelper.format_response(status_code, response)
