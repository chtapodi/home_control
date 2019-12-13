from __future__ import print_function
import time
import sys
import pychromecast
 

#Provided by this friendly person https://www.reddit.com/r/googlehome/comments/8b0b4o/python_script_to_manage_the_volume_of_multiple/ 
# Find Devices
print ("-- Discovering Devices\n")
chromecasts = pychromecast.get_chromecasts()
 
for device in chromecasts:
# Check if a device is a Chromecast.
    if device.model_name != "Chromecast":
# These sleeps seem necessary.
        time.sleep(1)
        device.wait()
        print(str(device))
        print("-- Current Volume: {0}%".format(int(device.status.volume_level*100)))
        print("-- Setting Night Volume to 10%...")
        device.set_volume(.1)
        time.sleep(1)
        print("-- New Volume: {0}%\n".format(int(device.status.volume_level*100)))
# If device is a Chromecast and will not set volume
    else:
        device.wait()
        print(str(device))
        print("-- Current Volume: {0}%".format(int(device.status.volume_level*100)))       
        print("-- Device is a Chromecast, leaving it alone...\n")
 
# Apparently needed so the script can terminate cool
time.sleep(1)
