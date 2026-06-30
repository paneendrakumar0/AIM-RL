# Artifacts

Runtime outputs are intentionally kept out of Git.

Reserved local paths:

- `artifacts/checkpoints/`: PyTorch policy checkpoints.
- `artifacts/logs/`: training logs and metric exports.
- `artifacts/renders/`: screenshots or videos from simulation.

Current smoke outputs:

- `artifacts/checkpoints/ppo_initial.pt`
- `artifacts/logs/ppo_smoke.csv`
- `artifacts/logs/policy_eval.csv`
