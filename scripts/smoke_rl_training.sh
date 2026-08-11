#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash -lc "source /opt/ros/humble/setup.bash && source '${REPO_ROOT}/colcon_ws/install/setup.bash' && ros2 run aim_arm_rl train_ppo --updates 1 --rollout-steps 64 --minibatch-size 32 --update-epochs 2 --device cpu"
bash -lc "source /opt/ros/humble/setup.bash && source '${REPO_ROOT}/colcon_ws/install/setup.bash' && ros2 run aim_arm_rl evaluate_policy --episodes 1"

test -f "${REPO_ROOT}/artifacts/checkpoints/ppo_latest.pt"
test -f "${REPO_ROOT}/artifacts/logs/ppo_training.csv"
test -f "${REPO_ROOT}/artifacts/logs/policy_eval.csv"

echo "RL training smoke test passed."
