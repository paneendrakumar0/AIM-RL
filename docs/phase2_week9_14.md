# Phase 2, Weeks 9-14: Reward and PPO Training Skeleton

## Implemented

- PPO configuration dataclass.
- Rollout buffer with Generalized Advantage Estimation.
- PyTorch actor-critic factory with CUDA preference and CPU fallback.
- `train_ppo` console entry point that initializes the trainer once PyTorch is installed.
- Minimal PPO optimizer-step smoke test.
- Smoke-test coverage for reward direction, crash penalty, environment step shape, and advantage calculation.

## Current Dependency Gate

PyTorch is not installed on this machine yet, so `train_ppo` exits with a clear message until:

```bash
python3 -m pip install -r requirements-rl.txt
```

After installation:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 run aim_arm_rl train_ppo
```

## Next Training Work

- Add a full PPO update loop.
- Add checkpoint saving/loading.
- Replace the mock environment backend with the Gazebo/ROS stepping backend once controllers are live.
- Add TensorBoard or CSV metrics for reward and success-rate curves.
