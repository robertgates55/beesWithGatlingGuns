import boto3
import subprocess
import time
import sys

awsUser = "ec2-user"
pemLocation = "/home/" + awsUser + "/perimeterAwsKey.pem"
instanceTag="micro"
resultsFolderName="results/awsGatling" + str(time.time()).replace('.','')
agentGatlingHome= "/home/" + awsUser + "/gatling/"
controllerGatlingHome="/home/" + awsUser + "/gatling/" 
totalUsers = int(sys.argv[1])
print str(totalUsers)

typeToMem = {'t2.micro': '750m', '2x.xlarge': '3g'}
typeToCores = {'t2.micro': 1, '2x.xlarge': 4}

print "#####################################"
print ""
print "#########################"
print "AWS + Gatling"
print "Remote Runner StartUp Script"
print "Rob Gates - Nov 2015"
print "#########################"
print ""
print "#####################################"


ec2 = boto3.resource('ec2')

test_instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:type', 'Values': [instanceTag]}])

print ""
print "#####################################"
print "Bringing up the AWS instances with 'type' tag of `" + instanceTag + "`"
print "#########################"

for test_instance in test_instances:
    if test_instance.state['Name'] != "running":
        print "Starting " + test_instance.instance_id + "..."
        test_instance.start()

for test_instance in test_instances:
    print "Waiting for " + test_instance.instance_id + "..."
    test_instance.wait_until_running()

running_instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:type', 'Values': [instanceTag]}, {'Name': 'instance-state-name', 'Values': ['running']}])

ip_addresses = []
totalCoresRunning = 0
for running_instance in running_instances:
    print "Found instance " + running_instance.instance_id + " is up and running at IP " + running_instance.public_ip_address
    ip_addresses.append(running_instance.public_ip_address)
    totalCoresRunning += typeToCores[running_instance.instance_type]
print "#########################"
print "AWS Instances UP - " + str(len(ip_addresses)) + " instances, " + str(totalCoresRunning) + " total cores"
print "#####################################"
print ""


print ""


print "#####################################"
print "Moving the test files to " + str(len(ip_addresses))+ " instances"
print "#########################"
for running_instance in running_instances:
    ip_address = running_instance.public_ip_address
    print "#####" + ip_address + "#####"

    createCommand = "mkdir " + agentGatlingHome
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  createCommand
    subprocess.call(sshCommand, shell=True)

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + "' " + \
                  "--exclude={,'/target','*.txt','*.git','/results','/bin','/lib'} " + \
                  controllerGatlingHome + "/* " + \
                  awsUser + "@" + ip_address + ":" + \
                  agentGatlingHome
    print rsyncCommand
    subprocess.call(rsyncCommand, shell=True)   

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + "' " + \
                   "./startGatlingRemotely.sh " + \
                  awsUser + "@" + ip_address + ":" + \
                  "/home/" + awsUser
    print rsyncCommand
    subprocess.call(rsyncCommand, shell=True) 

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + "' " + \
                   "./checkGatlingStatus.sh " + \
                  awsUser + "@" + ip_address + ":" + \
                  "/home/" + awsUser
    subprocess.call(rsyncCommand, shell=True)

print "#########################"
print "Test files MOVED"
print "#####################################"


print ""


print "#####################################"
print "Running the gatling start script on " + str(len(ip_addresses)) + " instances"
print "#########################"

for running_instance in running_instances:
    ip_address = running_instance.public_ip_address
    print "#####" + ip_address + "#####"
    instanceUsers = int(round(totalUsers * (float(typeToCores[running_instance.instance_type]) / float(totalCoresRunning)),0))

    commandToRun = "sh /home/" + awsUser + "/startGatlingRemotely.sh " + resultsFolderName + " " + typeToMem[running_instance.instance_type] + " " + str(instanceUsers)
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  commandToRun
    subprocess.call(sshCommand, shell=True)              
    print ""

print "#########################"
print "jmeter-server instances STARTED"
print "#####################################"

print ""

print "#####################################"
print "Checking gatling status on " + str(len(ip_addresses)) + " instances"
print "#########################"
time.sleep(1)

for running_instance in running_instances:
    ip_address = running_instance.public_ip_address
    print "#####" + ip_address + "#####"

    commandToRun = "sh /home/" + awsUser + "/checkGatlingStatus.sh"
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  commandToRun
    subprocess.call(sshCommand, shell=True)
    print ""

print "#########################"
print "jmeter-server instances RUNNING"
print "#####################################"


print ""
print "#####################################"
print "Script is running on " + str(len(ip_addresses)) + " instances"
print "Running in folder: " + resultsFolderName
print "Run `python awsGatlingFetchResults.py " + resultsFolderName + "` to process the results."
print "or `watch python awsGatlingFetchResults.py " + resultsFolderName + " -n60` to fetch and process every 60s."
print "#####################################"
