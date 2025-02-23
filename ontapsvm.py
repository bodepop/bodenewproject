import boto3
client = boto3.client('fsx')
response = client.describe_storage_virtual_machines( StorageVirtualMachineIds=["svm-01107a857272f799e"])

print (response['StorageVirtualMachines'][0]['FileSystemId'])
print (response['StorageVirtualMachines'][0]['Lifecycle'])
print (response['StorageVirtualMachines'][0]['ActiveDirectoryConfiguration'])
print (response['StorageVirtualMachines'][0]['CreationTime'])


