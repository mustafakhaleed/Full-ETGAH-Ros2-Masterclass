import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelSubscriber(Node):
    def __init__(self):
        super().__init__('cmd_vel_Sub_Handler')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10)
        self.subscription  # prevent unused variable warning

    def cmd_vel_callback(self, msg):
        linear_velocity = msg.linear.x
        angular_velocity = msg.angular.z
        self.get_logger().info(f'Received cmd_vel: linear={linear_velocity}, angular={angular_velocity}')


def main(args=None):
    rclpy.init(args=args)
    cmd_vel_subscriber = CmdVelSubscriber()
    rclpy.spin(cmd_vel_subscriber)
    cmd_vel_subscriber.destroy_node()
    rclpy.shutdown()        

if __name__ == '__main__':
    main()        