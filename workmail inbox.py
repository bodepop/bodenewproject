#import the imap client
from imapclient import IMAPClient

#user details
server_endpoint= "imap.mail.us-east-1.awsapps.com"
email_address="joe@example.com"
user_password="*************"

#start the connection
server = IMAPClient(server_endpoint, use_uid=True)
server.login(email_address, user_password)


# choose the folder to filter
select_info = server.select_folder('INBOX')

# serach for all unread messages
messages = server.search("UNSEEN")

#loop through all messages and print the subject
for msgid, data in server.fetch(messages, ['ENVELOPE']).items(): 
	envelope = data[b'ENVELOPE']
	print('ID #%d: "%s" received %s' % (msgid, envelope.subject.decode(), envelope.date))