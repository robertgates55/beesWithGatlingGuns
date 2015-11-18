#!/bin/bash

echo "Kill any previously running gatling instances"
kill -9 `ps -aef | grep 'gatling' | grep -v grep | awk '{print $2}'`

if [ ! -d "gatling/bin" ]; then
    echo "gatling not found (or not found where it was expected to be), so going to download/install and move bin, lib and conf to the gatling folder"
    wget https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/2.1.7/gatling-charts-highcharts-bundle-2.1.7-bundle.zip
    mkdir gatling
    unzip gatling-charts-highcharts-bundle-2.1.7-bundle.zip
    cp -r ./gatling-charts-highcharts-bundle-2.1.7/bin gatling
    cp -r ./gatling-charts-highcharts-bundle-2.1.7/lib gatling
    cp -r ./gatling-charts-highcharts-bundle-2.1.7/conf gatling
fi


userCountSearchString="val maxUserCount = "
if [ $3 ]; then
 maxUsers=$3
 find gatling/user-files/ -name *.scala -exec sed -i "s/$userCountSearchString[0-9]*/$userCountSearchString$maxUsers/g" {} \;
fi


runDuration="val testDuration = "
if [ $4 ]; then
 duration=$4
 find gatling/user-files/ -name *.scala -exec sed -i "s/$runDuration[0-9]* [a-z]*/$runDuration$duration minutes/g" {} \;
fi

defaultHeapSize="6G"
if [ $2 ]; then
 heapSize=$2
else
 heapSize=$defaultHeapSize
fi
gatlingBinary="/home/ec2-user/gatling/bin/gatling.sh"

sed -i "s/-Xms[0-9]*[A-Za-z]*/-Xms$(echo $heapSize)/g" $gatlingBinary
sed -i "s/-Xmx[0-9]*[A-Za-z]*/-Xmx$(echo $heapSize)/g" $gatlingBinary


ulimit -n 500000

echo "Starting gatling in background - $maxUsers users"
nohup sh $gatlingBinary -m -rf $1 > /dev/null 2>&1 &
