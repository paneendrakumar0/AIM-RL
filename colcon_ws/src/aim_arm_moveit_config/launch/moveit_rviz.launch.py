from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_moveit_rviz_launch


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("aim_arm", package_name="aim_arm_moveit_config")
        .robot_description(file_path="config/aim_arm.urdf.xacro")
        .robot_description_semantic(file_path="config/aim_arm.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )
    return generate_moveit_rviz_launch(moveit_config)
