#include "readCSV.h"
#include <gazebo_msgs/GetModelState.h>
#include <ros/ros.h>
#include <rviz_visual_tools/rviz_visual_tools.h>
#include <visualization_msgs/Marker.h>

namespace
{
    constexpr const char *kModelSrvName = "/gazebo/get_model_state";
    constexpr double radius = 2.5;
} // namespace
int main(int argc, char **argv)
{
    data_t data;

    string filename;

    data.load("/home/dronecomp/drone_ws/src/hku_m100_gazebo/src/array.csv");
    data.save(cout);
    ros::init(argc, argv, "rviz_collision_publisher");
    ros::NodeHandle nh;
    rviz_visual_tools::RvizVisualToolsPtr visual_tools_;
    visual_tools_.reset(
        new rviz_visual_tools::RvizVisualTools("/world", "/obstacles"));

    gazebo_msgs::GetModelState get_model_state;
    std::vector<geometry_msgs::Point> sphere_centers;
    std::vector<geometry_msgs::Point> sphere_centers2;
    int nr_of_obstacles;
    nh.getParam("nr_of_obstacles", nr_of_obstacles);
    visual_tools_->loadMarkerPub();
    visual_tools_->waitForMarkerPub();
    visual_tools_->setLifetime(0);
    for (int row = 0; row < nr_of_obstacles; row++)
        for (int col = 0; col < nr_of_obstacles; col++)
        {
            cout << col + row * 1000 << " " << data[row][col] << endl;
            geometry_msgs::Point sphere_point;
            geometry_msgs::Point sphere_point2;
            sphere_point.x = row;
            sphere_point.y = col;
            sphere_point.z = 10;
            sphere_centers.push_back(sphere_point);

            sphere_point2.x = sphere_point.x + 1;
            sphere_point2.y = sphere_point.y + 1;
            sphere_point2.z = sphere_point.z - 10;

            sphere_centers2.push_back(sphere_point2);
            cout << "before if... ";
            if (data[row][col] > 0.90)
            {
                // rgb(253, 231, 37) #fde725.
                visual_tools_->publishCuboid(sphere_point, sphere_point2, rviz_visual_tools::YELLOW, "Obstacles", 0);
                cout << "90%"<<endl;
                continue;
            }
            else if (data[row][col] > 0.70)
            {
                // rgb(94, 201, 98) #5ec962.
                visual_tools_->publishCuboid(sphere_point, sphere_point2, rviz_visual_tools::LIME_GREEN, "Obstacles", 0);
                cout << "70%"<<endl;
                continue;
            }
            else if (data[row][col] > 0.50)
            {
                // rgb(33, 145, 140) #21918c.
                visual_tools_->publishCuboid(sphere_point, sphere_point2, rviz_visual_tools::GREEN, "Obstacles", 0);
                cout << "50%"<<endl;
                continue;
            }
            else if (data[row][col] > 0.30)
            {
                // rgb(59, 82, 139) #3b528b.
                visual_tools_->publishCuboid(sphere_point, sphere_point2, rviz_visual_tools::BLUE, "Obstacles", 0);
                cout << "30%"<<endl;
                continue;
            }
            else
            {
                // rgb(68, 1, 84) #440154.
                visual_tools_->publishCuboid(sphere_point, sphere_point2, rviz_visual_tools::BLACK, "Obstacles", 0);
                cout << "else."<<endl;
                continue;
            }
        }

    visual_tools_->trigger();
    ros::Duration(1.0).sleep();
    return 0;
}