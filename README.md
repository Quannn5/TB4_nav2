# TurtleBot 4 SLAM and Navigation (ROS 2 Humble)

ROS 2 workspace package for mapping the TurtleBot 4 maze with SLAM Toolbox,
then localizing and navigating with Nav2.

## Requirements

- Ubuntu 22.04 and ROS 2 Humble
- TurtleBot 4 simulation/navigation packages
- SLAM Toolbox, Nav2, RViz2, and `teleop_twist_keyboard`

## Build

```bash
source /opt/ros/humble/setup.bash
cd ~/tb4_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select tb4_navigation_practice
source install/setup.bash
```

## Mapping

Start the maze simulation with SLAM:

```bash
ros2 launch tb4_navigation_practice tb4_slam.launch.py world:=maze
```

In another terminal, teleoperate the robot and explore the maze:

```bash
source /opt/ros/humble/setup.bash
source ~/tb4_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

When the map is ready, save it to the package:

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ~/tb4_ws/src/tb4_navigation_practice/maps/map
```

Rebuild so the saved map is copied to the installed package share:

```bash
cd ~/tb4_ws
colcon build --packages-select tb4_navigation_practice
source install/setup.bash
```

The shared map files are `src/tb4_navigation_practice/maps/map.yaml` and
`src/tb4_navigation_practice/maps/map.pgm`.

## Localization and autonomous navigation

Stop the mapping session, then launch a fresh maze simulation with AMCL
localization and Nav2:

```bash
ros2 launch tb4_navigation_practice tb4_navigation.launch.py
```

In RViz2, set the robot's initial pose with **2D Pose Estimate**, then send
navigation goals with **Nav2 Goal**. For a different map, pass
`map:=/absolute/path/to/map.yaml`.

## Main ROS interfaces

- `/scan`: LiDAR `sensor_msgs/msg/LaserScan`
- `/odom`: odometry `nav_msgs/msg/Odometry`
- `/map`: occupancy grid `nav_msgs/msg/OccupancyGrid`
- `/cmd_vel`: velocity commands `geometry_msgs/msg/Twist`
- `/tf`, `/tf_static`: robot and localization transforms

See [the package README](src/tb4_navigation_practice/README.md) for package
details and launch file descriptions.
