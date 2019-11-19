from __future__ import print_function
import time
import sys
import pychromecast
import math

#Provided by this friendly person https://www.reddit.com/r/googlehome/comments/8b0b4o/python_script_to_manage_the_volume_of_multiple/
# Find Devices


base_speaker="titan"
device_map={"titan":0,
			"rhea":26,
			"lapetus":48,
			"enceladus":40
}

#[dist, slope, offset]
func_map={"titan":[1.41, 0.323, 43.6],
			"rhea":[2.23, 0.236, 43.4],
			"lapetus":[4.47, 0.236, 41.0],
			"enceladus":[7.07, 0.236, 30]
}


coord_map={"titan":[3,0],
			"rhea":[5,3],
			"lapetus":[2,5],
			"enceladus":[3,8]
}

mid_vol=50
vol_list=[]

connected_devices={}
titan=-1
prev_vol=0

def connect() :
	global titan
	chromecasts = pychromecast.get_chromecasts()
	for device in chromecasts:
		#This actually applies the scaled volumes
		name=device.device.friendly_name
		if name in device_map: #if its one of mine
			connected_devices[name]=device
			print(device)
			if name ==base_speaker: #if its one of mine
				print("confirmed")
				titan=device

#equalizes all devices to coordinates
#returns the percentage that everything should be equalized to
def equalize_to_point(base_speaker, vol, point) :
	base_dist=get_dist(coord_map.get(base_speaker), point)
	base_db=get_db_at_dist(base_speaker, vol, base_dist)
	base_percent=get_device_vol(connected_devices.get(base_speaker))
	for device in connected_devices.values() :
		name=device.device.friendly_name
		# if (name!=base_speaker) :
		device_dist=get_dist(coord_map.get(name), point)
		# percent=get_percent_at_dist(name, base_percent, device_dist)
		percent=map_db_to_dist(device_dist,base_percent, base_dist)
		print("{0}: {1}%, {2}d".format(name, percent, device_dist))
		set_vol(device, percent)
		print("\n")




#gets the db from volume at percent
def get_percent_at_dist(name, db, dist) :
	base_dist=get_base_dist(name)
	slope=get_base_slope(name)
	offset=calc_offset(dist)
	print("%@d offset", offset)

	percent=get_equiv_percent(db, slope, offset)

	mapped_percent=map_db_to_dist(dist, percent, base_dist)

	print("%@d percent", percent)
	print("%@d mapped percent", mapped_percent)
	return percent


def calc_offset(dist) :
	return (-0.653*dist)**2+3.3*dist+39.3


#gets the db from volume at percent
def get_db_at_dist(name, percent, dist) :
	base_dist=get_base_dist(name)
	slope=get_base_slope(name)
	offset=get_base_offset(name)
	base_db=get_base_db(percent, slope, offset)

	db=map_db_to_dist(dist, base_db, base_dist)
	# print("db@d %", percent)
	# print("db@d db", db)
	# print("base db", base_db)
	return db



def map_db_to_dist(dist,to_map, base_dist) :
	return ((base_dist/dist)**2)*to_map

#gets the volume from a device
def get_device_vol(device) :
	# print('\n',device)
	device.wait()
	vol=int(device.status.volume_level*100)
	return vol

#gets the base distance param
def get_base_dist(name) :
	return func_map.get(name)[0]

#gets the base offset param
def get_base_offset(name) :
	return func_map.get(name)[2]

#gets the base slope param
def get_base_slope(name) :
	return func_map.get(name)[1]

#gets the base volume at a percentage
def get_base_db(percent, slope, offset) :
	return percent*slope + offset

#gets the base volume at a percentage
def get_equiv_percent(db, slope, offset) :
	return (db-offset)/slope

#gets the distance between two coords
def get_dist(coord_a, coord_b) :
	x_diff=coord_a[0]-coord_b[0]
	y_diff=coord_a[1]-coord_b[1]
	return math.sqrt(x_diff**2 +y_diff**2)

#sets the volume of a device
def set_vol(device, vol) :
	device.wait()
	vol=vol/100
	# time.sleep(1)
	if vol>1 :
		vol=1
	elif vol<0 :
		vol=0
	device.set_volume(vol)


#taken from https://stackoverflow.com/a/1969274 because google is faster than memory
#scales from one range of values to another
def translate(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan)
	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

def visualize(name, ratio) :
	index=int(ratio*10)
	to_print=[]
	for i in range(0,10) :
		if (i==index) :
			to_print.append("X")

		else :
			to_print.append("#")
	to_print= ''.join(to_print)
	print("{}\t".format(to_print), name)



#START
connect()
# while True :
point=[4,1] #desk
point=[3,7] #bedroom
point=[2,4]
vol=get_device_vol(connected_devices.get(base_speaker))
equalize_to_point(base_speaker, vol, point)
	# if vol!=prev_vol :
	# 	print("new baseline ", vol)
	# 	prev_vol=vol
	# 	equalize_to_point(base_speaker, vol, point)
	# 	print("\n")





time.sleep(1)
