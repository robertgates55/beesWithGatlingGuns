#set wsdl location (use local to fix bool>boolean issue)
rm tempWSDL.wsdl
wsdlUrl='https://sss01-qa-fra02.streamshield.net/server/sss.php?wsdl'
wget $wsdlUrl --no-check-certificate -O tempWSDL.wsdl
sed -i "s/xsd:bool\"/xsd:boolean\"/g" tempWSDL.wsdl
