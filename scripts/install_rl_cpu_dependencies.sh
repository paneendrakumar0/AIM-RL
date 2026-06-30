#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --user --timeout 1000 -r requirements-rl-cpu.txt
python3 -m pip install --user --timeout 1000 \
  --index-url https://download.pytorch.org/whl/cpu \
  "torch==2.3.1+cpu"

python3 - <<'PY'
import gymnasium
import torch

print(f"gymnasium={gymnasium.__version__}")
print(f"torch={torch.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
PY
