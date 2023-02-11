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
THRESH_NUM = 0.70
SLEEPTIME = 10

#set current binary state 1 or True
xState = True

# birds eye directions
UP_X = 3
DOWN_X = -3
RIGHT_Y = -3
LEFT_Y = 3

#for liftoff
UP_Z = 6

DATA_FILE = "data_text.csv"

def callback(data):
	print(data)
	rospy.longinfo(rospy.get_caller_id() + "I heard %f", data.data)
	print("In Callback")

def rotate(xy, degrees=0, origin=(0, 0)):
    '''angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)'''
    """Rotate a point around a given point.
    
    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    radians = np.deg2rad(degrees)
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
    return (qx,qy)

    

def rot_cell_points(origin, dir, buff = 10):
    arr = np.array(
        [(origin[0], origin[1]),(origin[0], origin[1]+buff),(origin[0]+buff, origin[1]+buff),(origin[0]+buff, origin[1])]
    )
    print("Original Arr:")
    print(arr)
    if dir == 0:
        return arr
    if dir == 1:
        arr[0] = rotate(arr[0], 90, arr[0])
        arr[1] = rotate(arr[1], 90, arr[0])
        arr[2] = rotate(arr[2], 90, arr[0])
        arr[3] = rotate(arr[3], 90, arr[0])
    if dir == 2:
        arr[0] = rotate(arr[0], 180, arr[0])
        arr[1] = rotate(arr[1], 180, arr[0])
        arr[2] = rotate(arr[2], 180, arr[0])
        arr[3] = rotate(arr[3], 180, arr[0])
    if dir == 3:
        arr[0] = rotate(arr[0], 270, arr[0])
        arr[1] = rotate(arr[1], 270, arr[0])
        arr[2] = rotate(arr[2], 270, arr[0])
        arr[3] = rotate(arr[3], 270, arr[0])
    print("arr")
    print(arr.astype(int))
    return arr.astype(int)


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
	gas_sensor_msg = rospy.wait_for_message("hku_m100_gazebo/GasSensor", GasSensor)
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
		gas_sensor_msg = rospy.wait_for_message("hku_m100_gazebo/GasSensor", GasSensor)
		msg_b = gas_sensor_msg.data
		#save coordinates
		coor_b = (drone.local_position.x,drone.local_position.y)
		print("MESSAGE B")
		print(msg_b)
		print(coor_b)
		#if local sample is below threshold of border
		if msg_b < THRESH_NUM:
			#edge is found: start CuP
			coor_a = (int(coor_a[0]),int(coor_a[1]))
			coor_b = (coor_a[0] + 10, coor_a[1])
			break
		else:
			#new edge is old edge, keep flying, try again
			msg_a = msg_b
			coor_a = coor_b
	return msg_a, msg_b, coor_a, coor_b


			
def CuP(msg_a, msg_b, coor_a, coor_b):
	print("=====================================")
	print("===========starting CuP==============")
	print("=====================================")
	GPS_coor = np.array([
	drone.global_position.header.stamp.secs,
	drone.global_position.longitude, 
	drone.global_position.latitude, 
	drone.local_position.x, 
	drone.local_position.y, 
	drone.local_position.x, 
	drone.local_position.y])
	np.savetxt(DATA_FILE, GPS_coor, fmt='%f', delimiter=',', newline='\n')
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
		print(coor_a)
		print(coor_b)
		cell_points = rot_cell_points(coor_a, dir)
		drone.local_position_navigation_send_request(cell_points[2][0],cell_points[2][1],UP_Z)
		print("moving to x3")
		time.sleep(SLEEPTIME)
		#take sample
		gas_sensor_msg = rospy.wait_for_message("hku_m100_gazebo/GasSensor", GasSensor)
		msg_c = gas_sensor_msg.data
		print("Sensor reading:")
		print(msg_c)
		#check for edge
		if msg_c > THRESH_NUM:
			msg_a = msg_c
			coor_a = (cell_points[2][0],cell_points[2][1])
		else:
			#longic to move past next point
			# check other point
			drone.local_position_navigation_send_request(cell_points[3][0],cell_points[3][1],UP_Z)
			print("moving to x4")
			time.sleep(SLEEPTIME)
			#take sample
			gas_sensor_msg = rospy.wait_for_message("hku_m100_gazebo/GasSensor", GasSensor)
			msg_d = gas_sensor_msg.data
			print("Sensor reading:")
			print(msg_d)
			if msg_d > THRESH_NUM:
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
		gps_y = drone.global_position.latitude
		print([drone.global_position.header.stamp.secs,gps_x,gps_y,coor_a[0],coor_a[1],coor_b[0],coor_b[1]])
		temp_coor = np.array([drone.global_position.header.stamp.secs,gps_x,gps_y,coor_a[0],coor_a[1],coor_b[0],coor_b[1]])
		GPS_coor = np.vstack((GPS_coor,temp_coor))
		np.savetxt(DATA_FILE, GPS_coor, fmt='%f', delimiter=',', newline='\n')
		#check terminal state
			#head home if done

		#check for low power
		if low_power(drone.power_status.percentage):
			print("Drone Disarmed")
			print("Low Power")
			return GPS_coor
		
	#this will happen when we finish the end condition
	#return GPS_coor
	'''if xState:
		#move
		#check state
		#if bounds are 
	#fly in a square
	drone.local_position_navigation_send_request(6,6,3)
	#drone.local_position_control(3,3,3,0)
	time.sleep(6)
	drone.local_position_control(6,6,3,0)'''


def main():
	'''
	for i in range(1):
		#rospy.init_node('test_node')
		print("========================")
		print(GasSensor())
		rospy.Subscriber("hku_m100_gazebo/GasSensor", GasSensor, callback)
		print("===========END==========")
		gas_sensor_msg = GasSensor()
		print(gas_sensor_msg.data)
	loc_x = drone.local_position.x
	loc_y = drone.local_position.y'''

	#start at 650,650
	for i in range(10):
		drone.local_position_navigation_send_request(725,-650,3)
		print("travelling to 725,650")
		time.sleep(SLEEPTIME)
	# init state: this is a priori
	msg_a, msg_b, coor_a, coor_b = init_state()
	
	#CuP
	GPS_data = CuP(msg_a, msg_b, coor_a, coor_b)
	GPS_data.tofile('data.csv', sep = ',')


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
		print("takeoff")
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
