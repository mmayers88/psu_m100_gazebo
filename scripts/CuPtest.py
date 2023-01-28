#!/usr/bin/env python

from dji_sdk.dji_drone import DJIDrone
from hku_m100_gazebo.msg import GasSensor
import rospy
import numpy as np
import dji_sdk.msg
import time
import sys
import math
import os

#set current binary state 1 or True
xState = True

# birds eye directions
UP_X = 3
DOWN_X = -3
RIGHT_Y = -3
LEFT_Y = 3

#for liftoff
UP_Z = 3

def callback(data):
	print(data)
	rospy.loginfo(rospy.get_caller_id() + "I heard %f", data.data)
	print("In Callback")

def rotate(p, origin=(0, 0), degrees=0):
    angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)


def low_power(lp):
	if lp < 10:
		drone.gohome() #land
		return True
	return False

def drone_move(dir1, dir2, dir3=0, r=50):
	for i in range(r):
		drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, dir1, dir2, dir3, 0)
		time.sleep(0.02)
def drone_rot(rot = 0, r=60):
	for i in range(r):
		drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, 0, 0, 0, rot)
		time.sleep(0.02)

def main():
	for i in range(1):
		#rospy.init_node('test_node')
		print("========================")
		print(GasSensor())
		rospy.Subscriber("hku_m100_gazebo/GasSensor", GasSensor, callback)
		print("===========END==========")
		rospy.spin()
	loc_x = drone.local_position.x
	loc_y = drone.local_position.y

	#init state: fly until finding the first  cut edge
	while True:
		#take sample
		#save coordinates
		#move
		for i in range(60):
			drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, 2, 2, 0, 0)
			time.sleep(0.02)
		time.sleep(5)
		#take second sample
		#save coordinates
		#if local sample is below threshold of border
			#edge is found: start CuP
		#else
			#new edge is old edge, keep flying, try again
	#CuP
	while True:
		#check edges
		#find old and new line orientation
		# get prospective points of node and rotate
		# check other two points
		#find edge
		#check for low power
		if xState:
			#move
			#check state
			#if bounds are 
		#fly in a square
		drone.local_position_navigation_send_request(6,6,3)
		#drone.local_position_control(3,3,3,0)
		time.sleep(6)
		drone.local_position_control(6,6,3,0)
		if low_power(drone.power_status.percentage):
			print("Drone Disarmed")
			print("Low Power")
			return


if __name__ == "__main__":
	#test to have the drone fly in a square and land, for purposes of testing automatic flight.
	drone = DJIDrone()
	print("control requesting")
	drone.request_sdk_permission_control() #request control
	time.sleep(1)
	print("control requested")
	drone.arm_drone()
	time.sleep(1)
	print("Drone Armed")
	#check battery before takeoff
	print(drone.power_status)
	if low_power(drone.power_status.percentage):
		print("Drone Disarmed")
		print("Low Power")
	else:
		drone_move(0,0,3,60)	#takeoff
		drone.takeoff() 		#takeoff: don't know if this actually does anything?
		print(drone.odometry)
		print(drone.compass)
		print(drone.flight_status)
		print(drone.global_position)
		print(drone.power_status)
		
		print("global")			#GPS coordinates
		print(drone.global_position)
		print("local") 			#position in RVIZ grid units(meters)
		print(drone.local_position)
		
		time.sleep(2)
	main()


#source ../../devel/setup.bash 
