#!/usr/bin/env bash
set -euo pipefail

if ! sudo -v; then
  cat >&2 <<'EOF'
sudo authentication failed.
Run from a terminal where sudo can prompt for your password.
EOF
  exit 1
fi

sudo apt update
sudo apt install -y \
  ros-humble-controller-manager \
  ros-humble-gazebo-ros2-control \
  ros-humble-joint-state-broadcaster \
  ros-humble-joint-trajectory-controller \
  ros-humble-moveit \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers

echo "ROS optional dependencies installed."
