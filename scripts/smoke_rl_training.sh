#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash -lc "source /opt/ros/humble/setup.bash && source '${REPO_ROOT}/colcon_ws/install/setup.bash' && ros2 run aim_arm_rl train_ppo"

test -f "${REPO_ROOT}/artifacts/checkpoints/ppo_initial.pt"
test -f "${REPO_ROOT}/artifacts/logs/ppo_smoke.csv"

echo "RL training smoke test passed."
