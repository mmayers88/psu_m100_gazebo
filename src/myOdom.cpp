#include <ros/ros.h>
#include <nav_msgs/Odometry.h>
#include <tf/transform_broadcaster.h>

//http://library.isr.ist.utl.pt/docs/roswiki/navigation(2f)Tutorials(2f)RobotSetup(2f)Odom.html

class SubscribeAndPublish
{
public:
    tf::TransformBroadcaster odom_broadcaster;
  SubscribeAndPublish()
  {
    //Topic you want to publish
    pub_ = n_.advertise<nav_msgs::Odometry::ConstPtr>("/myOdom", 1);
    

    //Topic you want to subscribe
    sub_ = n_.subscribe("dji_sdk/Odometry", 1, &SubscribeAndPublish::callback, this);
  }

  void callback(const nav_msgs::Odometry::ConstPtr& input_msg)
  {
    ros::Time current_time, last_time;
    current_time = ros::Time::now();
    last_time = ros::Time::now();
    
      //since all odometry is 6DOF we'll need a quaternion created from yaw
    geometry_msgs::Quaternion odom_quat = tf::createQuaternionMsgFromYaw(th);

    //first, we'll publish the transform over tf
    geometry_msgs::TransformStamped output_msg;
    output_msg.header.stamp = current_time;
    output_msg.header.frame_id = "odom";
    output_msg.child_frame_id = "base_link";

    output_msg.transform.translation.x = x;
    output_msg.transform.translation.y = y;
    output_msg.transform.translation.z = 0.0;
    output_msg.transform.rotation = odom_quat;

    //send the transform
    odom_broadcaster.sendTransform(output_msg);

    //next, we'll publish the odometry message over ROS
    nav_msgs::Odometry odom;
    odom.header.stamp = current_time;
    odom.header.frame_id = "odom";

    //set the position
    odom.pose.pose.position.x = x;
    odom.pose.pose.position.y = y;
    odom.pose.pose.position.z = 0.0;
    odom.pose.pose.orientation = odom_quat;

    //set the velocity
    odom.child_frame_id = "base_link";
    odom.twist.twist.linear.x = vx;
    odom.twist.twist.linear.y = vy;
    odom.twist.twist.angular.z = vth;

    pub_.publish(output_msg);
  }

private:
  ros::NodeHandle n_; 
  ros::Publisher pub_;
  ros::Subscriber sub_;

};//End of class SubscribeAndPublish

int main(int argc, char **argv)
{
  //Initiate ROS
  ros::init(argc, argv, "myOdom");

  //Create an object of class SubscribeAndPublish that will take care of everything
  SubscribeAndPublish SAPObject;

  ros::spin();

  return 0;
}