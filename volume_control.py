from __future__ import print_function
import time
import argparse
import sys
import readchar
import pychromecast
import math
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Controls volume foci of google devices')

parser.add_argument('-v', action="store", dest="volume", type=float, help='directly input a volume : 0-100')

parser.add_argument('-i', action="store_true", dest="interactive", default=False, help='interactive mode, lets you adjust volume and reposition')

parser.add_argument('-l', action="store_true", dest="loop", default=False, help='loop mode, continually attempts to adjust volume')



parser.add_argument('-p', '--position', nargs=2, metavar=('x', 'y'), help='Allows the input of a new point, syntax is x y')

parser.add_argument('-s', '--scan', action="store_true", dest="scan", default=False, help='Lists all detected cast device')


args = parser.parse_args()


#[coordinates, max_distance]
#The units do not matter as long as they are all the same
# device_settings={"titan":[[3,0],20],
# 			"rhea":[[5,3],15],
# 			"lapetus":[[2,5],15],
# 			"enceladus":[[3,8],15]
# }

#[coordinates, max_distance]
# #The units do not matter as long as they are all the same
# device_settings={"ceres":[[0,0],20],
# 			"Kitchen display":[[20,5],15],
# 			"Family Room TV":[[0,12],15]
# }


#[coordinates, max_distance]
#The units do not matter as long as they are all the same
device_settings={"titan":[[7,0],25],
			"janus & epimetheus":[[4,7],15],
			"Ledge":[[4,23],15]
}


## TODO: Read this in from a config file

connected_devices={}

def connect() :

	chromecasts = pychromecast.get_chromecasts()
	for device in chromecasts:
		#This actually applies the scaled volumes
		name=device.device.friendly_name
		if args.scan :
			print( "Detected ", name)
		if name in device_settings: #if its one of mine
			connected_devices[name]=device
			print("connected to {0}/{1}".format(len(connected_devices), len(device_settings)))


#equalizes all devices to coordinates
#returns the percentage that everything should be equalized to
def equalize_to_point(vol_mult, point) :
	for name in connected_devices :
		device=connected_devices[name]
		#distance to device
		device_dist=get_device_dist(name, point)

		new_vol=device_vol_scale(name, device_dist, vol_mult)
		set_vol(device, new_vol)


#Returns the volume of the device to center at the point in relation to the volume multiplier
def device_vol_scale(name, distance, vol_mult):
	device_max_dist=get_max_dist(name)

	#This uses a linear relationship, I may update this to be logarithmic
	new_vol=translate(distance, 0, device_max_dist,0,1)
	scaled_vol=new_vol*vol_mult
	return scaled_vol


#calculates the vol mult from a device
def get_device_vol_mult(name, point) :
	device=connected_devices[name]
	device_dist=get_device_dist(name, point)
	device_max_dist=get_max_dist(name)
	calc_vol=translate(device_dist, 0, device_max_dist,0,1)
	real_vol=get_device_vol(device)
	estimated_mult=real_vol/calc_vol
	return estimated_mult

#determines a base multiplier
def get_base_mult(point) :
	#finds the closest device to the point
	closest=None
	min_dist=sys.maxsize #all distances will be less than this
	for name in connected_devices :
		dist=get_device_dist(name, point)
		if min_dist>dist :
			min_dist=dist
			closest=name
	#estimates the mult val for this device.
	closest_mult=get_device_vol_mult(closest, point)
	print(closest)
	return closest_mult



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

def get_device_dist(name, point) :
	coords=get_device_coords(name)
	return get_dist(coords, point)

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


def interactive_mode(point, vol_mult) :
	print("entering interactive mode")
	if args.loop==False :
		print("q & e control volume")
	else :
		print("loop mode is activated, this will only update when position is updated")
	print("wasd controls location")
	print("c exits")
	x=point[0]
	y=point[1]
	while True :
		try :
			key=readchar.readkey()
			if key=='w' : #point up
				y+=1
			elif key=='s' : #point down
				y-=1
			elif key=='a' : #point left
				x-=1
			elif key=='d' : #point right
				x+=1
			elif key=='c' :
				break

			if args.loop==False :
				if key=='e' :#volume up
					vol_mult+=.05
				elif key=='q' : #volume down
					vol_mult-=.05
			else :
				base_mult=get_base_mult([x,y])
				if base_mult!=vol_mult :
					vol_mult=base_mult
					equalize_to_point(vol_mult, [x,y])

			print("[{0},{1}]:{2:3f}".format(x,y, vol_mult))
			equalize_to_point(vol_mult, [x,y])
			time.sleep(.1)

		except KeyboardInterrupt:
			pass


def main() :
	#This is a placeholder until I have a dynamic method for tracking my location
	#START
	point=[7,5] #about where I sit in the kitchen



	#connects to devices
	connect()


	#if a volume is provided via command line, use it, otherwise use volume of closest device
	vol_mult=get_base_mult(point)

	if args.volume!=None :
		vol_mult=args.volume/100

	#if a single position is being passed in as a point
	if args.position!=None :
		point=[float(args.position[0]),float(args.position[1])]
		print("point ", point)


	#interactive mode
	if args.interactive :
		interactive_mode(point, vol_mult)
	elif args.loop :
		print("entering loop mode")
		try :
			while True :
				base_mult=get_base_mult(point)
				if base_mult!=vol_mult :
					vol_mult=base_mult
					equalize_to_point(vol_mult, point)

		except KeyboardInterrupt:
			pass

	else :
		equalize_to_point(vol_mult, point)
		# visualize(point)



if __name__ == "__main__":
	# execute only if run as a script
	main()
