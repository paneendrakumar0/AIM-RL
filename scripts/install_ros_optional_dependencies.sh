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
  python3-opencv \
  ros-humble-controller-manager \
  ros-humble-cv-bridge \
  ros-humble-gazebo-ros2-control \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-joint-state-broadcaster \
  ros-humble-joint-trajectory-controller \
  ros-humble-moveit \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-xacro

echo "ROS optional dependencies installed."
