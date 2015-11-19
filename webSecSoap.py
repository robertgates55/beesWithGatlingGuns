from suds.client import Client
from suds.transport.https import HttpAuthenticated
import ssl
import time
import logging
from suds.sax.element import Element

#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

#ssl hack to allow connection out
if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context

#set wsdl location (use shell script to get wsdl, fix bool>boolean issue, and save locally)
url='file:///home/ec2-user/tempWSDL.wsdl'

#create client
client = Client(url)

#Custom Header
ssn = Element('ownerID').setText('0')
client.set_options(soapheaders=ssn)

def addIpAddressesToSite(ispId,siteName,ipAddresses) :

 #call adminAuthenticate
 timeout = int(time.time()+1000)
 auth=client.service.adminAuthenticate("perftestuser","08f5b04545cbf7eaa238621b9ab84734","1.1.1.1",timeout)
 
 #if +ve response from authenticate, continue
 if auth.retcode == 0 :
   print "Successfully logged in"
   sessionId=auth.data
   accountId=0

   id = dict(name="id",data=0)
   isp = dict(name="isp",data=ispId)
   site = dict(name="name",data=siteName)
   type = dict(name="type",data=3)
   data = [id,isp,site,type]
   
   addSite = client.service.policySet(sessionId,accountId,data)
 
 #if +ve response from add site (or it already exists [2], continue
 if addSite.retcode == 0 or addSite.retcode == 2 :
   print "Successfully added/updated site '" + str(siteName) + "' with siteId '" + addSite.data + "' on provider ID '" + str(ispId) + "'"
   siteId=addSite.data

   i=1
   for ipAddress in ipAddresses :
     ipData = client.factory.create('ns1:IPAddress')
     ipData.id=siteId
     ipData.ip=ipAddress
     ipData.action=1
     ipData.name="AWS "+str(i)
     addIp = client.service.policyIPSet(sessionId,ipData)
     i+=1
     if addIp.retcode == 0 :
       print "Successfully added " + ipData.ip + " as IP named " + ipData.name
     elif addIp.retcode ==3 :
       print ipData.ip + " already added"
     else:
       print "Failed to add " + ipData.ip + " as IP named " + ipData.name
 print "All done"
 print client.service.policyIPList(sessionId,siteId)
 return


#addIpAddressesToSite(47,"Perf Site",["1.2.1.1","1.2.1.2"])

