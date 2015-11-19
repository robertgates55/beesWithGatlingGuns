import boto3
import subprocess
import time
import sys
from webSecSoap import addIpAddressesToSite

awsUser = "ec2-user"
pemLocation = "/home/" + awsUser + "/perimeterAwsKey.pem"
instanceTag="micro"
resultsFolderName="results/awsGatling" + str(time.time()).replace('.','')
agentGatlingHome= "/home/" + awsUser + "/gatling/"
controllerGatlingHome="/home/" + awsUser + "/gatling/" 

totalUsers=1000 #default
runDuration=60 #default
maxInstances=20 #default
args = sys.argv[1:]
if len(args) > 0 :
 totalUsers = int(args[0])
if len(args) > 1 :
 runDuration=int(args[1])
if len(args) > 2 :
 maxInstances=int(args[2])

typeToMem = {'t2.micro': '750m','t2.medium': '3g', 't2.large': '7g'}
typeToCores = {'t2.micro': 1, 't2.medium': 4, 't2.large': 4}

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

all_test_instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:type', 'Values': [instanceTag]}])

test_instances=[]
instances_to_stop=[]
for inst in all_test_instances :
  if len(test_instances) < maxInstances :
    test_instances.append(inst)
  else:
    instances_to_stop.append(inst)

print ""
print "#####################################"
print "Bringing up " + str(maxInstances) + " AWS instances with 'type' tag of `" + instanceTag + "` (and stopping the rest)"
print "#########################"

for test_instance in test_instances:
    if test_instance.state['Name'] != "running":
        print "Starting " + test_instance.instance_id + "..."
        test_instance.start()

for test_instance in instances_to_stop:
    print "Stopping " + test_instance.instance_id + "..."
    test_instance.stop()

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

print "#####################################"
print "Adding IP Addresses to web Sec via API"
print "#########################"
addIpAddressesToSite(47,"AWS Test Array",ip_addresses)
print "#########################"
print ""
print "#####################################"

print ""

print "#####################################"
print "Moving the test files to " + str(len(ip_addresses))+ " instances"
print "#########################"
for running_instance in running_instances:
    ip_address = running_instance.public_ip_address
    print "#####" + ip_address + "#####"

    createCommand = "mkdir " + agentGatlingHome
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  createCommand
    subprocess.call(sshCommand, shell=True)

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
                  " -i " + pemLocation + "' " + \
                  "--exclude={,'/target','*.txt','*.git','/results','/bin','/lib'} " + \
                  controllerGatlingHome + "/* " + \
                  awsUser + "@" + ip_address + ":" + \
                  agentGatlingHome
    print rsyncCommand
    subprocess.call(rsyncCommand, shell=True)   

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
                  " -i " + pemLocation + "' " + \
                   "./startGatlingRemotely.sh " + \
                  awsUser + "@" + ip_address + ":" + \
                  "/home/" + awsUser
    print rsyncCommand
    subprocess.call(rsyncCommand, shell=True) 

    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
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

    commandToRun = "sh /home/" + awsUser + "/startGatlingRemotely.sh " + resultsFolderName + " " + \
                  typeToMem[running_instance.instance_type] + " " + \
                  str(instanceUsers) + " " + str(runDuration)
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  commandToRun
    subprocess.call(sshCommand, shell=True)              
    print ""

print "#########################"
print "Instances STARTED"
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
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ConnectionAttempts=3" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  commandToRun
    subprocess.call(sshCommand, shell=True)
    print ""

print "#########################"
print  "Instances RUNNING"
print "#####################################"


print ""
print "#####################################"
print "Script is running on " + str(len(ip_addresses)) + " instances"
print "Running in folder: " + resultsFolderName + " (and have created results folder here)"
subprocess.call("mkdir -p " + controllerGatlingHome + resultsFolderName, shell=True)
print "Run `python awsGatlingFetchResults.py " + resultsFolderName + "` to process the results."
print "#####################################"
