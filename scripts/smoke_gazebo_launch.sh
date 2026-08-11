#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u
export ROS_DOMAIN_ID=$((100 + $$ % 100))
export GAZEBO_MASTER_URI="http://127.0.0.1:$((12000 + $$ % 1000))"

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start >/dev/null 2>&1 || true

ros2 launch aim_arm_description gazebo.launch.py > /tmp/aim_rl_gazebo.log 2>&1 &
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

sleep 8

nodes="$(ros2 node list || true)"
echo "${nodes}"

if ! grep -qx "/robot_state_publisher" <<< "${nodes}"; then
  echo "robot_state_publisher did not start" >&2
  sed -n '1,200p' /tmp/aim_rl_gazebo.log >&2
  exit 1
fi

if ! grep -qx "/gazebo" <<< "${nodes}"; then
  echo "gazebo ROS node did not start" >&2
  sed -n '1,200p' /tmp/aim_rl_gazebo.log >&2
  exit 1
fi

if [[ -n "${CAPTURE_IMAGE_PATH:-}" ]]; then
  python3 "${REPO_ROOT}/scripts/capture_ros_image.py" \
    --topic "${CAPTURE_IMAGE_TOPIC:-/camera/image_raw}" \
    --output "${CAPTURE_IMAGE_PATH}"
fi

echo "Gazebo launch smoke test passed."
