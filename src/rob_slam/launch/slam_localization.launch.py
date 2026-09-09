import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution

from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState

from lifecycle_msgs.msg import Transition


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_lifecycle_manager = LaunchConfiguration('use_lifecycle_manager')
    slam_params_file = LaunchConfiguration('slam_params_file')
    autostart = LaunchConfiguration('autostart')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(
            get_package_share_directory('rob_slam'),
            'config',
            'slam_localization.yaml'
        ),
        description='Full path to the localization parameters file'
    )
    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically configure and activate slam_toolbox'
    )

    declare_use_lifecycle_manager = DeclareLaunchArgument(
        'use_lifecycle_manager',
        default_value='false',
        description='Use lifecycle manager'
    )

    start_slam_toolbox = LifecycleNode(
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        output='screen',
        parameters=[
            slam_params_file,
            {
                'use_sim_time': use_sim_time,
                'use_lifecycle_manager': use_lifecycle_manager
            }
        ]
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(start_slam_toolbox),
            transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(
            AndSubstitution(
                autostart,
                NotSubstitution(use_lifecycle_manager)
            )
        )
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=start_slam_toolbox,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                LogInfo(msg='[slam_toolbox] Activating localization node...'),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(start_slam_toolbox),
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        ),
        condition=IfCondition(
            AndSubstitution(
                autostart,
                NotSubstitution(use_lifecycle_manager)
            )
        )
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params_file,
        declare_autostart,
        declare_use_lifecycle_manager,
        start_slam_toolbox,
        configure_event,
        activate_event
    ])
