import paramiko
import logging
import os
import boto3
import json
from typing import Optional
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SSHConnection:
    def __init__(self):
        self.hostname = os.getenv('SSH_HOST', '172.31.4.134')
        self.username = os.getenv('SSH_USER', 'fsxadmin')
        self.client: Optional[paramiko.SSHClient] = None
        self.password = self.get_secret()

    def get_secret(self) -> str:
        """Retrieve password from AWS Secrets Manager"""
        # Replace with your secret name
        secret_name = "fsx/ssh/key" 

         # Replace with your AWS region
        region_name = "eu-west-1"     

        try:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )

            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            
            if 'SecretString' in get_secret_value_response:
                secret = json.loads(get_secret_value_response['SecretString'])
                # Assuming the secret is stored with 'password' as the key
                return secret.get('password')
            else:
                logger.error("Secret not found in SecretString format")
                raise ValueError("Invalid secret format")

        except ClientError as e:
            logger.error(f"Failed to retrieve secret: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving secret: {e}")
            raise

    def load_host_keys(self):
        """Load host keys from known_hosts file or create if doesn't exist"""
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        os.makedirs(os.path.dirname(known_hosts_path), exist_ok=True)
        
        if not os.path.exists(known_hosts_path):
            open(known_hosts_path, 'a').close()
            logger.info(f"Created new known_hosts file at {known_hosts_path}")
        
        self.client.load_host_keys(known_hosts_path)

    def connect(self) -> bool:
        """Establish SSH connection"""
        try:
            logger.info(f"Attempting to connect to {self.hostname}")
            self.client = paramiko.SSHClient()
            
            # Load system host keys
            self.client.load_system_host_keys()
            self.load_host_keys()
            
            # First, get the remote server's key
            transport = paramiko.Transport(self.hostname)
            transport.connect()
            key = transport.get_remote_server_key()
            transport.close()

            # Add the key to known_hosts
            known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
            self.client.get_host_keys().add(self.hostname, key.get_name(), key)
            self.client.save_host_keys(known_hosts_path)
            
            # Now connect with the saved key
            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                timeout=10
            )
            
            logger.info("Successfully connected")
            return True
            
        except paramiko.AuthenticationException:
            logger.error("Authentication failed")
            return False
        except paramiko.SSHException as ssh_exception:
            logger.error(f"SSH exception occurred: {ssh_exception}")
            return False
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return False

    def execute_command(self, command: str) -> tuple[list[str], str]:
        """Execute SSH command and return output and errors"""
        if not self.client:
            return [], "No SSH connection established"

        try:
            logger.info(f"Executing command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command.strip())
            
            output_lines = [line.strip('\n') for line in stdout]
            errors = stderr.read().decode().strip()
            
            if errors:
                logger.error(f"Command errors: {errors}")
            
            return output_lines, errors

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return [], str(e)

    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            logger.info("Connection closed")

def main():
    ssh = SSHConnection()
    
    try:
        if ssh.connect():
            output_lines, errors = ssh.execute_command('lun show')
            
            if output_lines:
                print("\nCommand output:")
                for line in output_lines:
                    print(line)
            
            if errors:
                print(f"\nErrors encountered:\n{errors}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
