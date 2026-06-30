#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${REPO_ROOT}/scripts/validate_stack.sh"
"${REPO_ROOT}/scripts/write_dependency_report.sh"
"${REPO_ROOT}/scripts/smoke_gazebo_launch.sh"
if ros2 pkg prefix controller_manager >/dev/null 2>&1 && \
  ros2 pkg prefix gazebo_ros2_control >/dev/null 2>&1; then
  "${REPO_ROOT}/scripts/smoke_controlled_gazebo.sh"
else
  echo "Skipping controlled Gazebo smoke test; ros2_control packages not installed."
fi
"${REPO_ROOT}/scripts/smoke_bringup.sh"
"${REPO_ROOT}/scripts/smoke_topic_flow.sh"

if python3 -c "import torch, gymnasium" >/dev/null 2>&1; then
  "${REPO_ROOT}/scripts/smoke_rl_training.sh"
else
  echo "Skipping RL training smoke test; torch/gymnasium not installed."
fi

echo "All AIM-RL checks passed."
