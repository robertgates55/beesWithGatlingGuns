#!/bin/bash
if [ $(ps aux | grep Gatling | grep java |  head -n 1 | wc -l) -eq 1 ]; then echo "Running"; else echo "FAILED TO START"; fi
