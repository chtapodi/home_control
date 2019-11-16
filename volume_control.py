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




#gets the db from volume at percent
def get_percent_at_dist(name, db, dist) :
	base_dist=get_base_dist(name)
	slope=get_base_slope(name)
	equiv_db=db/((base_dist/dist)**2)
	percent=get_equiv_percent(equiv_db, slope, offset)
	return percent


#gets the db from volume at percent
def get_db_at_dist(name, percent, dist) :
	base_dist=get_base_dist(name)
	slope=get_base_slope(name)
	base_db=get_base_db(percent, slope, base_dist)
	db=((base_dist/dist)**2)*base_db
	return db




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
	return sqrt(x_diff**2 +y_diff**2)

#sets the volume of a device
def set_vol(device, vol) :
	device.wait()
	# time.sleep(1)
	if vol>1 :
		vol=1
	elif vol<0 :
		vol=0
	device.set_volume(vol)

def equalize_to_point(coords) :
	reference_vol=
	for

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



#START
connect()
while True :
	vol=get_device_vol(titan)

	if vol!=prev_vol :
		print("\n")
		equalize_devices(vol)
		prev_vol=vol




time.sleep(1)
