import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import TwistStamped
from delivery_mission_interfaces.action import DeliveryMission

PICKUP_PAUSE = 3.0
RATE_HZ = 10.0


class DeliveryMissionNode(Node):
    def __init__(self):
        super().__init__('delivery_mission_node')
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.server = ActionServer(
            self,
            DeliveryMission,
            'delivery_mission',
            execute_callback=self.execute_cb,
            goal_callback=self.goal_cb,
            cancel_callback=self.cancel_cb,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info('delivery_mission action server started')

    def goal_cb(self, goal):
        self.get_logger().info(f'goal received: speed={goal.speed}, pickup={goal.pickup_duration}, '
                                f'delivery={goal.delivery_duration}, timeout={goal.timeout}')
        return GoalResponse.ACCEPT

    def cancel_cb(self, goal_handle):
        self.get_logger().info('cancel requested')
        return CancelResponse.ACCEPT

    def move(self, speed):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = speed
        self.pub.publish(msg)

    def run_phase(self, goal_handle, name, duration, speed, start_time, timeout):
        phase_start = time.monotonic()
        self.get_logger().info(f'phase started: {name}')

        while True:
            t = time.monotonic()
            elapsed_phase = t - phase_start
            elapsed_total = t - start_time

            if goal_handle.is_cancel_requested:
                self.move(0.0)
                self.get_logger().warn(f'phase {name} canceled')
                return 'canceled'

            if elapsed_total > timeout:
                self.move(0.0)
                self.get_logger().error(f'phase {name} aborted: timeout exceeded')
                return 'timeout'

            if elapsed_phase >= duration:
                self.get_logger().info(f'phase finished: {name}')
                return 'ok'

            self.move(speed)

            fb = DeliveryMission.Feedback()
            fb.current_phase = name
            fb.phase_progress = 100.0 * elapsed_phase / duration if duration > 0 else 100.0
            fb.elapsed_time = elapsed_total
            fb.remaining_time = max(0.0, timeout - elapsed_total)
            goal_handle.publish_feedback(fb)

            time.sleep(1.0 / RATE_HZ)

    def execute_cb(self, goal_handle):
        goal = goal_handle.request
        start_time = time.monotonic()
        self.get_logger().info('mission started')

        status = self.run_phase(goal_handle, 'DRIVING_TO_PICKUP', goal.pickup_duration,
                                 goal.speed, start_time, goal.timeout)

        if status == 'ok':
            status = self.run_phase(goal_handle, 'PICKING_UP', PICKUP_PAUSE,
                                     0.0, start_time, goal.timeout)

        if status == 'ok':
            status = self.run_phase(goal_handle, 'DRIVING_TO_DELIVERY', goal.delivery_duration,
                                     goal.speed, start_time, goal.timeout)

        self.move(0.0)
        result = DeliveryMission.Result()

        if status == 'ok':
            result.success = True
            result.message = 'mission completed successfully'
            goal_handle.succeed()
            self.get_logger().info(result.message)
        elif status == 'canceled':
            result.success = False
            result.message = 'mission canceled'
            goal_handle.canceled()
            self.get_logger().warn(result.message)
        else:
            result.success = False
            result.message = 'mission aborted, timeout exceeded'
            goal_handle.abort()
            self.get_logger().error(result.message)

        return result


def main(args=None):
    rclpy.init(args=args)
    node = DeliveryMissionNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == '__main__':
    main()