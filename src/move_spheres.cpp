#include <gazebo_msgs/GetModelState.h>
#include <gazebo_msgs/SetModelState.h>
#include <ros/ros.h>

namespace
{
	constexpr const char *kModelSrvName = "/gazebo/get_model_state";
	constexpr double radius = 2.5;
} // namespace
int main(int argc, char **argv)
{
	ros::init(argc, argv, "rviz_collision_publisher");
	ros::NodeHandle nh;
	ros::ServiceClient gazebo_client =
		nh.serviceClient<gazebo_msgs::GetModelState>(kModelSrvName);

	ros::ServiceClient move_client = nh.serviceClient<gazebo_msgs::SetModelState>("/gazebo/set_model_state");
	gazebo_client.waitForExistence();

	gazebo_msgs::GetModelState get_model_state;
	gazebo_msgs::SetModelState set_model_state;
	std::vector<geometry_msgs::Point> sphere_centers;
	int nr_of_obstacles;
	nh.getParam("nr_of_obstacles", nr_of_obstacles);
	for (int i = 0; i < nr_of_obstacles; i++)
	{
		std::string sphere = "collision_sphere_clone_" + std::to_string(i);
		get_model_state.request.model_name = sphere;
		if (gazebo_client.call(get_model_state))
		{

			geometry_msgs::Pose sphere_pose = get_model_state.response.pose;
			gazebo_msgs::ModelState new_modelstate;
            ROS_INFO("%d Before %lf, %lf, %lf", i, sphere_pose.position.x, sphere_pose.position.y, sphere_pose.position.z);
			sphere_pose.position.z = 10;
            ROS_INFO("%d After %lf, %lf, %lf", i, sphere_pose.position.x, sphere_pose.position.y, sphere_pose.position.z);
			new_modelstate.model_name = (std::string) sphere;
    		new_modelstate.pose = sphere_pose;
			set_model_state.request.model_state = new_modelstate;
			sphere_centers.push_back(sphere_pose.position);
			if (move_client.call(set_model_state))
				ROS_INFO("Sphere's magic moving success!! sphere_clone_%d", i);
			else
				ROS_ERROR("Failed to magic move PR2! Error msg:%s", set_model_state.response.status_message.c_str());
		}
        ros::Duration(0.05).sleep();
	}
	ros::Duration(2.0).sleep();
	return 0;
}