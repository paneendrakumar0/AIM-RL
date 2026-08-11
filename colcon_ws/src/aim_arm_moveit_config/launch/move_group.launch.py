from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("aim_arm", package_name="aim_arm_moveit_config")
        .robot_description(file_path="config/aim_arm.urdf.xacro")
        .robot_description_semantic(file_path="config/aim_arm.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )
    generated_launch = generate_move_group_launch(moveit_config)
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use the Gazebo simulation clock.",
            ),
            SetParameter(
                name="use_sim_time",
                value=LaunchConfiguration("use_sim_time"),
            ),
            *generated_launch.entities,
        ]
    )
