#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u

ros2 launch aim_arm_bringup software_pipeline.launch.py > /tmp/aim_rl_bringup.log 2>&1 &
launch_pid=$!

cleanup() {
  if kill -0 "${launch_pid}" >/dev/null 2>&1; then
    kill "${launch_pid}" >/dev/null 2>&1 || true
    wait "${launch_pid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

sleep 5

nodes="$(ros2 node list)"
echo "${nodes}"

for node in \
  /cartesian_target_node \
  /serial_bridge_node \
  /synthetic_camera_node \
  /target_tracker_node; do
  if ! grep -qx "${node}" <<< "${nodes}"; then
    echo "Missing expected node: ${node}" >&2
    echo "Launch log:" >&2
    sed -n '1,160p' /tmp/aim_rl_bringup.log >&2
    exit 1
  fi
done

echo "Bringup smoke test passed."

