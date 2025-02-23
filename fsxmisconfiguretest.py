import boto3
client = boto3.client('fsx')
response = client.describe_file_systems( FileSystemIds=["fs-08ab18183d65c0a41"])

print (response['FileSystems'][0]['Lifecycle'])

if (response['FileSystems'][0]['Lifecycle'] == 'AVAILABLE'):
 print ('The file system is in a healthy state, and is reachable and available for use.')

else:
 
 if(response['FileSystems'][0]['Lifecycle'] == 'MISCONFIGURED'):
      print ('The file system is in an impaired state due to a change in your Active Directory environment. Your file system is either currently unavailable or at risk of losing availability, and backups may not succeed')

 else:

  if(response['FileSystems'][0]['Lifecycle'] == 'UPDATING'):
      print ('The file system is undergoing a customer-initiated update.')

  elif(response['FileSystems'][0]['Lifecycle'] == 'FAILED'):
      print ('The file system has failed and Amazon FSx cant recover it.')  

  elif(response['FileSystems'][0]['Lifecycle'] == 'MISCONFIGURED_UNAVAILABLE'):
      print ('The file system is currently unavailable due to a change in your Active Directory environment.')

  elif(response['FileSystems'][0]['Lifecycle'] == 'DELETING'):
      print ('Amazon FSx is deleting an existing file system.')

 if(response['FileSystems'][0]['Lifecycle'] == 'FAILED'):
  print ('The file system has failed and Amazon FSx cant recover it.')



    






        