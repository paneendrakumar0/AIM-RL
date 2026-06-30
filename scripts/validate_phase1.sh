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
test -f "${PKG_ROOT}/launch/display.launch.py"
test -f "${PKG_ROOT}/launch/gazebo.launch.py"
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
test -f "${HARDWARE_PKG_ROOT}/package.xml"
test -f "${HARDWARE_PKG_ROOT}/src/serial_bridge_node.cpp"
test -f "${BRINGUP_PKG_ROOT}/package.xml"
test -f "${BRINGUP_PKG_ROOT}/launch/software_pipeline.launch.py"

xacro "${PKG_ROOT}/urdf/aim_arm.urdf.xacro" > "${GENERATED_URDF}"
xacro "${PKG_ROOT}/urdf/aim_arm.urdf.xacro" \
  enable_ros2_control:=true \
  ros2_control_config:="${PKG_ROOT}/config/ros2_controllers.yaml" \
  > "${GENERATED_CONTROL_URDF}"

python3 -m py_compile \
  "${PKG_ROOT}/launch/display.launch.py" \
  "${PKG_ROOT}/launch/gazebo.launch.py" \
  "${BRINGUP_PKG_ROOT}/launch/software_pipeline.launch.py"

python3 - "${GENERATED_URDF}" "${GENERATED_CONTROL_URDF}" "${PKG_ROOT}/worlds/aim_empty.world" <<'PY'
import sys
import xml.etree.ElementTree as ET

urdf_path = sys.argv[1]
control_urdf_path = sys.argv[2]
world_path = sys.argv[3]

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

print(
    f"URDF validation passed: {len(links)} links, "
    f"{len(revolute_joints)} controlled joints."
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

echo "Phase 1 validation loop passed."
