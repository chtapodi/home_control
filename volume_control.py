from __future__ import print_function
import time
import sys
import pychromecast


#Provided by this friendly person https://www.reddit.com/r/googlehome/comments/8b0b4o/python_script_to_manage_the_volume_of_multiple/
# Find Devices
print ("-- Discovering Devices\n")
chromecasts = pychromecast.get_chromecasts()

device_map={"titan":-23,
			"rhea":-4,
			"lapetus":14,
			"enceladus":18
}

mid_vol=50
vol_list=[]

#This gets the average volume of the devices in the room
for device in chromecasts:
	if device.device.friendly_name in device_map: #if its one of mine
		time.sleep(1)
		device.wait()
		vol_list.append(int(device.status.volume_level*100))
#actually calculates the avages, defaults to 50% if theres something wrong
try:
	mid_vol=sum(vol_list)/len(vol_list)
except:
	pass

for device in chromecasts:
	#This actually applies the scaled volumes
	if device.device.friendly_name in device_map: #if its one of mine
		# These sleeps seem necessary.
		time.sleep(1)
		device.wait()
		new_vol=(device_map.get(device.device.friendly_name)+mid_vol)/100
		if new_vol>1 :
			new_vol=1
		elif new_vol<0 :
			new_vol=0
		device.set_volume(new_vol)
		time.sleep(1)
		print("set {0} to {1}".format(device.device.friendly_name, new_vol*100))


# Apparently needed so the script can terminate cool
time.sleep(1)
