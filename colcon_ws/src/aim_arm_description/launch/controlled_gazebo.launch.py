from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_share = FindPackageShare("aim_arm_description")
    xacro_file = PathJoinSubstitution(
        [package_share, "urdf", "aim_arm.urdf.xacro"]
    )
    controller_config = PathJoinSubstitution(
        [package_share, "config", "ros2_controllers.yaml"]
    )
    world_file = PathJoinSubstitution(
        [package_share, "worlds", "aim_empty.world"]
    )
    gazebo_launch = PathJoinSubstitution(
        [FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"]
    )

    robot_description = {
        "robot_description": Command(
            [
                "xacro ",
                xacro_file,
                " enable_ros2_control:=true",
                " ros2_control_config:=",
                controller_config,
            ]
        )
    }

    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic",
            "robot_description",
            "-entity",
            "aim_arm",
            "-x",
            "0",
            "-y",
            "0",
            "-z",
            "0.05",
        ],
        output="screen",
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
        output="screen",
    )

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gazebo_launch),
                launch_arguments={"world": world_file}.items(),
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
                output="screen",
            ),
            spawn_robot,
            RegisterEventHandler(
                OnProcessExit(
                    target_action=spawn_robot,
                    on_exit=[joint_state_broadcaster, arm_controller],
                )
            ),
        ]
    )

