#include <gazebo_msgs/GetModelState.h>
#include <ros/ros.h>
#include <cmath>
#include "readCSV.h"
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
	ros::ServiceClient gazebo_client = nh.serviceClient<gazebo_msgs::GetModelState>(kModelSrvName);
	gazebo_msgs::GetModelState get_model_state;
	std::string drone_name = "hku_m100";
	std::string relativeEntityName = (std::string) "world";
	std::string filename = "/home/dronecomp/drone_ws/src/hku_m100_gazebo/src/array.csv";
	data_t data;
	int array_xy;
	SphereMonitor()
	{
		nh.getParam("array_xy", array_xy);
		data.load(filename);
		data.save(std::cout);
	};

	double printDist()
	{
		geometry_msgs::Point drone_pose;
		geometry_msgs::Quaternion drone_ore;
		get_model_state.request.model_name = drone_name;
		// client.call(get_drone_state);
		drone_pose = get_model_state.response.pose.position;
		drone_ore = get_model_state.response.pose.orientation;
		double count = 0.0;
		if (gazebo_client.call(get_model_state))
		{
			//int diff = array_xy / 2;
			int diff = 650;
			if (drone_pose.x + diff > array_xy || drone_pose.y + diff > array_xy || drone_pose.x + diff < 0 || drone_pose.y + diff < 0)
				count = 0.0;
			else
				count = data[drone_pose.x + diff][drone_pose.y + diff];
		}
		if (count > 0.0)
			std::cout << count << std::endl;
		else
			std::cout << -1.0 << std::endl;
		return count;
	};
	double distance(double x1, double y1, double z1, double x2, double y2, double z2)
	{
		// Calculating distance
		return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2));
	};

private:
	std::vector<geometry_msgs::Point> sphere_centers_;

	void InitSpheres()
	{
		data.load(filename);
		std::cout << "HERE!." << std::endl;
		data.save(std::cout);
		std::cout << "Spheres are live." << std::endl;
	};
};

int main(int argc, char **argv)
{
	ros::init(argc, argv, "psu_m100_gasSensor");
	ros::NodeHandle n;
	ros::Publisher pub = n.advertise<hku_m100_gazebo::GasSensor>("hku_m100_gazebo/GasSensor", 1000);
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