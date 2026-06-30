#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u
export ROS_DOMAIN_ID=$((100 + $$ % 100))
export GAZEBO_MASTER_URI="http://127.0.0.1:$((13000 + $$ % 1000))"

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start >/dev/null 2>&1 || true

ros2 launch aim_arm_description controlled_gazebo.launch.py > /tmp/aim_rl_controlled_gazebo.log 2>&1 &
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

sleep 12

nodes="$(ros2 node list || true)"
echo "${nodes}"

if ! grep -qx "/controller_manager" <<< "${nodes}"; then
  echo "controller_manager did not start" >&2
  sed -n '1,240p' /tmp/aim_rl_controlled_gazebo.log >&2
  exit 1
fi

controllers="$(ros2 control list_controllers || true)"
echo "${controllers}"

for controller in joint_state_broadcaster arm_controller; do
  if ! grep -q "${controller}" <<< "${controllers}"; then
    echo "Missing expected controller: ${controller}" >&2
    sed -n '1,260p' /tmp/aim_rl_controlled_gazebo.log >&2
    exit 1
  fi
done

echo "Controlled Gazebo smoke test passed."
