#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="${REPO_ROOT}/colcon_ws"
PKG_ROOT="${WS_ROOT}/src/aim_arm_description"
CONTROL_PKG_ROOT="${WS_ROOT}/src/aim_arm_control"
RL_PKG_ROOT="${WS_ROOT}/src/aim_arm_rl"
PERCEPTION_PKG_ROOT="${WS_ROOT}/src/aim_arm_perception"
HARDWARE_PKG_ROOT="${WS_ROOT}/src/aim_arm_hardware"
BRINGUP_PKG_ROOT="${WS_ROOT}/src/aim_arm_bringup"
MOVEIT_PKG_ROOT="${WS_ROOT}/src/aim_arm_moveit_config"
GENERATED_URDF="$(mktemp)"
GENERATED_CONTROL_URDF="$(mktemp)"

cleanup() {
  rm -f "${GENERATED_URDF}" "${GENERATED_CONTROL_URDF}"
}
trap cleanup EXIT

set +u
source /opt/ros/humble/setup.bash
set -u

command -v ros2 >/dev/null
command -v colcon >/dev/null
command -v xacro >/dev/null

test -f "${PKG_ROOT}/package.xml"
test -f "${PKG_ROOT}/CMakeLists.txt"
test -f "${PKG_ROOT}/config/ros2_controllers.yaml"
test -f "${PKG_ROOT}/launch/controlled_gazebo.launch.py"
test -f "${PKG_ROOT}/launch/display.launch.py"
test -f "${PKG_ROOT}/launch/gazebo.launch.py"
test -f "${PKG_ROOT}/meshes/visual/upper_arm_visual.stl"
test -f "${PKG_ROOT}/meshes/visual/forearm_visual.stl"
test -f "${PKG_ROOT}/meshes/visual/wrist_visual.stl"
test -f "${PKG_ROOT}/meshes/visual/tool_visual.stl"
test -f "${PKG_ROOT}/urdf/aim_arm.urdf.xacro"
test -f "${PKG_ROOT}/worlds/aim_empty.world"
test -f "${CONTROL_PKG_ROOT}/package.xml"
test -f "${CONTROL_PKG_ROOT}/CMakeLists.txt"
test -f "${CONTROL_PKG_ROOT}/src/cartesian_target_node.cpp"
test -f "${RL_PKG_ROOT}/package.xml"
test -f "${RL_PKG_ROOT}/setup.py"
test -f "${RL_PKG_ROOT}/aim_arm_rl/env.py"
test -f "${PERCEPTION_PKG_ROOT}/package.xml"
test -f "${PERCEPTION_PKG_ROOT}/setup.py"
test -f "${PERCEPTION_PKG_ROOT}/aim_arm_perception/target_detector.py"
test -f "${PERCEPTION_PKG_ROOT}/aim_arm_perception/synthetic_camera_node.py"
test -f "${HARDWARE_PKG_ROOT}/package.xml"
test -f "${HARDWARE_PKG_ROOT}/src/serial_bridge_node.cpp"
test -f "${BRINGUP_PKG_ROOT}/package.xml"
test -f "${BRINGUP_PKG_ROOT}/launch/software_pipeline.launch.py"
test -f "${MOVEIT_PKG_ROOT}/package.xml"
test -f "${MOVEIT_PKG_ROOT}/config/aim_arm.srdf"
test -f "${MOVEIT_PKG_ROOT}/config/aim_arm.urdf.xacro"
test -f "${MOVEIT_PKG_ROOT}/config/moveit_controllers.yaml"
test -f "${MOVEIT_PKG_ROOT}/config/ompl_planning.yaml"
test -f "${MOVEIT_PKG_ROOT}/config/moveit.rviz"
test -f "${MOVEIT_PKG_ROOT}/launch/move_group.launch.py"
test -f "${MOVEIT_PKG_ROOT}/launch/moveit_rviz.launch.py"
test -f "${MOVEIT_PKG_ROOT}/launch/planning_simulation.launch.py"
test -f "${MOVEIT_PKG_ROOT}/src/plan_execution_smoke.cpp"

xacro "${PKG_ROOT}/urdf/aim_arm.urdf.xacro" > "${GENERATED_URDF}"
xacro "${PKG_ROOT}/urdf/aim_arm.urdf.xacro" \
  enable_ros2_control:=true \
  ros2_control_config:="${PKG_ROOT}/config/ros2_controllers.yaml" \
  > "${GENERATED_CONTROL_URDF}"

python3 -m py_compile \
  "${PKG_ROOT}/launch/controlled_gazebo.launch.py" \
  "${PKG_ROOT}/launch/display.launch.py" \
  "${PKG_ROOT}/launch/gazebo.launch.py" \
  "${BRINGUP_PKG_ROOT}/launch/software_pipeline.launch.py" \
  "${MOVEIT_PKG_ROOT}/launch/move_group.launch.py" \
  "${MOVEIT_PKG_ROOT}/launch/moveit_rviz.launch.py" \
  "${MOVEIT_PKG_ROOT}/launch/planning_simulation.launch.py"

python3 - "${MOVEIT_PKG_ROOT}/config/moveit_controllers.yaml" "${MOVEIT_PKG_ROOT}/config/ompl_planning.yaml" <<'PY'
import sys

import yaml

controllers = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
planning = yaml.safe_load(open(sys.argv[2], encoding="utf-8"))

manager = controllers.get("moveit_simple_controller_manager", {})
names = manager.get("controller_names", [])
if names != ["arm_controller"]:
    raise SystemExit("MoveIt controller list must contain arm_controller")
if len(manager["arm_controller"].get("joints", [])) != 6:
    raise SystemExit("MoveIt arm_controller must contain six joints")
if planning.get("planning_plugin") != "ompl_interface/OMPLPlanner":
    raise SystemExit("MoveIt OMPL planning plugin is not configured")
if "arm" not in planning:
    raise SystemExit("MoveIt OMPL configuration is missing the arm group")
print("MoveIt planning and controller YAML validation passed.")
PY

python3 - "${GENERATED_URDF}" "${GENERATED_CONTROL_URDF}" "${PKG_ROOT}/worlds/aim_empty.world" "${MOVEIT_PKG_ROOT}/config/aim_arm.srdf" <<'PY'
import sys
import xml.etree.ElementTree as ET

urdf_path = sys.argv[1]
control_urdf_path = sys.argv[2]
world_path = sys.argv[3]
srdf_path = sys.argv[4]

root = ET.parse(urdf_path).getroot()

if root.tag != "robot":
    raise SystemExit("Generated URDF root element is not <robot>")

links = root.findall("link")
joints = root.findall("joint")
revolute_joints = [joint for joint in joints if joint.attrib.get("type") == "revolute"]

if len(links) < 9:
    raise SystemExit(f"Expected at least 9 links, found {len(links)}")
if len(revolute_joints) != 6:
    raise SystemExit(f"Expected 6 revolute joints, found {len(revolute_joints)}")

required_joint_names = {
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_pitch_joint",
    "wrist_roll_joint",
    "wrist_yaw_joint",
}
actual_joint_names = {joint.attrib["name"] for joint in revolute_joints}
missing = sorted(required_joint_names - actual_joint_names)
if missing:
    raise SystemExit(f"Missing expected joints: {', '.join(missing)}")

for joint in revolute_joints:
    if joint.find("limit") is None:
        raise SystemExit(f"Joint {joint.attrib['name']} is missing limits")

mesh_visuals = root.findall(".//visual/geometry/mesh")
if len(mesh_visuals) < 5:
    raise SystemExit(f"Expected at least 5 visual meshes, found {len(mesh_visuals)}")

print(
    f"URDF validation passed: {len(links)} links, "
    f"{len(revolute_joints)} controlled joints, "
    f"{len(mesh_visuals)} visual meshes."
)

control_root = ET.parse(control_urdf_path).getroot()
ros2_control = control_root.find("ros2_control")
if ros2_control is None:
    raise SystemExit("Controller-enabled URDF is missing <ros2_control>")
control_joint_names = {
    joint.attrib["name"] for joint in ros2_control.findall("joint")
}
missing_control = sorted(required_joint_names - control_joint_names)
if missing_control:
    raise SystemExit(
        f"ros2_control is missing joints: {', '.join(missing_control)}"
    )
if control_root.find("gazebo/plugin") is None:
    raise SystemExit("Controller-enabled URDF is missing gazebo_ros2_control plugin")
print("Optional ros2_control XML validation passed.")

world_root = ET.parse(world_path).getroot()
if world_root.tag != "sdf":
    raise SystemExit("Gazebo world root element is not <sdf>")
if world_root.find("world") is None:
    raise SystemExit("Gazebo world does not contain a <world> element")
print("Gazebo world XML validation passed.")

srdf_root = ET.parse(srdf_path).getroot()
if srdf_root.tag != "robot":
    raise SystemExit("SRDF root element is not <robot>")
group = srdf_root.find("group[@name='arm']")
if group is None:
    raise SystemExit("SRDF is missing arm planning group")
chain = group.find("chain")
if chain is None or chain.attrib.get("base_link") != "base_link" or chain.attrib.get("tip_link") != "tool0":
    raise SystemExit("SRDF arm group chain is invalid")
print("MoveIt SRDF validation passed.")
PY

cd "${WS_ROOT}"
colcon build --symlink-install

set +u
source "${WS_ROOT}/install/setup.bash"
set -u

"${WS_ROOT}/install/aim_arm_control/lib/aim_arm_control/ik_smoke_test"
"${WS_ROOT}/install/aim_arm_hardware/lib/aim_arm_hardware/serial_packet_smoke_test"
ros2 run aim_arm_rl rl_smoke_test
ros2 run aim_arm_perception perception_smoke_test

echo "AIM-RL stack validation loop passed."
