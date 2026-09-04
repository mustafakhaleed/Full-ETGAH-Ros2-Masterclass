import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('my_robot_description')
    turtlebot3_gazebo_share = get_package_share_directory('turtlebot3_gazebo')

    world_file = os.path.join(
        turtlebot3_gazebo_share,
        'worlds',
        'turtlebot3_house.world'
    )

    xacro_file = os.path.join(
        pkg_share,
        'urdf',
        'robot.urdf.xacro'
    )

    bridge_file = os.path.join(
        pkg_share,
        'config',
        'gz_bridge.yaml'
    )

    robot_description = xacro.process_file(xacro_file).toxml()

    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
            os.path.dirname(pkg_share),
            turtlebot3_gazebo_share
        ])
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}'
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'two_wheel_robot',
            '-x', '-2.0',
            '-y', '0.5',
            '-z', '0.0',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '1.57'
        ],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[
            {'config_file': bridge_file},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_resource_path,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        bridge
    ])