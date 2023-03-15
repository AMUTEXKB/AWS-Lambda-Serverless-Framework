import json
import logging
import os
import sys

# pylint: disable=import-error
# pylint: disable=wildcard-import
import requests
from handlers.authorizer.gateway_response_helper import *
from jose import jwt
from six.moves.urllib.request import urlopen

from applications.aws_lambdas.authorizer.gateway_response_helper import AuthPolicy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALGORITHMS = ["RS256"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]

AUTH0_MANAGEMENT_API_DOMAIN = os.environ["AUTH0_MANAGEMENT_API_DOMAIN"]
AUTH0_MANAGEMENT_API_CLIENT_ID = os.environ["AUTH0_MANAGEMENT_API_CLIENT_ID"]
AUTH0_MANAGEMENT_API_SECRET = os.environ["AUTH0_MANAGEMENT_API_SECRET"]


def lambda_handler(event, context):
    logger.info(event)
    is_token_validated = False
    user_context = None
    try:
        token = event["authorizationToken"]
        validation_response = validate_token(token.replace("Bearer ", ""))
        is_token_validated = validation_response["is_token_validated"]
        if is_token_validated:
            management_api_bearer_token = get_management_api_bearer_token()
            user_email = validation_response["payload"]["email"]
            user_id = validation_response["payload"]["sub"]
            user_roles = get_user_roles(management_api_bearer_token, user_id)
            is_admin = False

            for user_role in user_roles:
                if user_role["name"] == "admin":
                    is_admin = True
                    break

            user_context = {
                "id": user_id,
                "email": user_email,
                "is_admin": is_admin
            }

    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())

    auth_response = get_auth_response(event, is_token_validated)
    if user_context:
        auth_response["context"] = user_context

    return auth_response


def validate_token(token):
    is_token_validated = False
    payload = None
    jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_CLIENT_ID,
                issuer="https://" + AUTH0_DOMAIN + "/"
            )
            is_token_validated = True
        except jwt.ExpiredSignatureError:
            logger.error({"code": "token_expired",
                          "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            logger.error({"code": "invalid_claims",
                          "description":
                              "incorrect claims,"
                              "please check the audience and issuer"}, 401)
        except Exception:
            logger.error({"code": "invalid_header",
                          "description":
                              "Unable to parse authentication"
                              " token."}, 401)
    else:
        logger.error({"code": "invalid_header",
                      "description": "Unable to find appropriate key"}, 401)

    return {
        "is_token_validated": is_token_validated,
        "payload": payload
    }


def get_management_api_bearer_token():
    bearer_token = None
    url = "https://" + AUTH0_DOMAIN + "/oauth/token"
    data = {
        "client_id": AUTH0_MANAGEMENT_API_CLIENT_ID,
        "client_secret": AUTH0_MANAGEMENT_API_SECRET,
        "audience": "https://" + AUTH0_MANAGEMENT_API_DOMAIN + "/api/v2/",
        "grant_type": "client_credentials"
    }

    headers = {
        'Content-type': 'application/json'
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    response_json_body = response.json()

    if 'access_token' in response_json_body:
        bearer_token = response_json_body["access_token"]

    return bearer_token


def get_auth_response(event, allow_methods=False):
    tmp = event['methodArn'].split(':')
    api_gateway_arn_tmp = tmp[5].split('/')
    aws_account_id = tmp[4]

    policy = AuthPolicy("", aws_account_id)
    policy.restApiId = api_gateway_arn_tmp[0]
    policy.region = tmp[3]
    policy.stage = api_gateway_arn_tmp[1]

    if allow_methods:
        policy.allow_all_methods()
    else:
        policy.deny_all_methods()

    auth_response = policy.build()

    return auth_response


def get_user_roles(bearer_token, user_id):
    user_roles = []
    try:
        url = "https://" + AUTH0_DOMAIN + "/api/v2/users/" + user_id + "/roles"
        headers = {
            'Content-type': 'application/json',
            "Authorization": "Bearer {}".format(bearer_token)
        }

        response = requests.get(url, headers=headers)
        response_json_body = response.json()
        user_roles.extend(response_json_body)
    except Exception as exception:
        logger.error("Exception: {}".format(exception), exc_info=sys.exc_info())

    return user_roles
