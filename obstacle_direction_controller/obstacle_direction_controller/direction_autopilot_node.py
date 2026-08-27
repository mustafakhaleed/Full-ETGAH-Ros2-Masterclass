import sys
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
from set_dir.srv import SetDirection

class DirectionAuto(Node):
    def __init__(self):
        super().__init__('direction_auto')

        # Service server
        self.srv = self.create_service(SetDirection, 'set_direction', self.set_direction_callback)

        # Publishers and subscribers
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

        # State variables
        self.front_distance = float('inf')
        self.left_distance = float('inf')
        self.right_distance = float('inf')
        self.current_state = 'forward'
        self.manual_override = False
        self.override_timer = None
        self.state_entry_time = self.get_clock().now()
        self.MIN_TURN_DURATION = 1.0  # min seconds to hold a turn before going back to forward

        self.get_logger().info('Direction Auto Node initialized.')

    def set_direction_callback(self, request, response):
        valid_directions = ['forward', 'reverse', 'left', 'right']
        requested_dir = request.direction.lower()

        if requested_dir in valid_directions:
            self.manual_override = True
            self.current_state = requested_dir
            self.state_entry_time = self.get_clock().now()
            self.get_logger().info(f'[OVERRIDE] Executing manual command: {requested_dir}')

            # Reset the override timer so it ends 3s after the latest command
            if self.override_timer is not None:
                self.override_timer.cancel()
            self.override_timer = self.create_timer(3.0, self.reset_override)

            response.success = True
            response.message = f"Movement set to '{requested_dir}' for 3 seconds."
        else:
            response.success = False
            response.message = f"Invalid direction '{requested_dir}'"

        return response

    def reset_override(self):
        """Turn off manual override and resume autonomous control."""
        self.manual_override = False
        if self.override_timer is not None:
            self.override_timer.cancel()
            self.override_timer = None
        self.get_logger().info('[AUTOPILOT] Resuming autonomous obstacle avoidance.')

    @staticmethod
    def _clean_range(value, range_max):
        """Return a safe finite distance for a single LiDAR ray."""
        if value == float('inf') or value == 0.0 or value != value:
            return range_max
        return value

    def scan_callback(self, msg):
        if len(msg.ranges) == 0 or msg.angle_increment == 0.0:
            return

        def indices_for_angle_window(center_deg, half_width_deg):
            """Return the ranges slice for [center-half, center+half] degrees.
            0 deg = straight ahead, positive = left (LaserScan convention)."""
            center_rad = math.radians(center_deg)
            half_rad = math.radians(half_width_deg)
            lo_angle = center_rad - half_rad
            hi_angle = center_rad + half_rad
            lo_idx = int(round((lo_angle - msg.angle_min) / msg.angle_increment))
            hi_idx = int(round((hi_angle - msg.angle_min) / msg.angle_increment))
            lo_idx, hi_idx = sorted((lo_idx, hi_idx))
            lo_idx = max(0, lo_idx)
            hi_idx = min(len(msg.ranges) - 1, hi_idx)
            if hi_idx < lo_idx:
                return []
            return msg.ranges[lo_idx:hi_idx + 1]

        def window_min(window):
            cleaned = [self._clean_range(v, msg.range_max) for v in window]
            return min(cleaned) if cleaned else msg.range_max

        # Wide cones with no gaps between them (front covers -35..35,
        # left covers 35..145, right covers -145..-35) so a diagonal
        # obstacle can't hide in a blind spot between the cones and
        # clip the robot while it's turning.
        self.front_distance = window_min(indices_for_angle_window(0, 35))
        self.left_distance = window_min(indices_for_angle_window(90, 55))
        self.right_distance = window_min(indices_for_angle_window(-90, 55))

        # Only run autopilot logic when not manually overridden
        if not self.manual_override:
            new_state = self.current_state

            # Hysteresis: "enter" threshold triggers a change, "exit"
            # threshold (further away) is needed to switch back, so
            # readings near one cutoff don't cause rapid flapping.
            #
            # LiDAR readings are distance from the robot's center, not
            # from its edge. TurtleBot3 Waffle has ~0.22m radius, so we
            # add that (plus a small buffer) to every threshold below —
            # otherwise "0.5m to the obstacle" really means the edge of
            # the robot is only ~0.28m away.
            ROBOT_RADIUS = 0.22
            SAFETY_BUFFER = 0.10
            CLEARANCE = ROBOT_RADIUS + SAFETY_BUFFER  # ~0.32m

            REVERSE_ENTER = 0.5 + CLEARANCE
            REVERSE_EXIT = 0.7 + CLEARANCE
            TURN_ENTER = 1.2 + CLEARANCE
            TURN_EXIT = 1.5 + CLEARANCE
            SIDE_CLEARANCE = 0.6 + CLEARANCE  # min clearance needed on both sides before driving forward again

            if self.current_state == 'reverse':
                if self.front_distance >= REVERSE_EXIT:
                    new_state = 'left' if self.left_distance >= self.right_distance else 'right'
            elif self.current_state in ('left', 'right'):
                turning_duration = (self.get_clock().now() - self.state_entry_time).nanoseconds / 1e9
                if self.front_distance < REVERSE_ENTER:
                    new_state = 'reverse'
                elif (self.front_distance >= TURN_EXIT
                      and self.left_distance >= SIDE_CLEARANCE
                      and self.right_distance >= SIDE_CLEARANCE
                      and turning_duration >= self.MIN_TURN_DURATION):
                    new_state = 'forward'
                # else: keep turning — front, a side, or the timer isn't clear yet
            else:  # 'forward' or anything else
                if self.front_distance < REVERSE_ENTER:
                    new_state = 'reverse'
                elif self.front_distance < TURN_ENTER:
                    new_state = 'left' if self.left_distance >= self.right_distance else 'right'
                elif self.left_distance < SIDE_CLEARANCE:
                    new_state = 'right'  # something close on the left, steer away
                elif self.right_distance < SIDE_CLEARANCE:
                    new_state = 'left'   # something close on the right, steer away
                else:
                    new_state = 'forward'

            if new_state != self.current_state:
                self.state_entry_time = self.get_clock().now()
                self.get_logger().info(
                    f'[AUTOPILOT] State: {self.current_state} -> {new_state} '
                    f'(Front: {self.front_distance:.2f}m, L: {self.left_distance:.2f}m, R: {self.right_distance:.2f}m)'
                )
                self.current_state = new_state

    def timer_callback(self):
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        # Speed values for each state
        if self.current_state == 'forward':
            cmd.twist.linear.x = 0.2
            cmd.twist.angular.z = 0.0
        elif self.current_state == 'left':
            cmd.twist.linear.x = 0.03
            cmd.twist.angular.z = 0.7   # turn left, wider swing for more clearance
        elif self.current_state == 'right':
            cmd.twist.linear.x = 0.03
            cmd.twist.angular.z = -0.7  # turn right, wider swing for more clearance
        elif self.current_state == 'reverse':
            cmd.twist.linear.x = -0.15
            cmd.twist.angular.z = 0.0

        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = DirectionAuto()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()