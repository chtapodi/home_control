from __future__ import print_function
import time
import sys
import pychromecast


#Provided by this friendly person https://www.reddit.com/r/googlehome/comments/8b0b4o/python_script_to_manage_the_volume_of_multiple/
# Find Devices
print ("-- Discovering Devices\n")
chromecasts = pychromecast.get_chromecasts()

base_speaker="titan"
device_map={"titan":0,
			"rhea":16,
			"lapetus":34,
			"enceladus":40
}

mid_vol=50
vol_list=[]

connected_devices=[]
titan=-1
prev_vol=0

def connect() :
	global titan
	for device in chromecasts:
		#This actually applies the scaled volumes
		if device.device.friendly_name in device_map: #if its one of mine
			connected_devices.append(device)
			print(device)
			if device.device.friendly_name ==base_speaker: #if its one of mine
				print("confirmed")
				titan=device


def get_vol(device) :
	# print('\n',device)
	device.wait()
	vol=int(device.status.volume_level*100)
	return vol


def set_vol(device, vol) :
	device.wait()
	# time.sleep(1)
	if vol>1 :
		vol=1
	elif vol<0 :
		vol=0
	device.set_volume(vol)


def equalize_devices(vol) :
	for device in connected_devices :
		name=device.device.friendly_name
		modifier=device_map.get(name)
		modified=(modifier+vol)
		new_vol=modified/100
		set_vol(device, new_vol)
		# print("set {0} to {1}".format(name, new_vol))
		visualize(name, new_vol)


def visualize(name, ratio) :
	index=int(ratio*10)
	to_print=[]
	for i in range(10) :
		if (i==index) :
			to_print.append("X")

		else :
			to_print.append("#")
	to_print= ''.join(to_print)
	print("{}\t".format(to_print), name)


if __name__ == "__main__":
#START
	connect()
	while True :
		vol=get_vol(titan)

		if vol!=prev_vol :
			print("\n")
			equalize_devices(vol)
			prev_vol=vol


main()


#
# for device in chromecasts:
# 	if device.device.friendly_name =="titan": #if its one of mine
# 		time.sleep(1)
# 		device.wait()
# 		mid_vol=int(device.status.volume_level*100)-device_map.get(device.device.friendly_name) #generates a middle based on titan volume
#
# for device in chromecasts:
# 	#This actually applies the scaled volumes
# 	if device.device.friendly_name in device_map: #if its one of mine
# 		# These sleeps seem necessary.
# 		time.sleep(1)
# 		device.wait()
# 		new_vol=(device_map.get(device.device.friendly_name)+mid_vol)/100
# 		if new_vol>1 :
# 			new_vol=1
# 		elif new_vol<0 :
# 			new_vol=0
# 		device.set_volume(new_vol)
# 		time.sleep(1)
# 		print("set {0} to {1}".format(device.device.friendly_name, new_vol*100))
#

# Apparently needed so the script can terminate cool
time.sleep(1)
