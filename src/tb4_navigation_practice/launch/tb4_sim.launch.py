from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument(
        'world',
        default_value='warehouse',
        description='Ignition world to launch.'
    ),
    DeclareLaunchArgument(
        'model',
        default_value='standard',
        choices=['standard', 'lite'],
        description='TurtleBot 4 model.'
    ),
    DeclareLaunchArgument(
        'x',
        default_value='0.0',
        description='Initial robot x position.'
    ),
    DeclareLaunchArgument(
        'y',
        default_value='0.0',
        description='Initial robot y position.'
    ),
    DeclareLaunchArgument(
        'z',
        default_value='0.0',
        description='Initial robot z position.'
    ),
    DeclareLaunchArgument(
        'yaw',
        default_value='0.0',
        description='Initial robot yaw angle.'
    ),
    DeclareLaunchArgument(
        'spawn_assignment_objects',
        default_value='true',
        choices=['true', 'false'],
        description='Spawn static chair, boxes, person, and traffic light.',
    ),
]


def generate_launch_description():
    pkg_ignition = get_package_share_directory('turtlebot4_ignition_bringup')
    pkg_viz = get_package_share_directory('turtlebot4_viz')

    ignition_launch = PathJoinSubstitution(
        [pkg_ignition, 'launch', 'turtlebot4_ignition.launch.py']
    )
    view_robot_launch = PathJoinSubstitution(
        [pkg_viz, 'launch', 'view_robot.launch.py']
    )

    launch = LaunchDescription(ARGUMENTS)

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([ignition_launch]),
        launch_arguments=[
            ('world', LaunchConfiguration('world')),
            ('model', LaunchConfiguration('model')),
            ('x', LaunchConfiguration('x')),
            ('y', LaunchConfiguration('y')),
            ('z', LaunchConfiguration('z')),
            ('yaw', LaunchConfiguration('yaw')),
            ('rviz', 'false'),
        ],
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([view_robot_launch]),
        launch_arguments=[
            ('use_sim_time', 'true'),
            ('description', 'true'),
            ('model', LaunchConfiguration('model')),
        ],
    )

    model_dir = PathJoinSubstitution([
        get_package_share_directory('tb4_navigation_practice'),
        'models',
    ])
    object_spawns = [
        ('yolo_chair', 'chair.sdf', '-5.0', '-7.0', '0.0', '0.0'),
        ('yolo_box_red', 'box.sdf', '8.0', '-3.0', '0.0', '0.0'),
        ('yolo_box_yellow', 'box.sdf', '-3.0', '5.0', '0.0', '0.0'),
        ('yolo_box_green', 'box.sdf', '3.0', '-3.0', '0.0', '0.0'),
        ('yolo_person', 'person.sdf', '3.0', '4.0', '0.0', '3.14'),
        ('yolo_traffic_light', 'traffic_light.sdf', '5.0', '-8.0', '0.0', '3.4'),
        ('yolo_chair_2', 'chair.sdf', '5.0', '4.0', '0.0', '1.57'),
        ('yolo_person_2', 'person.sdf', '-3.0', '-1.0', '0.0', '0.0'),
        ('yolo_box_blue', 'box_blue.sdf', '-1.0', '-7.0', '0.0', '0.0'),
    ]
    spawn_nodes = [
        Node(
            package='ros_gz_sim',
            executable='create',
            name=f'spawn_{name}',
            arguments=[
                '-world', LaunchConfiguration('world'),
                '-file', PathJoinSubstitution([model_dir, model_file]),
                '-name', name,
                '-x', x,
                '-y', y,
                '-z', z,
                '-Y', yaw,
            ],
            output='screen',
            condition=IfCondition(
                LaunchConfiguration('spawn_assignment_objects')
            ),
        )
        for name, model_file, x, y, z, yaw in object_spawns
    ]
    spawn_objects = [
        TimerAction(period=8.0, actions=[spawn_nodes[0]]),
        *[
            RegisterEventHandler(
                OnProcessExit(
                    target_action=previous,
                    on_exit=[TimerAction(period=3.0, actions=[next_node])],
                )
            )
            for previous, next_node in zip(spawn_nodes, spawn_nodes[1:])
        ],
    ]

    launch.add_action(sim)
    launch.add_action(rviz)
    for spawn_action in spawn_objects:
        launch.add_action(spawn_action)
    return launch
