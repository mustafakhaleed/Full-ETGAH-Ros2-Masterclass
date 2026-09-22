import math
import rclpy
import rclpy.time
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Quaternion
import tf2_ros


def yaw_to_quaternion(yaw: float) -> Quaternion:
    """Convert a yaw angle (radians) into a geometry_msgs/Quaternion
    (rotation about Z only, which is all a ground robot needs)."""
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


# Waypoint name -> (x, y, yaw) in the map frame.
WAYPOINTS = {
    'Home':     (0.0, 0.0, 0.0),
    'Loading':  (7.88, -3.22, 1.57),
    'Storage':  (10.78, 0.08, 0.0),
    'Shipping': (19.66, -3.42, -1.57),
}


class WaypointMarkerPublisher(Node):
    def __init__(self):
        super().__init__('waypoint_marker_publisher')

        self.marker_pub = self.create_publisher(
            MarkerArray,
            'waypoint_markers',
            10
        )

        # Setup TF buffer and listener bound directly to this node
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # List to store points of the robot's actual path in map frame
        self.robot_path_points = []

        self.waypoints = WAYPOINTS

        self.active_goal = None

        # Track robot pose fast (every 0.1s)
        self.track_timer = self.create_timer(0.1, self.track_robot_pose)

        # Publish markers every second
        self.timer = self.create_timer(1.0, self.publish_markers)

    def track_robot_pose(self):
        """Lookup robot's exact pose in the 'map' frame using TF."""
        try:
            # Check transform from map -> base_footprint
            if self.tf_buffer.can_transform('map', 'base_footprint', rclpy.time.Time()):
                transform = self.tf_buffer.lookup_transform(
                    'map',
                    'base_footprint',
                    rclpy.time.Time()
                )

                x = transform.transform.translation.x
                y = transform.transform.translation.y
                z = transform.transform.translation.z

                new_point = Point(x=x, y=y, z=z + 0.05)

                # Record point if first point or if robot moved > 5cm
                if not self.robot_path_points:
                    self.robot_path_points.append(new_point)
                else:
                    last = self.robot_path_points[-1]
                    dist = ((x - last.x) ** 2 + (y - last.y) ** 2) ** 0.5
                    if dist > 0.05:
                        self.robot_path_points.append(new_point)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            pass

    def publish_markers(self):
        marker_array = MarkerArray()
        marker_id = 0

        # ---------------------------------------------------------
        # Blue line showing actual driven path in map frame
        # ---------------------------------------------------------
        if self.robot_path_points:
            line = Marker()
            line.header.frame_id = 'map'
            line.header.stamp = self.get_clock().now().to_msg()
            line.ns = 'actual_robot_path'
            line.id = marker_id
            marker_id += 1

            line.type = Marker.LINE_STRIP
            line.action = Marker.ADD
            line.pose.orientation.w = 1.0
            line.scale.x = 0.08  # Line thickness

            # Blue color
            line.color.r = 0.0
            line.color.g = 0.0
            line.color.b = 1.0
            line.color.a = 1.0

            line.points = self.robot_path_points
            marker_array.markers.append(line)

        # ---------------------------------------------------------
        # Waypoint spheres, orientation arrows, and labels
        # ---------------------------------------------------------
        for name, (x, y, yaw) in self.waypoints.items():
            orientation = yaw_to_quaternion(yaw)

            # Waypoint sphere
            sphere = Marker()
            sphere.header.frame_id = 'map'
            sphere.header.stamp = self.get_clock().now().to_msg()
            sphere.ns = 'waypoints'
            sphere.id = marker_id
            marker_id += 1

            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.position = Point(x=x, y=y, z=0.0)
            sphere.pose.orientation = orientation

            sphere.scale.x = 0.4
            sphere.scale.y = 0.4
            sphere.scale.z = 0.4

            if name == self.active_goal:
                sphere.color.r = 0.0
                sphere.color.g = 1.0
                sphere.color.b = 0.0
                sphere.color.a = 1.0
            else:
                sphere.color.r = 0.0
                sphere.color.g = 0.0
                sphere.color.b = 1.0
                sphere.color.a = 1.0

            marker_array.markers.append(sphere)

            # Orientation arrow
            arrow = Marker()
            arrow.header.frame_id = 'map'
            arrow.header.stamp = self.get_clock().now().to_msg()
            arrow.ns = 'waypoint_orientations'
            arrow.id = marker_id
            marker_id += 1

            arrow.type = Marker.ARROW
            arrow.action = Marker.ADD
            arrow.pose.position = Point(x=x, y=y, z=0.05)
            arrow.pose.orientation = orientation

            arrow.scale.x = 0.6   # length
            arrow.scale.y = 0.08  # shaft diameter
            arrow.scale.z = 0.08  # head diameter

            arrow.color.r = 1.0
            arrow.color.g = 0.65
            arrow.color.b = 0.0
            arrow.color.a = 1.0

            marker_array.markers.append(arrow)

            # Waypoint text label
            text = Marker()
            text.header.frame_id = 'map'
            text.header.stamp = self.get_clock().now().to_msg()
            text.ns = 'waypoint_labels'
            text.id = marker_id
            marker_id += 1

            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD

            text.pose.position = Point(x=x, y=y, z=0.5)
            text.pose.orientation.w = 1.0
            text.scale.z = 0.3

            text.color.r = 1.0
            text.color.g = 1.0
            text.color.b = 1.0
            text.color.a = 1.0

            text.text = name

            marker_array.markers.append(text)

        self.marker_pub.publish(marker_array)

    def set_active_goal(self, name):
        """Set the current active waypoint. Pass None to clear (all blue)."""
        self.get_logger().info(f'Active goal changed to: {name}')
        self.active_goal = name
        self.publish_markers()


def main(args=None):
    rclpy.init(args=args)
    node = WaypointMarkerPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()