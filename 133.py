
$FSxManagementIP = '172.31.4.134'
$Username = 'fsxadmin'
$VserverName = 'svm1'


# Specify the Commands to Run in the Correct Order
# Now run commands to show above configurations are successful


$Command1 = "vserver vscan show -vserver $VserverName"
$Command2 = "vscan scanner-pool show -instance -vserver $VserverName"
$Command3 = "vserver vscan on-access-policy show -vserver $VserverName"
$Command4 = "vscan connection-status show"

# Login to the filesystem and run the Above Commands:

ssh $Username@$FSxManagementIP "$Command1;$Command2;$Command3;$Command4"