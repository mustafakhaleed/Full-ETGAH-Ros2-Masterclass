import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_Pub_Handler')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        
    def run(self):
        while rclpy.ok():
            msg = Twist()
            User_In = input("Enter (W/A/S/D) for Moving , or Q for Stopping").strip().upper()
            if User_In == 'Q':
                print(f"Robot 's Stopping ")
                self.publisher_.publish(msg)   # empty msg to stop the robot , No linear or angular velocity has been given
                break
            elif User_In == 'W':
                print("Moving Forward")
                msg.linear.x = 0.2
            elif User_In == 'S':
                print("Moving Backward")
                msg.linear.x = -0.2            
            elif User_In == 'D':
                print("Moving Forward but to Right")
                msg.linear.x = 0.1
                msg.angular.z = -0.2
            elif User_In == 'A':
                print("Moving Forward but to Left")
                msg.linear.x = 0.1
                msg.angular.z = 0.2           
            else :
                print(f"Please Enter (W/A/S/D) for Moving , or Q for Stopping ")
                continue
            self.publisher_.publish(msg)
            self.get_logger().info(f'Publishing: linear={msg.linear.x}, angular={msg.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    cmd_vel_publisher = CmdVelPublisher()
    
    try:
        cmd_vel_publisher.run()
    except KeyboardInterrupt:
        pass
    finally:
        cmd_vel_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
