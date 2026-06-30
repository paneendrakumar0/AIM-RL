#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="${REPO_ROOT}/colcon_ws"
PKG_ROOT="${WS_ROOT}/src/aim_arm_description"
GENERATED_URDF="$(mktemp)"

cleanup() {
  rm -f "${GENERATED_URDF}"
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
test -f "${PKG_ROOT}/urdf/aim_arm.urdf.xacro"

xacro "${PKG_ROOT}/urdf/aim_arm.urdf.xacro" > "${GENERATED_URDF}"

python3 - "${GENERATED_URDF}" <<'PY'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()

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
PY

cd "${WS_ROOT}"
colcon build --symlink-install

echo "Phase 1 validation loop passed."
