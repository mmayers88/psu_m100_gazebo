#include <gazebo_msgs/GetModelState.h>
#include <ros/ros.h>
#include <cmath>
#include "hku_m100_gazebo/GasSensor.h"

const int sensitivity = 1;
namespace
{
	constexpr const char *kModelSrvName = "/gazebo/get_model_state";
	constexpr double radius = 2.5;
} // namespace

// Function to calculate distance

class SphereMonitor
{
public:
	ros::NodeHandle nh;
	ros::ServiceClient gazebo_client =
		nh.serviceClient<gazebo_msgs::GetModelState>(kModelSrvName);
	gazebo_msgs::GetModelState get_model_state;
	std::string drone_name = "hku_m100";
	std::string relativeEntityName = (std::string) "world";
	int nr_of_obstacles;
	SphereMonitor()
	{
		nh.getParam("nr_of_obstacles", nr_of_obstacles);
		InitSpheres(nr_of_obstacles, gazebo_client);
	};

	double printDist()
	{
		geometry_msgs::Point drone_pose;
		geometry_msgs::Quaternion drone_ore;
		get_model_state.request.model_name = drone_name;
		// client.call(get_drone_state);
		drone_pose = get_model_state.response.pose.position;
		drone_ore = get_model_state.response.pose.orientation;
		float count = 0.0;
		for (int i = 0; i < nr_of_obstacles; i++)
		{
			if (gazebo_client.call(get_model_state))
			{
				// std::cout << get_model_state.response << std::endl;
				// std::cout << i << "_x: " << sphere_centers_[i].x << "y: " << sphere_centers_[i].y << "z: " << sphere_centers_[i].z << std::endl;
				// std::cout << "Drone x: " << drone_pose.x << "y: " << drone_pose.y << "z: " << drone_pose.z << std::endl;
				// std::cout << get_model_state.response.pose.position.x << get_model_state.response.pose.position.y << get_model_state.response.pose.position.z << std::endl;
				double dist = sqrt(pow(sphere_centers_[i].x - drone_pose.x, 2) + pow(sphere_centers_[i].y - drone_pose.y, 2) + pow(sphere_centers_[i].z - drone_pose.z, 2));
				// std::cout << i <<"_Dist: " << dist << std::endl;
				if (dist <= 0.5)
					count += sensitivity;
				/*else if (dist <= 1.0)
					count += 0.75 * sensitivity;
				else if (dist <= 1.5)
					count += 0.5 * sensitivity;
				else if (dist <= 2.0)
					count += 0.25 * sensitivity;*/
				else if (dist <= 2.5)
					count += (dist/2.5) * sensitivity;
				else
					continue;
				// std::cout << i << "_Pose: "<< sphere_centers_[i].x << sphere_centers_[i].y << sphere_centers_[i].z << std::endl;
			}
		}
		if (count > 0.0)
			std::cout << count << std::endl;
		return count;
	};
	double distance(double x1, double y1, double z1, double x2, double y2, double z2)
	{
		// Calculating distance
		return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2));
	};

private:
	std::vector<geometry_msgs::Point> sphere_centers_;

	void InitSpheres(int nr_of_obstacles, ros::ServiceClient gazebo_client)
	{
		for (int i = 0; i < nr_of_obstacles; i++)
		{
			std::string sphere = "collision_sphere_clone_" + std::to_string(i);
			get_model_state.request.model_name = sphere;
			if (gazebo_client.call(get_model_state))
			{
				sphere_centers_.push_back(get_model_state.response.pose.position);
			}
		}
		std::cout << "Spheres are live." << std::endl;
	};
};

int main(int argc, char **argv)
{
	ros::init(argc, argv, "psu_m100_gasSensor");
	ros::NodeHandle n;
	ros::Publisher pub = n.advertise<hku_m100_gazebo::GasSensor>("hku_m100_gazebo/message", 1000);
	ros::Rate loop_rate(10);
	SphereMonitor monitor;
	monitor.gazebo_client.waitForExistence();
	std::cout << "Initialization: ";
	while (ros::ok())
	{
		hku_m100_gazebo::GasSensor msg;
		msg.header.stamp = ros::Time::now();
		msg.header.frame_id = "/world";
		msg.data = monitor.printDist();
		pub.publish(msg);
		ros::spinOnce();
		// loop_rate.sleep();
	}
	return 0;
}