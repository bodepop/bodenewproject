
import boto3
from botocore.exceptions import ClientError

# Retrieve secret value using SecretId
admin_secret = get_secscret_value('fsx/ssh/key')

# Convert secret value from JSON to dictionary
secret = json.loads(admin_secret)

# Create a PSCredential object using the secret's username and password
username = secret['username']
password = getpass(prompt='Enter password: ')
credential = Credential(username, password)

