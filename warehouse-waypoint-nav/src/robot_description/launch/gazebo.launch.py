#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    pkg_robot_gazebo = get_package_share_directory('robot_description')
    pkg_warehouse_world = get_package_share_directory('warehouse_world')

    models_path = os.path.join(pkg_robot_gazebo, 'models')
    pkg_parent_share = os.path.abspath(os.path.join(pkg_robot_gazebo, '..'))
    warehouse_share = os.path.abspath(os.path.join(pkg_warehouse_world, '..'))

    # Merge our own resource paths with the warehouse_world ones here,
    # since warehouse_storage_launch.launch.py overwrites GZ_SIM_RESOURCE_PATH
    # instead of appending to it.
    resource_paths = ':'.join([
        pkg_parent_share,
        models_path,
        warehouse_share,
        pkg_robot_gazebo,
        os.path.join(pkg_warehouse_world, 'worlds'),
        os.path.join(pkg_warehouse_world, 'models'),
        os.path.abspath(os.path.join(pkg_warehouse_world, '..'))
    ])

    bridge_file = os.path.join(pkg_robot_gazebo, 'config', 'gz_bridge.yaml')
    xacro_file = os.path.join(pkg_robot_gazebo, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # Pass custom Nvidia & Network environment settings directly to Gazebo
    set_nv_prime = SetEnvironmentVariable(name='__NV_PRIME_RENDER_OFFLOAD', value='1')
    set_glx_vendor = SetEnvironmentVariable(name='__GLX_VENDOR_LIBRARY_NAME', value='nvidia')
    set_egl_vendor = SetEnvironmentVariable(name='__EGL_VENDOR_LIBRARY_NAME', value='nvidia')
    set_gz_ip = SetEnvironmentVariable(name='GZ_IP', value='127.0.0.1')

    # Set Gazebo Resource Path (merged with warehouse_world's paths)
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=resource_paths
    )

    # Launch World Simulation (Server)
    warehouse_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_warehouse_world, 'launch', 'warehouse_storage_launch.launch.py')
        )
    )

    # Launch Gazebo GUI Automatically using Nvidia GPU settings
    gz_gui_process = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        output='screen'
    )

    # Robot State Publisher
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

    # Parameter Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[
            {'config_file': bridge_file},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # Spawn Robot Node
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

    ld = LaunchDescription()

    # Apply GPU & Network Environment Variables
    ld.add_action(set_nv_prime)
    ld.add_action(set_glx_vendor)
    ld.add_action(set_egl_vendor)
    ld.add_action(set_gz_ip)


    ld.add_action(warehouse_launch)
    ld.add_action(set_gz_resource_path)
    ld.add_action(gz_gui_process)
    ld.add_action(robot_state_publisher)
    ld.add_action(bridge)
    ld.add_action(spawn_robot)

    return ld