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

ros2 launch aim_arm_bringup software_pipeline.launch.py > /tmp/aim_rl_topic_flow.log 2>&1 &
launch_pid=$!

cleanup() {
  if kill -0 "${launch_pid}" >/dev/null 2>&1; then
    kill "${launch_pid}" >/dev/null 2>&1 || true
    wait "${launch_pid}" >/dev/null 2>&1 || true
  fi
  ros2 daemon stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 5

target_msg="$(timeout 8 ros2 topic echo --once /aim_arm/target_pose)"
trajectory_msg="$(timeout 8 ros2 topic echo --once /arm_controller/joint_trajectory)"

echo "${target_msg}" | sed -n '1,80p'
echo "${trajectory_msg}" | sed -n '1,80p'

if ! grep -q "frame_id: world" <<< "${target_msg}"; then
  echo "Target pose did not publish in world frame" >&2
  exit 1
fi

for joint in \
  shoulder_pan_joint \
  shoulder_lift_joint \
  elbow_joint \
  wrist_pitch_joint \
  wrist_roll_joint \
  wrist_yaw_joint; do
  if ! grep -q "${joint}" <<< "${trajectory_msg}"; then
    echo "Trajectory missing joint: ${joint}" >&2
    exit 1
  fi
done

echo "Topic-flow smoke test passed."
