import smtplib
import socket
import platform
from email.mime.text import MIMEText

# SMTP server configuration
smtp_server = "email-smtp.eu-west-1.amazonaws.com"
smtp_port = 465
smtp_username = "joe@example.com"
smtp_password = "************"

# Email recipient
recipient_email = "john@example.com"

# List of known devices
known_devices = ["device1", "device2", "device3"]

def get_current_devices():
    """
    Get a list of all devices currently connected to the network.
    This function should be implemented based on your network setup.
    """
    # Implement logic to get a list of current devices on the network
    current_devices = ["device1", "device2", "device3", "new_device"]
    return current_devices

def send_email_notification(new_device):
    """
    Send an email notification about the new device on the network.
    """
    try:
        # Create the email message
        msg = MIMEText(f"A new device '{new_device}' has joined the network.")
        msg["Subject"] = "New Device Alert"
        
        msg["From"] = smtp_username
        msg["To"] = recipient_email

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(smtp_username, recipient_email, msg.as_string())
        print(f"Email notification sent for new device '{new_device}'")

        # Disconnect from the SMTP server
        server.quit()

    except Exception as e:
        print(f"Failed to send email notification: {e}")

def main():
    """
    Main function to check for new devices and send email notifications.
    """
    current_devices = get_current_devices()
    new_devices = set(current_devices) - set(known_devices)

    for new_device in new_devices:
        send_email_notification(new_device)

if __name__ == "__main__":
    main()