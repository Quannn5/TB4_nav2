# TurtleBot 4 Navigation Practice

This package wraps the TurtleBot 4 Ignition simulator, SLAM Toolbox, and Nav2 stack so the workspace is ready for the assignment:

- Launch TurtleBot 4 in simulation
- Build a map with SLAM Toolbox
- Save the map to `map.yaml` and `map.pgm`
- Localize the robot against the saved map
- Run autonomous navigation with Nav2

## Launch files

- `tb4_sim.launch.py` : starts TurtleBot 4 in the Ignition world and RViz
- `tb4_slam.launch.py` : starts the simulation and SLAM Toolbox, intended for mapping
- `tb4_localization.launch.py` : loads a saved map and runs AMCL localization
- `tb4_navigation.launch.py` : loads a map and starts Nav2 for autonomous navigation

## Typical workflow

1. Build the workspace:

   source /opt/ros/humble/setup.bash
   cd ~/tb4_ws
   colcon build --packages-select tb4_navigation_practice
   source install/setup.bash

2. Start the simulation and SLAM mapping stack:

   ros2 launch tb4_navigation_practice tb4_slam.launch.py world:=maze

3. In a second terminal, teleoperate the robot to explore the environment:

   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel

4. In RViz2, confirm that walls, corridors, and obstacles are visible. Drive the robot through most of the drivable area.

5. Save the generated map:

   ros2 run nav2_map_server map_saver_cli -f ~/tb4_ws/src/tb4_navigation_practice/maps/map

   This creates:
   - `~/tb4_ws/src/tb4_navigation_practice/maps/map.yaml`
   - `~/tb4_ws/src/tb4_navigation_practice/maps/map.pgm`

6. Copy the saved map into the installed package share directory by rebuilding:

   cd ~/tb4_ws
   colcon build --packages-select tb4_navigation_practice
   source install/setup.bash

   Both localization and navigation launches use this shared package map by default. Rebuild after saving a new map so the installed copy is refreshed.

7. Start localization and navigation using that map:

   ros2 launch tb4_navigation_practice tb4_navigation.launch.py

8. Send a goal in RViz2 using the Nav2 goal tool or via a small script/CLI command.

## Notes

- The default world for mapping, localization, and navigation is the TurtleBot 4 maze world.
- The package's `maps/map.yaml` and `maps/map.pgm` are the shared map files used by localization and navigation. Pass `map:=/full/path/to/map.yaml` to either launch to select a different map.
- If you want to use a different world or map, change the launch arguments accordingly.
