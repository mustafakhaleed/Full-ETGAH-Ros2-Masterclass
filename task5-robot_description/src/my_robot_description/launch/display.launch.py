import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Path to the Xacro file
    urdf_xacro_file_path = os.path.join(
        get_package_share_directory('my_robot_description'),
        'urdf',
        'robot.urdf.xacro'
    )

    # Path to the saved RViz config
    rviz_config_file_path = os.path.join(
        get_package_share_directory('my_robot_description'),
        'rviz',
        'robot_view.rviz'
    )

    # Dynamically process Xacro file into URDF string
    robot_description_content = Command(['xacro ', urdf_xacro_file_path])

    # Wrap as a string parameter
    robot_description_param = ParameterValue(robot_description_content, value_type=str)

    ld = LaunchDescription()

    # Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_param}]
    )
    ld.add_action(robot_state_publisher_node)

    # Joint State Publisher GUI Node (sliders for the driven wheels + caster)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )
    ld.add_action(joint_state_publisher_gui_node)

    # RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=(
            ['-d', rviz_config_file_path]
            if os.path.exists(rviz_config_file_path) else []
        )
    )
    ld.add_action(rviz_node)

    return ld