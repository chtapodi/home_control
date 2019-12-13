from __future__ import print_function
import time
import sys
import pychromecast
import math
import matplotlib.pyplot as plt



#[coordinates, max_distance]
#The units do not matter as long as they are all the same
# device_settings={"titan":[[3,0],20],
# 			"rhea":[[5,3],15],
# 			"lapetus":[[2,5],15],
# 			"enceladus":[[3,8],15]
# }

#[coordinates, max_distance]
#The units do not matter as long as they are all the same
device_settings={"ceres":[[0,0],20],
			"Kitchen display":[[20,5],15],
			"Family Room TV":[[0,12],25]
}
## TODO: Read this in from a config file

connected_devices={}

def connect() :
	chromecasts = pychromecast.get_chromecasts()
	for device in chromecasts:
		#This actually applies the scaled volumes
		name=device.device.friendly_name
		if name in device_settings: #if its one of mine
			connected_devices[name]=device
			# print("connected to ", device)


#equalizes all devices to coordinates
#returns the percentage that everything should be equalized to
def equalize_to_point(vol_mult, point) :
	for name in connected_devices :
		device=connected_devices[name]
		#distance to device
		coords=get_device_coords(name)
		device_dist=get_dist(coords, point)
		new_vol=device_vol_scale(name, device_dist, vol_mult)
		set_vol(device, new_vol)


#Returns the volume of the device to center at the point in relation to the volume multiplier
def device_vol_scale(name, distance, vol_mult):
	device_max_dist=get_max_dist(name)

	#This uses a linear relationship, I may update this to be logarithmic
	new_vol=translate(distance, 0, device_max_dist,0,1)
	print("vol for ", name, " ", new_vol)

	scaled_vol=new_vol*vol_mult
	print("scaled vol", scaled_vol)
	return scaled_vol



#gets the volume from a device, 0.0->1.0
def get_device_vol(device) :
	# print('\n',device)
	device.wait()
	vol=device.status.volume_level
	return vol


#gets the coordinates of a device from it's name
def get_device_coords(name) :
	return device_settings.get(name)[0]


#gets the max distance param, which represents the distance at which 100% sounds like a good value for 100%
def get_max_dist(name) :
	dist=device_settings.get(name)[1]
	return dist

#gets the distance between two coords
def get_dist(coord_a, coord_b) :
	x_diff=coord_a[0]-coord_b[0]
	y_diff=coord_a[1]-coord_b[1]
	return math.sqrt(x_diff**2 +y_diff**2)

#sets the volume of a device
def set_vol(device, vol) :
	device.wait()
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

#prints out a vague visualization of volume.
def text_visualize(name, ratio) :
	index=int(ratio*10)
	to_print=[]
	for i in range(0,10) :
		if (i==index) :
			to_print.append("X")
		else :
			to_print.append("#")
	to_print= ''.join(to_print)
	print("{}\t".format(to_print), name)


#Graphs volume representations and locations of devices, good for troubleshooting
def visualize(point)  :
	fig, ax = plt.subplots(1, 1)
	plt.ylim(0,20)
	plt.xlim(0,20)
	plt.gca().set_aspect('equal', adjustable='box')
	plt.grid(linestyle='-', linewidth=1)
	for name in connected_devices :
		device=connected_devices[name]
		vol=get_device_vol(device)
		coords=coords=get_device_coords(name)
		device_max_dist=get_max_dist(name)

		radius=translate(vol,0,1, 0, device_max_dist)

		circle1=plt.Circle(coords,radius, fill=False)

		plt.gcf().gca().add_artist(circle1)

	plt.scatter(point[0],point[1])
	plt.savefig("graph.png")



def main() :
	#This is a placeholder until I have a dynamic method for tracking my location
	#START
	connect()
	vol_mult=.6
	point=[7,5] #about where I sit in the kitchen
	equalize_to_point(vol_mult, point)
	visualize(point)
	time.sleep(1)



if __name__ == "__main__":
	# execute only if run as a script
	main()
