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

   The simulation adds two chairs, four boxes, two person models, and a
   traffic light at separate locations across the map, one at a time after
   startup. Wait for the `spawn_*` processes to report successful creation
   before mapping. The chair/person meshes are fetched
   from Gazebo Fuel on first use and may require an internet connection.
   Pass `spawn_assignment_objects:=false` to disable the props.

3. In a second terminal, teleoperate the robot to explore the environment and
   move the camera close enough to view the props:

   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel

4. In RViz2, confirm that walls, corridors, and obstacles are visible. Drive the robot through most of the drivable area.

5. Save the generated map to a new name so the old map is kept as a backup:

   ros2 run nav2_map_server map_saver_cli \
     -f ~/tb4_ws/src/tb4_navigation_practice/maps/map_with_objects

   This creates:
   - `~/tb4_ws/src/tb4_navigation_practice/maps/map_with_objects.yaml`
   - `~/tb4_ws/src/tb4_navigation_practice/maps/map_with_objects.pgm`

   The old map does not contain the newly added obstacles, so do not use it
   for localization/navigation in this modified world. Use the newly saved
   map for the next steps.

6. Start localization and navigation using the new map:

   ros2 launch tb4_navigation_practice tb4_navigation.launch.py \
     map:=$HOME/tb4_ws/src/tb4_navigation_practice/maps/map_with_objects.yaml

7. In RViz2, set the robot's **2D Pose Estimate** and verify the LiDAR scan
   aligns with the walls before starting autonomous navigation.

## Assignment: waypoint navigation and YOLO

The package includes a waypoint node and a camera detection node. The first
three waypoints in `config/goals.yaml` are the coordinates recorded with
RViz2 Publish Point. A fourth waypoint `(0, 0, 0)` returns the robot to the
simulation's default start pose. Confirm that your Gazebo spawn pose and
AMCL initial pose match that start coordinate before using the return goal.
Store each waypoint as `(x, y, yaw)` in the `map` frame, with yaw in radians.

Install the vision dependencies in the same Python environment used to run
the ROS node:

```bash
python3 -m pip install --user \
  ultralytics 'numpy<2' 'opencv-python<4.12' \
  'setuptools>=77,<80' 'packaging>=22'
```

The `yolo_detector` uses the camera topic from `config/yolo.yaml` by default.
Check the real topic before running and override `image_topic` if needed:

```bash
ros2 topic list | grep -E 'image|camera'
ros2 topic info /oakd/rgb/preview/image_raw
```

Build and source the workspace after editing package files:

```bash
cd ~/tb4_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select tb4_navigation_practice
source install/setup.bash
```

Start the simulation, localization and Nav2 in one terminal:

```bash
ros2 launch tb4_navigation_practice tb4_navigation.launch.py \
  world:=maze map:=/absolute/path/to/map.yaml
```

In RViz2, set **2D Pose Estimate**, then confirm `/amcl_pose` is stable and
`/scan` aligns with the map. Only then start the assignment nodes in another
terminal. The waypoint node sends all configured goals in sequence; it stops if one
fails. The YOLO node publishes annotated images to
`/yolo/detections/image` and reports detected class names and confidence in
the terminal:

```bash
ros2 launch tb4_navigation_practice tb4_assignment.launch.py
```

To resume at a specific waypoint, pass its zero-based `start_goal_index`;
for example, `3` starts directly at Goal 4 (the return-to-start waypoint):

```bash
ros2 run tb4_navigation_practice waypoint_navigator --ros-args \
  --params-file "$(ros2 pkg prefix tb4_navigation_practice)/share/tb4_navigation_practice/config/goals.yaml" \
  -p start_goal_index:=3
```

In RViz2, add an **Image** display subscribed to `/yolo/detections/image`.
Set `show_window: true` in `config/yolo.yaml` to display an OpenCV window on a
desktop session. To override the camera topic without editing the file:

```bash
ros2 run tb4_navigation_practice yolo_detector --ros-args \
  -p image_topic:=/your/actual/camera/topic
```

The default model is `yolov8n.pt`; Ultralytics may download model weights on
first use. Its pretrained classes do not cover every possible simulation
object, so use a suitable custom model if the assignment requires a specific
class not recognized by the pretrained weights.
The default inference device is CPU so the node works with systems whose
NVIDIA driver cannot run the installed PyTorch CUDA build. Inference is
limited to two PyTorch CPU threads by default to leave resources for Gazebo;
stop an already running YOLO node before restarting SLAM, and start the
assignment launch after mapping/localization is stable.
The scene contains physical collisions for the chair, person, boxes and
traffic light, so SLAM can map them. The COCO-pretrained YOLO model can detect
classes such as `person` and `chair`, but COCO has no generic `box` class;
boxes may not be named/detected as boxes without training or a model that
supports open-vocabulary prompts. Verify detections from the actual camera
image rather than assuming every Gazebo prop is recognized.

## Notes

- The default world for mapping, localization, and navigation is the TurtleBot 4 maze world.
- The package's `maps/map.yaml` and `maps/map.pgm` are the shared map files used by localization and navigation. Pass `map:=/full/path/to/map.yaml` to either launch to select a different map.
- If you want to use a different world or map, change the launch arguments accordingly.
