import boto3

# Initialize the EC2 client
ec2 = boto3.client('ec2', region_name="eu-west-1")


# Describe the instance
response = ec2.describe_instances(InstanceIds=["i-036c61db688bb26f9"])

# Extract instance details
instance = response['Reservations'][0]['Instances'][0]

# Print instance information
print("Instance ID:", instance['InstanceId'])
print("Instance State:", instance['State']['Name'])
print("Instance Type:", instance['InstanceType'])
print("Public DNS:", instance.get('PublicDnsName', 'N/A'))
print("Private IP:", instance['PrivateIpAddress'])