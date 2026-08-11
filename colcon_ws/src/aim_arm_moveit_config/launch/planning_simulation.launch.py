from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
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
    moveit_rviz = PathJoinSubstitution(
        [FindPackageShare("aim_arm_moveit_config"), "launch", "moveit_rviz.launch.py"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Start RViz with the MoveIt MotionPlanning display.",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(controlled_gazebo)
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(move_group),
                launch_arguments={"use_sim_time": "true"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(moveit_rviz),
                condition=IfCondition(LaunchConfiguration("use_rviz")),
            ),
        ]
    )
