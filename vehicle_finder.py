import json
import os

import boto3
import requests
from boto3.dynamodb.conditions import Key

dynamo = boto3.resource('dynamodb')
""" :type : pyboto3.dynamodb """

sm = boto3.client('secretsmanager')
""" :type : pyboto3.secretsmanager """

table_name = os.environ['STOLEN_VEHICLE_REGISTRY_TABLE_NAME']
secret_id = os.environ['EXTERNAL_STOLEN_VEHICLE_SERVICE_SECRET_ID']


def lambda_handler(event, null):
    print(f'event: {event}')
    registration_number = event['registration-number']
    items = dynamo.Table(table_name).query(
        KeyConditionExpression=Key('registration-number').eq(registration_number)
    )['Items']

    vehicle_found = len(items) != 0
    yes_or_not = yes_or_not_as_str(vehicle_found)
    message = f'A vehicle with the registration number {registration_number} has{yes_or_not}been found in our database of stolen vehicles. Please, check the db service to get more details.'

    secret = json.loads(sm.get_secret_value(SecretId=secret_id)['SecretString'])

    if not vehicle_found:
        response = requests.get(secret['url'], auth=(secret['user'], secret['secret-key']),
                                params={'registration_number': registration_number})
        vehicle_found = response.json()['vehicle-found']
        message = message + f'. \nA vehicle with the registration number {registration_number} has{yes_or_not}been found in the external service of stolen vehicles.'
    return {
        'vehicle-found': vehicle_found,
        'registration-number': registration_number,
        'message': message
    }


def yes_or_not_as_str(vehicle_found):
    return " " if vehicle_found else " not "
