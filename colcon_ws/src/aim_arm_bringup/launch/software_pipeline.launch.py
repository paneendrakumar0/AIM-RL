from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    image_topic = LaunchConfiguration("image_topic")
    dry_run = LaunchConfiguration("dry_run")
    serial_port = LaunchConfiguration("serial_port")

    xacro_file = PathJoinSubstitution(
        [FindPackageShare("aim_arm_description"), "urdf", "aim_arm.urdf.xacro"]
    )
    robot_description = {"robot_description": Command(["xacro ", xacro_file])}

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "image_topic",
                default_value="/camera/image_raw",
                description="Camera image topic used by the target tracker.",
            ),
            DeclareLaunchArgument(
                "dry_run",
                default_value="true",
                description="Keep serial bridge in dry-run mode unless hardware is attached.",
            ),
            DeclareLaunchArgument(
                "serial_port",
                default_value="/dev/ttyUSB0",
                description="Serial device path for the microcontroller.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
                output="screen",
            ),
            Node(
                package="aim_arm_perception",
                executable="target_tracker_node",
                parameters=[{"image_topic": image_topic}],
                output="screen",
            ),
            Node(
                package="aim_arm_control",
                executable="cartesian_target_node",
                output="screen",
            ),
            Node(
                package="aim_arm_hardware",
                executable="serial_bridge_node",
                parameters=[
                    {
                        "dry_run": dry_run,
                        "port": serial_port,
                    }
                ],
                output="screen",
            ),
        ]
    )

