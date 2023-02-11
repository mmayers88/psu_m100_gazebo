from dji_sdk.dji_drone import DJIDrone
import time

drone = DJIDrone()
print("control requesting")
drone.request_sdk_permission_control() #request control
time.sleep(1)
print("control requested")
drone.arm_drone()
time.sleep(1)
print("Drone Armed")




for i in range(60):
		drone.attitude_control(DJIDrone.HORIZ_POS|DJIDrone.VERT_VEL|DJIDrone.YAW_ANG|DJIDrone.HORIZ_BODY|DJIDrone.STABLE_ON, 0, 0, 3, 0)
		time.sleep(0.02)


drone.local_position_navigation_send_request(1000,-1000,3)
