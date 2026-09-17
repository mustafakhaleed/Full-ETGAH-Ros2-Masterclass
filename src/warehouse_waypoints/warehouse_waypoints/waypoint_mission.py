import rclpy
import threading
import time
from geometry_msgs.msg import PoseStamped
from rclpy.executors import SingleThreadedExecutor
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from warehouse_waypoints.waypoint_markers import (
    WaypointMarkerPublisher,
    WAYPOINTS,
    yaw_to_quaternion,
)

# Mission order (Home is the start; the robot returns there last)
MISSION_ORDER = ['Loading', 'Storage', 'Shipping', 'Home']

# How long to wait at the Loading Station (seconds)
LOADING_WAIT_SECONDS = 30.0


def make_pose(navigator, x, y, yaw):
    """Build a PoseStamped that includes the stored orientation for
    the station, not just an identity quaternion."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation = yaw_to_quaternion(yaw)
    return pose


def run_mission(navigator, marker_node):
    # Mission starts at Home - mark it active so RViz reflects the
    # robot's starting station before the first goal is sent.
    marker_node.set_active_goal('Home')

    for name in MISSION_ORDER:
        marker_node.get_logger().info(f'Navigating to {name}...')

        # Set the current waypoint as active (turns it green,
        # republishes MarkerArray immediately)
        marker_node.set_active_goal(name)

        x, y, yaw = WAYPOINTS[name]
        goal_pose = make_pose(navigator, x, y, yaw)

        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            time.sleep(0.1)

        result = navigator.getResult()

        if result != TaskResult.SUCCEEDED:
            marker_node.get_logger().error(f'Failed to reach {name}')
            return

        marker_node.get_logger().info(f'Reached {name}')

        # Stop for 30 seconds at the Loading station
        if name == 'Loading':
            marker_node.get_logger().info(
                f'Waiting {int(LOADING_WAIT_SECONDS)} seconds at Loading Station...'
            )
            time.sleep(LOADING_WAIT_SECONDS)
            marker_node.get_logger().info(
                '30-second wait completed. Continuing mission...'
            )

    # Mission completed - robot is back at Home, keep it highlighted green as the final destination
    marker_node.get_logger().info(
        'Mission complete. Returned to Home.'
    )


def main(args=None):
    rclpy.init(args=args)

    navigator = BasicNavigator()
    navigator.waitUntilNav2Active()

    marker_node = WaypointMarkerPublisher()

    marker_executor = SingleThreadedExecutor()
    marker_executor.add_node(marker_node)
    spin_thread = threading.Thread(target=marker_executor.spin, daemon=True)
    spin_thread.start()

    # Give discovery a moment before changing any state
    time.sleep(1.5)

    run_mission(navigator, marker_node)

    marker_executor.shutdown()
    spin_thread.join(timeout=2.0)
    marker_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()