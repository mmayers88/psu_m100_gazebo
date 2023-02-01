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

#settings
thresh_num = 48.0

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

def init_state():
	#take sample
	gas_sensor_msg = GasSensor()
	msg_a = gas_sensor_msg.data
	#save coordinates
	coor_a = (drone.local_position.x,drone.local_position.y)
	#fly until finding the first  cut edge
	while True:
		#move up
		for i in range(50):
			drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, 2, 0, 0, 0)
			time.sleep(0.02)
		time.sleep(5)
		#take second sample
		msg_b = gas_sensor_msg.data
		#save coordinates
		coor_b = (drone.local_position.x,drone.local_position.y)
		#if local sample is below threshold of border
		if msg_b < thresh_num:
			#edge is found: start CuP
			coor_a = (int(coor_a[0]),int(coor_a[1]))
			coor_b = (coor_a[0] + 10, coor_a[1])
			break
		else:
			#new edge is old edge, keep flying, try again
			msg_a = msg_b
			coor_a = coor_b
	return msg_a, msg_b, coor_a, coor_b

def rot_cell_points(origin, dir, buff = 10):
	arr = np.array(
		[[(origin.x, origin.y),(origin.x, origin.y+buff)],
		[(origin.x+buff, origin.y+buff),(origin.x+buff, origin.y)]]
	)
	if dir == 0:
		return arr
	for i in range(dir):
		arr = rotate(arr, arr[0], -90)
	return arr

			
def CuP(msg_a, msg_b, coor_a, coor_b):
	while True:
		#check edges
		#find line orientation
		dir = -1
		x_dir  = coor_b[0] - coor_a[0]
		if x_dir:
			if x_dir > 0:
				# a-b
				dir = 1
			else:
				# b-a
				dir = 3
		else:
			if (coor_b[1] - coor_a[1]) > 0:
				# b
				# |
				# a
				dir = 0
			else:
				# a
				# |
				# b
				dir = 2
		# get prospective points of node and rotate
		cell_points = rot_cell_points(coor_a, dir)
		drone.local_position_navigation_send_request(cell_points[2][0],cell_points[2][1],3)
		time.sleep(10)
		#take sample
		msg_c = gas_sensor_msg.data
		#check for edge
		if msg_c > thresh_num:
			msg_a = msg_c
			coor_a = (cell_points[2][0],cell_points[2][1])
		else:
			#logic to move past next point
			# check other point
			drone.local_position_navigation_send_request(cell_points[3][0],cell_points[3][1],3)
			time.sleep(10)
			#take sample
			msg_d = gas_sensor_msg.data
			if msg_d > thresh_num:
				msg_b = msg_c
				msg_a = msg_d
				coor_a = (cell_points[3][0],cell_points[3][1])
				coor_b = (cell_points[2][0],cell_points[2][1])
			else:
				msg_b = msg_d
				coor_b = (cell_points[3][0],cell_points[3][1])
				write_msg = msg_a
		#write coordinates
		gps_x = drone.global_position.longitude
		gps_y = drone.global_position.latitude,
		GPS_coor = np.vstack((GPS_coor,[gps_x,gps_y,coor_a.x,coor_a.y,coor_b.x,coor_b.y]))
		#check terminal state
			#head home if done

		#check for low power
		if low_power(drone.power_status.percentage):
			print("Drone Disarmed")
			print("Low Power")
			return GPS_coor

		return GPS_coor


def main():
    drone.local_position_navigation_send_request(6,6,3)
    time.sleep(10)
    print(gas_sensor_msg)
    drone.local_position_navigation_send_request(6,6,3)
    time.sleep(10)
    print(gas_sensor_msg)
    return
    # init state: this is a priori
    msg_a, msg_b, coor_a, coor_b = init_state()

    #CuP
    GPS_data = CuP(msg_a, msg_b, coor_a, coor_b)


if __name__ == "__main__":
	#test to have the drone fly in a square and land, for purposes of testing automatic flight.
	drone = DJIDrone()
	gas_sensor_msg = GasSensor()
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
		drone.takeoff() 	
		time.sleep(2)
		for i in range(50):
			drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, 0, 0, 3, 0)
			time.sleep(0.02)
			#takeoff: don't know if this actually does anything?
		print("takeoff")
		'''print(drone.odometry)
		print(drone.compass)
		print(drone.flight_status)
		print(drone.global_position)
		print(drone.power_status)
		print("global")			#GPS coordinates
		print(drone.global_position)
		print("local") 			#position in RVIZ grid units(meters)
		print(drone.local_position)'''
	

		time.sleep(2)
	GPS_coor = np.array([
		drone.global_position.longitude, 
		drone.global_position.latitude, 
		drone.local_position.x, 
		drone.local_position.y, 
		drone.local_position.x, 
		drone.local_position.y,
		drone.global_position.header.stamp.secs])
	main()


#source ../../devel/setup.bash 
