# Contributing

## Local Checks

Before opening a pull request or pushing a change, run:

```bash
./scripts/run_all_checks.sh
```

For smaller loops:

```bash
./scripts/validate_stack.sh
./scripts/smoke_topic_flow.sh
```

## Development Rules

- Keep commits focused and validate before pushing.
- Do not commit generated build outputs from `colcon_ws/build`, `colcon_ws/install`, or `colcon_ws/log`.
- Keep runtime artifacts in `artifacts/`; they are intentionally ignored.
- When adding a ROS package, wire it into `scripts/validate_stack.sh`.
- When changing media, regenerate it with `./scripts/generate_readme_media.py`.

## Dependency Gates

The base stack validates without optional MoveIt, `gazebo_ros2_control`, Gymnasium, or PyTorch packages. Changes that require optional dependencies should keep a graceful fallback or document the gate clearly.

