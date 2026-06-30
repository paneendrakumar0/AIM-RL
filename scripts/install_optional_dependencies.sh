#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y \
  ros-humble-controller-manager \
  ros-humble-gazebo-ros2-control \
  ros-humble-joint-state-broadcaster \
  ros-humble-joint-trajectory-controller \
  ros-humble-moveit \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers

"$(dirname "${BASH_SOURCE[0]}")/install_rl_cpu_dependencies.sh"

echo "Optional dependencies installed. Re-run ./scripts/audit_dependencies.sh"
