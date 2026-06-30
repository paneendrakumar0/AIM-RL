#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source /opt/ros/humble/setup.bash
source "${REPO_ROOT}/colcon_ws/install/setup.bash"
set -u
export ROS_DOMAIN_ID=$((100 + $$ % 100))
export GAZEBO_MASTER_URI="http://127.0.0.1:$((14000 + $$ % 1000))"

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start >/dev/null 2>&1 || true

ros2 launch aim_arm_description controlled_gazebo.launch.py > /tmp/aim_rl_controlled_trajectory.log 2>&1 &
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

ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  joint_names: [
    shoulder_pan_joint,
    shoulder_lift_joint,
    elbow_joint,
    wrist_pitch_joint,
    wrist_roll_joint,
    wrist_yaw_joint
  ],
  points: [
    {
      positions: [0.0, -0.6, 1.2, -0.6, 0.0, 0.0],
      time_from_start: {sec: 2, nanosec: 0}
    }
  ]
}" >/tmp/aim_rl_trajectory_pub.log 2>&1

joint_state="$(timeout 8 ros2 topic echo --once /joint_states)"
echo "${joint_state}" | sed -n '1,120p'

for joint in \
  shoulder_pan_joint \
  shoulder_lift_joint \
  elbow_joint \
  wrist_pitch_joint \
  wrist_roll_joint \
  wrist_yaw_joint; do
  if ! grep -q "${joint}" <<< "${joint_state}"; then
    echo "Joint state missing joint: ${joint}" >&2
    sed -n '1,260p' /tmp/aim_rl_controlled_trajectory.log >&2
    exit 1
  fi
done

echo "Controlled trajectory smoke test passed."

