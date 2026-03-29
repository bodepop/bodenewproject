import boto3
client = boto3.client('fsx')
response = client.describe_file_systems( FileSystemIds=["fs-id"])

print (response['FileSystems'][0]['Lifecycle'])






