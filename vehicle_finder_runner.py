import os

from vehicle_finder import lambda_handler

event = {'registration-number': 'SB8392Y'}

os.environ['STOLEN_VEHICLE_REGISTRY_TABLE_NAME'] = 'dev'
lambda_handler(event, None)
