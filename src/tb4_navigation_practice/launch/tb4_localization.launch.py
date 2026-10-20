from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


pkg_tb4 = get_package_share_directory('tb4_navigation_practice')
pkg_turtlebot4_navigation = get_package_share_directory('turtlebot4_navigation')

ARGUMENTS = [
    DeclareLaunchArgument(
        'world',
        default_value='maze',
        description='Ignition world to launch.'
    ),
    DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution([pkg_tb4, 'maps', 'map.yaml']),
        description='Full path to the saved map YAML file.'
    ),
    DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        choices=['true', 'false'],
        description='Use sim time.'
    ),
    DeclareLaunchArgument(
        'spawn_assignment_objects',
        default_value='true',
        choices=['true', 'false'],
        description='Spawn static assignment props in Gazebo.',
    ),
]


def generate_launch_description():
    launch = LaunchDescription(ARGUMENTS)

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_tb4, 'launch', 'tb4_sim.launch.py'])]
        ),
        launch_arguments=[
            ('world', LaunchConfiguration('world')),
            (
                'spawn_assignment_objects',
                LaunchConfiguration('spawn_assignment_objects'),
            ),
        ],
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([
                pkg_turtlebot4_navigation,
                'launch',
                'localization.launch.py',
            ])]
        ),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('map', LaunchConfiguration('map')),
            ('params', PathJoinSubstitution([
                pkg_tb4,
                'config',
                'localization_params.yaml',
            ])),
        ],
    )

    launch.add_action(sim)
    launch.add_action(localization)
    return launch
