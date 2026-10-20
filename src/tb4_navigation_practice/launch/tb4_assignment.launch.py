import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory(
        'tb4_navigation_practice'
    )
    return LaunchDescription([
        Node(
            package='tb4_navigation_practice',
            executable='waypoint_navigator',
            name='waypoint_navigator',
            output='screen',
            parameters=[os.path.join(package_share, 'config', 'goals.yaml')],
        ),
        Node(
            package='tb4_navigation_practice',
            executable='yolo_detector',
            name='yolo_detector',
            output='screen',
            parameters=[os.path.join(package_share, 'config', 'yolo.yaml')],
        ),
    ])
