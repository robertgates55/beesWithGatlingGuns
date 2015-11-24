import boto3
import subprocess
import time


awsUser = "ec2-user"
pemLocation = "/home/ec2-user//perimeterAwsKey.pem"
instanceTag="agent"
agentGatlingHome= "/home/" + awsUser + "/gatling/"
controllerGatlingHome="/home/" + awsUser + "/gatling/"

def runShellCommand(cmd):
  proc = subprocess.Popen(cmd,shell=True,bufsize=256, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  for line in proc.stdout:
    print(">>> " + str(line.rstrip()))
  return

print "#####################################"
print ""
print "#########################"
print "AWS + Gatling"
print "Remote Runner Stop Script"
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
for running_instance in running_instances:
    print "Found instance " + running_instance.instance_id + " is up and running at IP " + running_instance.public_ip_address
    ip_addresses.append(running_instance.public_ip_address)
print "#########################"
print "AWS Instances UP"
print "#####################################"
print ""


print "#########################"

for ip_address in ip_addresses:
    print "#####" + ip_address + "#####"



    rsyncCommand="rsync -rave 'ssh -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + "' " + \
                   "./stopGatlingRemotely.sh " + \
                  awsUser + "@" + ip_address + ":" + \
                  "/home/" + awsUser
    print rsyncCommand
    runShellCommand(rsyncCommand) 


    commandToRun = "sh /home/" + awsUser + "/stopGatlingRemotely.sh " + resultsFolderName + " " + heapSize
    sshCommand = "ssh -nq -o StrictHostKeyChecking=no" + \
                  " -i " + pemLocation + " " + \
                  awsUser + "@" + ip_address + " " + \
                  commandToRun
    runShellCommand(sshCommand)              
    print ""

print "#########################"




