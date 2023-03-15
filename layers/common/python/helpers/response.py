import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


class ResponseHelper:
    @staticmethod
    def format_response(status_code, message):
        return {
            'statusCode': status_code,
            'body': json.dumps(message, cls=DecimalEncoder),
            'headers': {
                'Content-Type': 'application/json',
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Credentials': True,
            }
        }
