import boto3
import json


def lambda_handler(event, context):
    secrets_client = boto3.client('secretsmanager')
    secret_name = 'fsx/ssh/key'
    secret_response = secrets_client.get_secret_value(SecretId=secret_name).get('SecretString')
    print(secret_response)
    secret_list = json.loads(secret_response)

    username = secret_list.get('username')
    print(username)