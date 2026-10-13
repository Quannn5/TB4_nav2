from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


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

    launch.add_action(sim)
    launch.add_action(rviz)
    return launch
