import boto3
client = boto3.client('fsx')
response = client.describe_file_systems( FileSystemIds=["fs-02962c127de4999a4"])

print (response['FileSystems'][0]['Lifecycle'])






