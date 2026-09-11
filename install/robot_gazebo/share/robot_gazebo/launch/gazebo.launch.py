#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro
from launch.actions import TimerAction


def generate_launch_description():

    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world = os.path.join(pkg_robot_gazebo, 'worlds', 'my_world.sdf')

    # Construct resource paths so 'model://simple_building' and 'model://robot_gazebo/...' both resolve
    models_path = os.path.join(pkg_robot_gazebo, 'models')
    pkg_parent_share = os.path.abspath(os.path.join(pkg_robot_gazebo, '..'))
    resource_paths = f"{models_path}:{pkg_parent_share}"

    bridge_file = os.path.join(pkg_robot_gazebo, 'config', 'gz_bridge.yaml')
    xacro_file = os.path.join(pkg_robot_gazebo, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=resource_paths
    )

    # --- Machine-specific NVIDIA Optimus workaround ---
    # Only needed on laptops that hit the Ogre2 "material datablock already
    # exists" crash caused by EGL falling back to the wrong GPU. Comment
    # these two out if running on a machine without this specific issue.
    set_nv_prime = SetEnvironmentVariable(
        name='__NV_PRIME_RENDER_OFFLOAD',
        value='1'
    )
    set_glx_vendor = SetEnvironmentVariable(
        name='__GLX_VENDOR_LIBRARY_NAME',
        value='nvidia'
    )

    # Single combined Gazebo Sim launch (server + GUI together).
    # Do NOT also add separate gzserver/gzclient IncludeLaunchDescription
    # actions alongside this one -- running Gazebo more than once at the
    # same time causes resource conflicts and crashes.
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -v2 {world}'
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


    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[
            {'config_file': bridge_file},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    spawn_robot = Node(
    package='ros_gz_sim',
    executable='create',
    arguments=[
        '-name', 'Eissa',
        '-topic', 'robot_description',
        '-x', '1', '-y', '2', '-z', '0.2'
    ],
    output='screen'
)
#     delayed_spawn = TimerAction(
#     period=2.0,
#     actions=[spawn_robot]
# )

    ld = LaunchDescription()

    ld.add_action(set_gz_resource_path)
    ld.add_action(set_nv_prime)
    ld.add_action(set_glx_vendor)

    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(bridge)
    ld.add_action(spawn_robot)

    return ld