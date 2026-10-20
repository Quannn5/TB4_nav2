import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def create_pose(navigator, frame_id, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main(args=None):
    rclpy.init(args=args)
    navigator = BasicNavigator(node_name='waypoint_navigator')
    try:
        frame_id = navigator.declare_parameter('frame_id', 'map').value
        goals = navigator.declare_parameter(
            'goals',
            [
                -5.25, -7.15, 0.0,
                0.25, -0.15, 0.0,
                4.25, 6.75, 0.0,
            ],
        ).value
        start_goal_index = navigator.declare_parameter(
            'start_goal_index', 0
        ).value
        if len(goals) < 9 or len(goals) % 3:
            raise ValueError(
                'The goals parameter must contain at least three '
                '(x, y, yaw) triples.'
            )
        goal_count = len(goals) // 3
        if not 0 <= start_goal_index < goal_count:
            raise ValueError(
                f'start_goal_index must be between 0 and {goal_count - 1}.'
            )

        formatted_goals = [
            f'Goal {index // 3 + 1}=({goals[index]:.3f}, '
            f'{goals[index + 1]:.3f}, {goals[index + 2]:.3f})'
            for index in range(0, len(goals), 3)
        ]
        navigator.get_logger().info(
            f'Loaded {goal_count} goals in frame "{frame_id}": '
            + '; '.join(formatted_goals)
        )
        if start_goal_index:
            navigator.get_logger().info(
                f'Resuming at Goal {start_goal_index + 1}.'
            )
        navigator.get_logger().info(
            'Waiting for Nav2 to become active. Set and verify the initial '
            'pose in RViz2 before starting this node.'
        )
        try:
            navigator.waitUntilNav2Active()
        except Exception as exc:  # noqa: BLE001 - need a clearer startup message.
            navigator.get_logger().warning(
                'Nav2 is not active yet or the robot initial pose is not set. '
                'Use RViz2 -> 2D Pose Estimate, then rerun the waypoint node. '
                f'Original error: {exc}'
            )
            return

        for index in range(start_goal_index * 3, len(goals), 3):
            goal_number = index // 3 + 1
            x, y, yaw = goals[index:index + 3]
            navigator.get_logger().info(
                f'Sending Goal {goal_number}: '
                f'x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad'
            )
            navigator.goToPose(
                create_pose(navigator, frame_id, x, y, yaw)
            )
            while not navigator.isTaskComplete():
                pass

            result = navigator.getResult()
            if result != TaskResult.SUCCEEDED:
                navigator.get_logger().error(
                    f'Goal {goal_number} did not succeed (result={result}). '
                    'Stopping the waypoint sequence.'
                )
                return
            navigator.get_logger().info(f'Goal {goal_number} reached.')
        navigator.get_logger().info('All waypoint goals reached.')
    finally:
        navigator.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
