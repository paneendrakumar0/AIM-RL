#!/usr/bin/env bash
set -euo pipefail

if ! sudo -v; then
  cat >&2 <<'EOF'
sudo authentication failed.

Run this script from a normal terminal where you can enter your sudo password:

  ./scripts/install_optional_dependencies.sh

Or install only Python RL dependencies without sudo:

  ./scripts/install_rl_cpu_dependencies.sh
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

"$(dirname "${BASH_SOURCE[0]}")/install_rl_cpu_dependencies.sh"

echo "Optional dependencies installed. Re-run ./scripts/audit_dependencies.sh"
