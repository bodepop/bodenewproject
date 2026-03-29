import json
import boto3
fsx = boto3.client('fsx')
response = fsx.describe_backups(
  Filters=[
  {
    'Name': 'file-system-id',
    'Values': [ 'fs-75787gy88h8' ]
  },
  ],
  MaxResults=100
  )
print (len(response["Backups"]))
