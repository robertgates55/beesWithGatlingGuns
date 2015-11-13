import boto3
import subprocess
import time
import sys

awsUser = "ec2-user"
pemLocation = "~/perimeterAwsKey.pem"
instanceTag="micro"
agentGatlingHome= "/home/" + awsUser + "/gatling/"
controllerGatlingHome="/home/" + awsUser + "/gatling/"
resultsFolderName=sys.argv[1]

print resultsFolderName

print "#####################################"
print "Getting agent IP Addresses"
print "#########################"
ec2 = boto3.resource('ec2')

running_instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:type', 'Values': [instanceTag]}, {'Name': 'instance-state-name', 'Values': ['running']}])

ip_addresses = []
for running_instance in running_instances:
    print "Found instance " + running_instance.instance_id + " is up and running at IP " + running_instance.public_ip_address
    ip_addresses.append(running_instance.public_ip_address)

print "#########################"
print "Agent IPs identified"
print "#####################################"
print ""
print ""

print "#####################################"
print "Fetching results from " + str(len(ip_addresses))+ " agents"
print "#########################"
subprocess.call("mkdir -p " + controllerGatlingHome + resultsFolderName, shell=True)
for ip_address in ip_addresses:
    print "#####" + ip_address + "#####"

    print "Expecting .log file in " + agentGatlingHome + "/results/" + resultsFolderName + "/*/"
    localCopyCommand = "find " + agentGatlingHome + resultsFolderName + " -name 'simulation.log' -exec \cp -f -t " + agentGatlingHome + resultsFolderName + " '{}' + "
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  localCopyCommand
    print sshCommand
    subprocess.call(sshCommand, shell=True)   

    fetchCommand = agentGatlingHome + resultsFolderName + "/simulation.log" + " " + \
                     controllerGatlingHome + resultsFolderName + "/" + str(ip_address).replace('.','') + "simulation.log"
    scpCommand = "scp -q -r -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + ":" + \
                  fetchCommand
    subprocess.call(scpCommand, shell=True)

print "#########################"
print "Test files MOVED"
print "#####################################"
print ""


print "#####################################"
print "Processing Results"
print "#########################"
subprocess.call(controllerGatlingHome + "/bin/gatling.sh -ro " + resultsFolderName.replace('results/',''), shell=True)
subprocess.call("sudo service nginx restart",shell=True)
print "#########################"
print "Results Processed"
print "#####################################"


