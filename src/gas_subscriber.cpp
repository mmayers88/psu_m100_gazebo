#include "ros/ros.h"
#include "hku_m100_gazebo/GasSensor.h"
 
void messageCallback(const hku_m100_gazebo::GasSensor::ConstPtr& msg) {
  ROS_INFO("I have received: [%lf]", msg->data);
}
 
int main(int argc, char **argv) {
  ros::init(argc, argv, "gas_subscriber");
  ros::NodeHandle n;
  ros::Subscriber sub = n.subscribe("hku_m100_gazebo/message", 1000, messageCallback);
  ros::spin();
  return 0;
}