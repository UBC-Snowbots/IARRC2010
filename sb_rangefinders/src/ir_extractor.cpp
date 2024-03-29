/** 
 * ir_extractor ROS Node
 * This node subscribes to the robot_state topic and takes the ir
 * analog values via a RobotState message and then reads the necessary
 * information off the config file (e.g: robot.cfg). It then combines
 * these information to create a LaserScan message and publishes this
 * message on the ir_info topic.
 * 
 * @author: Navid Fattahi <navid.fattahi@gmail.com>
 */

#include <iostream>
#include <stdio.h>
#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <sb_config/include/sb_config/config_file.h>
#include <sb_msgs/RobotState.h>
#include <sb_rangefinders/Rangefinder.h>

/* Constants */
const std::string NODE_NAME     = "ir_extractor";
const std::string SUBSCRIBE_TOPIC = "robot_state";
const std::string PUBLISH_TOPIC   = "base_scan";
const int MSG_QUE_SIZE = 20;

/* Method Declaration */
void callBack(const sb_msgs::RobotStateConstPtr&);

/* Creating a Rangefinder object */
sb_rangefinders::Rangefinder* ir_sensor;

using namespace ros;

Publisher dataPub;

int main (int argc, char** argv)
{
  /* Initializing this node */
  ROS_INFO("Starting %s", NODE_NAME.c_str());
  init(argc, argv, NODE_NAME);

  /* Initializing ir_sensor */
  ir_sensor = new sb_rangefinders::Rangefinder();

  /* Opening and loading the Config file */
  std::string cfgFile;
  if (! sb_config::findConfigFile(argc, argv, cfgFile))
  {
    ROS_FATAL("Can't find configuration file.");
    shutdown();
  }
  ROS_INFO("Loading configuration in %s", cfgFile.c_str());
  ir_sensor->loadConfig(cfgFile);

  NodeHandle n;

  /* Creating the subscriber and publisher */
  Subscriber dataSub = n.subscribe(SUBSCRIBE_TOPIC, MSG_QUE_SIZE, callBack);
  dataPub = n.advertise<sensor_msgs::LaserScan>(PUBLISH_TOPIC, MSG_QUE_SIZE);

  /* Main loop */
  while (ok())
    spin();

  /* Informing the user when getting shut down */
  ROS_INFO("Shutting Down %s", NODE_NAME.c_str());
  delete ir_sensor;
}

/**
 * This function get called whenever a new messaged is arrived.
 * When the LaserScan message is ready, this function publishes
 * the message out.
 */
void callBack(const sb_msgs::RobotStateConstPtr& robotStateMsg)
{
  ROS_DEBUG("got a RobotState message");
  int num_rays = ir_sensor->getNumRays();
  double ranges[num_rays];  //this array stores distances
  
  ranges[0] = 104*exp(-0.004*ranges[0]);
  ranges[1] = 134*exp(-0.004*ranges[1]);
  ranges[2] = 107*exp(-0.004*ranges[2]);
  ranges[3] = 192*exp(-0.004*ranges[3]);
  ranges[4] = 158*exp(-0.004*ranges[4]);

  ir_sensor->getDistances(robotStateMsg->analog, ranges);

  //Creating a LaserScan message
  sensor_msgs::LaserScan laserScanMsg = ir_sensor->LaserScanMsgGenerator(ranges);

  //Publishing the LaserScan message
  dataPub.publish(laserScanMsg);
}

