import boto3
client = boto3.client('fsx')
response = client.describe_file_systems( FileSystemIds=["fsx-id"])

print (response['FileSystems'][0]['Lifecycle'])
print (response['FileSystems'][0]['FileSystemId'])
print (response['FileSystems'][0]['FileSystemType'])
print (response['FileSystems'][0]['OwnerId'])
print (response['FileSystems'][0]['StorageCapacity'])
print (response['FileSystems'][0]['StorageType'])
print (response['FileSystems'][0]['SubnetIds'])

    