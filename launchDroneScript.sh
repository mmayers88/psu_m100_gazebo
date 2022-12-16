#!/usr/bin/env bash
source /opt/ros/kinetic/setup.bash

#Terminal 1
echo "Initialization Sequence."
echo "Connect to drone."
gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;cd ~/MatricePyROS/catkin_ws;source devel/setup.bash;roslaunch dji_sdk sdk_manifold.launch; $SHELL'"

echo "Waiting for connection..."
echo "Countdown!"
for i in 4 3 2 1
do
	echo "$i sec..."
	sleep 1;
done

#Terminal 2
echo "Launch Simulation"
#gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;source ~/drone_ws/devel/setup.bash;roslaunch hku_m100_gazebo empty_world_with_tags.launch; $SHELL'" 
gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;source ~/drone_ws/devel/setup.bash;roslaunch -v hku_m100_gazebo sphere_world.launch; $SHELL'" 

#echo "Waiting for sim to start..."
#for i in 10 9 8 7 6 5 4 3 2 1
#do
#	echo "$i sec..."
#	sleep 2;
#done

#Terminal 3
#echo "Launch Bridge"
#gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;source ~/drone_ws/devel/setup.bash;roslaunch hku_m100_gazebo moveSpheres.launch; $SHELL'"

#echo "Moving Spheres..."
for i in 10 9 8 7 6 5 4 3 2 1
do
	echo "$i sec..."
	sleep 1;
done

#Terminal 4
echo "Launch Bridge"
gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;source ~/drone_ws/devel/setup.bash;roslaunch -v hku_m100_gazebo bridge.launch; $SHELL'"


#Terminal 4
#echo "Work Terminal"
#gnome-terminal --tab --command="bash -c 'source /opt/ros/kinetic/setup.bash;source ~/drone_ws/devel/setup.bash;rosrun hku_m100_gazebo psu_m100_gasSensor; $SHELL'"





