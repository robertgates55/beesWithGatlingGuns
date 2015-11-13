#!/bin/bash
echo "Kill any previously running gatling instances"
kill -9 `ps -aef | grep 'gatling' | grep -v grep | awk '{print $2}'`
