from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    controlled_gazebo = PathJoinSubstitution(
        [
            FindPackageShare("aim_arm_description"),
            "launch",
            "controlled_gazebo.launch.py",
        ]
    )
    move_group = PathJoinSubstitution(
        [FindPackageShare("aim_arm_moveit_config"), "launch", "move_group.launch.py"]
    )

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(controlled_gazebo)
            ),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(move_group)),
        ]
    )
