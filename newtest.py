import paramiko

# Define the variables
fsx_management_ip = '172.31.4.134'
username = 'fsxadmin'
password = 'Ebunoluwa1/'
vserver_name = 'svm1'

# Specify the commands to run in the correct order
commands = [
    f"vserver vscan show -vserver {vserver_name}",
    f"vscan scanner-pool show -instance -vserver {vserver_name}",
    f"vserver vscan on-access-policy show -vserver {vserver_name}",
    "vscan connection-status show"
]

# Create an SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the filesystem
    ssh_client.connect(fsx_management_ip, username=username, password=password)

    # Run the commands
    for command in commands:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(f"Output of '{command}':")
        print(stdout.read().decode())
        print(stderr.read().decode())

finally:
    # Close the SSH connection
    ssh_client.close()