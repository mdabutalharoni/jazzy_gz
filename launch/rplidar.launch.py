from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-port0',
            description='Serial port for the RPLidar'
        ),
        DeclareLaunchArgument(
            'serial_baudrate',
            default_value='256000',
            description='Baud rate for the RPLidar'
        ),
        DeclareLaunchArgument(
            'scan_mode',
            default_value='Standard',
            description='Scan mode for the RPLidar'
        ),
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': LaunchConfiguration('serial_port'),
                'serial_baudrate': LaunchConfiguration('serial_baudrate'),
                'frame_id': 'laser_frame',
                'angle_compensate': True,
                'scan_mode': LaunchConfiguration('scan_mode'),
            }]
        )
    ])