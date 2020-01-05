#!/bin/bash

if ! pgrep -f 'volume_control.py'
then

     python3 /home/chtapodi/spacial_volume_control/volume_control.py -l & >/dev/null
# run the test, remove the two lines below afterwards
else
    echo "running"

fi
