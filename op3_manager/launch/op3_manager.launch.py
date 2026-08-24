import launch
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os

def generate_launch_description():
    # Auto-detect simulation: if /dev/ttyUSB0 doesn't exist, assume simulation
    gazebo_default = 'false'
    if not os.path.exists('/dev/ttyUSB0'):
        gazebo_default = 'true'

    gazebo_robot_name_default = 'robotis_op3'
    offset_file_path_default = get_package_share_directory('op3_manager') + '/config/offset.yaml'
    robot_file_path_default = get_package_share_directory('op3_manager') + '/config/OP3.robot'
    init_file_path_default = get_package_share_directory('op3_manager') + '/config/dxl_init_OP3.yaml'
    device_name_default = '/dev/ttyUSB0'

    # ZMP Launch integration
    zmp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('zmp'), 'launch', 'zmp.launch.py')
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'simulation',
            default_value=gazebo_default,
            description='Whether to run in simulation mode'
        ),
        DeclareLaunchArgument(
            'device_name',
            default_value=device_name_default,
            description='Device name for the port'
        ),
        Node(
            package='op3_manager',
            executable='op3_manager',
            # name='op3_manager',
            output='screen',
            parameters=[{
                'angle_unit': 30.0,
                'simulation': LaunchConfiguration('simulation'),
                'simulation_robot_name': gazebo_robot_name_default,
                'offset_file_path': offset_file_path_default,
                'robot_file_path': robot_file_path_default,
                'init_file_path': init_file_path_default,
                'device_name': LaunchConfiguration('device_name')
            }]
        ),
        zmp_launch
    ])
