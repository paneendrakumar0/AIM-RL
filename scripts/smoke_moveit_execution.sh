#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u
export ROS_DOMAIN_ID=$((100 + $$ % 100))
export GAZEBO_MASTER_URI="http://127.0.0.1:$((15000 + $$ % 1000))"

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start >/dev/null 2>&1 || true

ros2 launch aim_arm_moveit_config planning_simulation.launch.py use_rviz:=false \
  > /tmp/aim_rl_moveit_execution.log 2>&1 &
launch_pid=$!

cleanup() {
  if kill -0 "${launch_pid}" >/dev/null 2>&1; then
    kill "${launch_pid}" >/dev/null 2>&1 || true
    wait "${launch_pid}" >/dev/null 2>&1 || true
  fi
  ros2 daemon stop >/dev/null 2>&1 || true
  sleep 2
}
trap cleanup EXIT

sleep 15

nodes="$(ros2 node list || true)"
controllers="$(ros2 control list_controllers || true)"
echo "${nodes}"
echo "${controllers}"

if ! grep -qx "/move_group" <<< "${nodes}"; then
  echo "MoveIt move_group did not start" >&2
  sed -n '1,280p' /tmp/aim_rl_moveit_execution.log >&2
  exit 1
fi
if ! grep -q "arm_controller.*active" <<< "${controllers}"; then
  echo "arm_controller is not active" >&2
  sed -n '1,280p' /tmp/aim_rl_moveit_execution.log >&2
  exit 1
fi

if ! ros2 run aim_arm_moveit_config plan_execution_smoke; then
  sed -n '1,320p' /tmp/aim_rl_moveit_execution.log >&2
  exit 1
fi

if [[ -n "${CAPTURE_IMAGE_PATH:-}" ]]; then
  capture_topic="${CAPTURE_IMAGE_TOPIC:-/camera/image_raw}"
  if ! python3 "${REPO_ROOT}/scripts/capture_ros_image.py" \
    --topic "${capture_topic}" \
    --output "${CAPTURE_IMAGE_PATH}"; then
    echo "Available ROS topics:" >&2
    ros2 topic list >&2 || true
    ros2 topic info --verbose "${capture_topic}" >&2 || true
    echo "Available Gazebo topics:" >&2
    gz topic -l >&2 || true
    sed -n '1,360p' /tmp/aim_rl_moveit_execution.log >&2
    exit 1
  fi
fi

echo "MoveIt plan-execution smoke test passed."
