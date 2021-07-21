import time
import argparse
import sys
import readchar
import pychromecast
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


class volume_controller :

		def __init__(self, device_map, foci=None, show_plot=False, verbose=False) :
			self.verbose=verbose
			self.devices=device_map
			self.connect()

			# print(self.devices["Titan"])

			#if a foci is not assigned, use the middle of the room
			if foci!=None :self.foci=np.array(foci)
			else :
				points=[loc["location"] for loc in self.devices.values()]
				self.foci=np.mean(points,axis=0)
			self.min_vol=.2
			self.closest_vol=0 #This seems dumb but also will save a lot of computation
			self.closest_index=0 #def gotta fix

			self.closest_device=self.get_closest()

			# self.get_device_vector(self.devices["Titan"])

			# self.get_error()
			# self.adjust_vols([1,1,1,1])
			self.minimize_vols()

			if self.verbose:
				# for name,device in self.devices.items() :
				# 	print(name)
				# 	print(self.get_device_vol(device))
				print(self)
			if show_plot:
				self.plot_vectors()


		#interaction methods
		def get_foci(self) :
			return self.foci

		def set_foci(self,foci) :
			self.foci=np.array(foci)

		def vector_to_foci(self,foci) :
			self.set_foci(foci)
			self.minimize_vols()

		#Visualization operations-----------------
		def plot_vectors(self) :
			sum_point=[0,0]
			plt.figure()
			ax = plt.gca()
			for name,device in self.devices.items():
				vector=self.get_device_vector(device)
				mags=np.array(self.centralize_vector(vector))
				color_val=np.random.rand(3,)
				ax.quiver(sum_point[0], sum_point[1], mags[0], mags[1], color=color_val,angles='xy', scale_units='xy', scale=1,width=.005)
				sum_point=np.add(sum_point,mags)


				ax.scatter(vector[0], vector[1],c="black")
				#plot speakers
				ax.quiver(vector[0], vector[1], mags[0], mags[1], color=color_val,angles='xy', scale_units='xy', scale=1, label=str(name),width=.005)



			# ax.quiver(X, Y, Ux, Uy, angles='xy', scale_units='xy', scale=1, label=labels)
			ax.scatter(*self.foci,c="red")
			ax.scatter(*sum_point,c="black", label=np.linalg.norm(sum_point))
			ax.scatter([0],[0],c="black")
			ax.set_xlim([-10, 25])
			ax.set_ylim([-10, 25])
			plt.legend()
			plt.draw()
			plt.show()



		def __str__ (self,) :
			string=""
			for name,device in self.devices.items() :
				string+="{}:{}%\n".format(name,self.get_device_vol(device))
			return string

		#Minimization Operations------------------

		def minimize_vols(self) :
			init_vols=[.4 for device in self.devices.keys()]
			# self.closest_vol=np.clip(self.get_device_vol(self.closest_device),.4,1)
			self.closest_device=self.get_closest()
			# self.closest_vol=self.distance_to_volume(np.linalg.norm(self.foci-self.closest_device["location"])) #not convinced this is legit
			self.closest_vol=self.get_device_vol(self.closest_device)
			# print("closest device",self.closest_device["name"])

			if self. verbose :
				print("closest device volume ",self.closest_vol)


			bound_list=[(.35,1) for device in self.devices.keys()]
			res = minimize(self.adjust_vols, init_vols,method='nelder-mead',
			   options={'xatol': 1e-8, 'disp': True})

			if self. verbose :
				print("closest device volume ",self.closest_vol)
				print(res.x)
			for vol,device in  zip(res.x,self.devices.values()):
				self.set_device_vol(device,vol)

		def adjust_vols(self, vol_list) :
			# print(self.closest_index)
			vol_list[self.closest_index]=self.closest_vol
			return self.get_error(vol_list)

		def get_error(self, vol_list) : #returns summed vector error
			xsum=0
			ysum=0
			mag_diff=0
			vol_sum=0
			for device, vol in zip(self.devices.values(),vol_list) :
				np.clip(vol,.2,1)
				vector=self.centralize_vector(self.get_device_vector(device, hyp_vol=vol))

				vol_sum+=vol
				xsum+=vector[0]
				ysum+=vector[1]
				#This should penalize it for making the volumes too different
				mag_diff+=abs(self.closest_vol-vol)
				# sum=np.add(vector,sum)
				# if self.verbose:
					# print("xsum",xsum)
					# print("ysum",ysum)
					# print("mag_diff",mag_diff)
					# print("vol_sum",vol_sum)
			#normalize the totals and make mag_diff less important
			#1.2 is completely arbitrary, but it seems to work decently
			total=abs(xsum/vol_sum)+abs(ysum/vol_sum) + mag_diff/(1.2*vol_sum)
			return total #np.linalg.norm(sum)


		#Sound Operations------------------------

		def distance_to_volume(self,distance) :
			# This should return the volume at which the device will sound like ~50db from the given distance.
			volume=(distance+(25*self.min_vol))/20
			# distance=20*volume-6 #in ft
			if volume<.2:volume=.2 #its not great below 20%
			return volume

		def volume_to_distance(self,volume) :
			#So this is relatively arbitrary. I did some testing, and working on the assumption that ~50db is the optimal volume for music, determined the way to go about this is to use the distance that should be ~50db at said volume
			#Based on experimentation I got this formula.
			# print(volume)

			distance=25*volume-(20*self.min_vol) #in ft
			if distance<.5:distance=.5
			return distance

		#Misc operations-------------------------
		def get_closest(self) : #gets the closest device to the foci
			closest=None
			closest_name=None
			min_dist=sys.maxsize #all distances will be less than this
			i=0
			for name, device in self.devices.items() :
				dist=np.linalg.norm(self.foci-device["location"])
				if dist<min_dist :
					closest=device
					closest_name=name
					min_dist=dist
					self.closest_index=i
				i+=1
			print
			return closest


		#Vector Operations------------------------

		#gets a device vector with magnitude indicitive of volume
		def get_device_vector(self, device, hyp_vol=None) :
			#this allows hypothetical volumes to be passed in without querrying.
			if hyp_vol==None: vol=self.get_device_vol(device)
			else : vol=hyp_vol
			# print(device, " Vol ", vol)
			magnitude=self.volume_to_distance(vol)
			unit_vector=self.get_device_unit_vector(device)
			unit_vector=magnitude*np.array(unit_vector)
			vector=self.offset_vector(device["location"],unit_vector)
			return vector

		#calculates the unit vector of device with offset
		def get_device_unit_vector(self, device) :
			vector=np.concatenate((device["location"], self.foci))
			base_vector=self.centralize_vector(vector)
			unit_vector=base_vector/self.get_vector_mag(base_vector)
			# unit_vector=self.offset_vector(vector[0:2],unit_vector)
			return unit_vector

		#calculates the magnitude of a 2 point vector
		def get_vector_mag(self, vector) :
			# is this right???
			return np.linalg.norm(vector)

		#removes vector offset
		def centralize_vector(self,vector) :
			return [vector[2]-vector[0],vector[3]-vector[1]]

		#offsets a vector
		def offset_vector(self,point, vector) :
			return [point[0],point[1],vector[0]+point[0],vector[1]+point[1]]



		#Device interation methods----------------
		""" Connects to and returns a list of devices in the settings"""
		def connect(self) :
			chromecasts = pychromecast.get_chromecasts()
			for device in chromecasts:
				name=device.device.friendly_name
				# if args.scan :
				# 	print( "Detected ", name)
				if name in self.devices: #if its one of mine
					# connected_devices[name]=device
					self.devices[name]["device"]=device

		#sets device volume
		def set_device_vol(self,device, vol) :
			vol=np.clip(vol,.2,1)
			device["device"].wait()
			device["device"].set_volume(vol)

		#gets device volume
		def get_device_vol(self,device) :
			# print('\n',device)
			device["device"].wait()
			vol=device["device"].status.volume_level
			return vol




def interactive_mode(controller) :
	print("entering interactive mode")

	print("loop mode is activated, this will only update when position is updated")
	print("wasd controls location")
	print("c exits")
	foci=controller.get_foci()
	x=foci[0]
	y=foci[1]
	inc=1
	while True :
		# try :
			foci=controller.get_foci()
			x=foci[0]
			y=foci[1]
			key=readchar.readkey()
			if key=='s' : #point up
				y-=inc
			elif key=='w' : #point down
				y+=inc
			elif key=='d' : #point left
				x+=inc
			elif key=='a' : #point right
				x-=inc
			elif key=='p' : #prints volumes
				controller.plot_vectors()
			elif key=='v' : #prints volumes
				print(controller)
			elif key=='c' :
				break

			# if args.loop==False :
			# 	if key=='e' :#volume up
			# 		vol_mult+=.025
			# 	elif key=='q' : #volume down
			# 		vol_mult-=.025
			# else :
			# 	base_mult=get_base_mult([x,y])
			# 	if base_mult!=vol_mult :
			# 		vol_mult=base_mult
			# 		equalize_to_point(vol_mult, [x,y])
			#
			# print("[{0},{1}]:{2:3f}".format(x,y, vol_mult))
			# equalize_to_point(vol_mult, [x,y])
			print("foci {} {}".format(x,y))
			controller.set_foci([x,y])
			controller.minimize_vols()
			time.sleep(.1)

		# except KeyboardInterrupt:
		# 	pass

def main() :
	# device_settings={"Titan":[[12,15],25], #1
	# 			"janus":[[7,12],15], #2
	# 			"Kitchen speaker":[[20,1],15], #3
	# 			"Epimetheus":[[3,12],15] #4
	# 			# "Bedroom":[[9,22],15] #5
	# }

	device_settings={"Titan":{"location":np.array([12,15])}, #1
				"janus":{"location":np.array([6,1])}, #2
				"Kitchen speaker":{"location":np.array([20,1])}, #3
				"Epimetheus":{"location":np.array([3,12])} #4
				# "Bedroom":[[9,22],15] #5
	}
	location_map={"living room":[8,5],
				"kitchen" : [22,5],
				"desk" : [15,15]

	}

	parser = argparse.ArgumentParser(description='Controls volume foci of google devices')
	parser.add_argument('-l', type=str,dest="location", default=False, help='input location')
	args = parser.parse_args()

	if args.location :
		print(args.location)
		foci=location_map[args.location]
	else : foci=[10.5,4]

	controller=volume_controller(device_settings, foci=foci, verbose=True)
	interactive_mode(controller)




if __name__ == "__main__":
	# execute only if run as a script
	main()
