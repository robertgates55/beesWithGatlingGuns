import boto3
import subprocess


testTag="micro"


ec2 = boto3.resource('ec2')

test_instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:type', 'Values': [testTag]}])

ip_addresses = []
for test_instance in test_instances:
    ip_addresses.append(test_instance.public_ip_address)

for test_instance in test_instances:
    print "Stopping " + test_instance.instance_id + " ..."
    test_instance.stop()

for test_instance in test_instances:
    print "Waiting for " + test_instance.instance_id + " to stop..."
    test_instance.wait_until_stopped()
