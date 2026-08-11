#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u
export ROS_DOMAIN_ID=$((100 + $$ % 100))

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start >/dev/null 2>&1 || true

ros2 launch aim_arm_moveit_config move_group.launch.py > /tmp/aim_rl_move_group.log 2>&1 &
launch_pid=$!

cleanup() {
  if kill -0 "${launch_pid}" >/dev/null 2>&1; then
    kill "${launch_pid}" >/dev/null 2>&1 || true
    wait "${launch_pid}" >/dev/null 2>&1 || true
  fi
  ros2 daemon stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 8

nodes="$(ros2 node list || true)"
echo "${nodes}"

if ! grep -qx "/move_group" <<< "${nodes}"; then
  echo "MoveIt move_group did not start" >&2
  sed -n '1,240p' /tmp/aim_rl_move_group.log >&2
  exit 1
fi

echo "MoveIt planning smoke test passed."
