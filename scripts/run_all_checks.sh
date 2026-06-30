#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${REPO_ROOT}/scripts/validate_stack.sh"
"${REPO_ROOT}/scripts/audit_dependencies.sh"
"${REPO_ROOT}/scripts/smoke_gazebo_launch.sh"
"${REPO_ROOT}/scripts/smoke_bringup.sh"
"${REPO_ROOT}/scripts/smoke_topic_flow.sh"

echo "All AIM-RL checks passed."
