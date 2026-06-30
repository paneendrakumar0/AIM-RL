#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="${REPO_ROOT}/artifacts/logs/dependency_audit.txt"

mkdir -p "$(dirname "${REPORT_PATH}")"
"${REPO_ROOT}/scripts/audit_dependencies.sh" | tee "${REPORT_PATH}"

echo "Dependency report written: ${REPORT_PATH}"

