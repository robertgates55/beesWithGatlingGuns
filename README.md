# beesWithGatlingGuns
Designed to fire up an array of AWS instances, and then execute a gatling script remotely on them.

You'll need to:
 - have python installed
 - install boto3
 - aws configure (and enter your user details)
 - put your .pem file somewhere & update the .py scripts to point to it
 - make sure the 'type' attribute of your target aws instances [add it as a label if it doesn't exist] matches what's in the aws script

then run 'python awsStartGatling.py 1000' to start with 1000 users distributed across your aws instances. The script will move the gatling home folder from the controller to all the agents (or 'bees'), then run the gatling.sh command on each of them. It'll run the default configuration, so aim to only have 1 so the script knows which to start.
