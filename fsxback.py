import json
import boto3
fsx = boto3.client('fsx')
response = fsx.describe_backups(
  Filters=[
  {
    'Name': 'file-system-id',
    'Values': [ 'fs-08ab18183d65c0a41' ]
  },
  ],
  MaxResults=100
  )
print (len(response["Backups"]))
