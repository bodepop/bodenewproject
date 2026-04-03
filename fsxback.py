import json
import boto3
fsx = boto3.client('fsx')
response = fsx.describe_backups(
  Filters=[
  {
    'Name': 'file-system-id',
    'Values': [ 'fs-' ]
  },
  ],
  MaxResults=100
  )
print (len(response["Backups"]))
