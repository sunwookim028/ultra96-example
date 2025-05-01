#!/bin/bash

# Note: This script requires the sshpass command.

# list of ultra96-board IPs
BORAD_IPS=(\
"132.236.59.63" \
"132.236.59.64" \
"132.236.59.68" \
"132.236.59.70" \
"132.236.59.71" \
"132.236.59.72" \
"132.236.59.75" \
"132.236.59.76" \
"132.236.59.77" \
"132.236.59.80" \
)

# Check that required env vars are set
if [ -z "$ULTRA96_PASSWD" ]; then
    echo "Error: ULTRA96_PASSWD environment variables must be set."
    echo "Please set them by 'export ULTRA96_PASSWD=<password>'"
    exit 1
fi

timeout=3

# Loop through IPs
for ip in "${BORAD_IPS[@]}"; do

    sshpass -p $ULTRA96_PASSWD ssh -q -o StrictHostKeyChecking=no -o ConnectTimeout=$timeout xilinx@$ip exit

    if [ $? -eq 0 ]; then
        echo "$ip: Up and running"
    else
        echo "$ip: Unable to connect in $timeout seconds"
    fi
done
