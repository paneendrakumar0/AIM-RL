# Phase 2, Weeks 9-14: Reward and PPO Training Skeleton

## Implemented

- PPO configuration dataclass.
- Rollout buffer with Generalized Advantage Estimation.
- PyTorch actor-critic factory with CUDA preference and CPU fallback.
- `train_ppo` console entry point with rollout collection and clipped PPO minibatch updates.
- Configurable update, rollout, minibatch, epoch, and device settings.
- Trained checkpoint saving with model, optimizer, configuration, and update state.
- CSV metrics for reward, success count, policy loss, value loss, and entropy.
- Checkpoint-based policy evaluation against `MockArmReachEnv`.
- Deterministic Torch/NumPy seeding for repeatable smoke metrics.
- Smoke-test coverage for reward direction, crash penalty, environment step shape, and advantage calculation.

## Current Dependency Gate

`train_ppo` exits with a clear message when PyTorch is unavailable. Install the RL dependencies with:

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

- Replace the mock environment backend with the Gazebo/ROS stepping backend once controllers are live.
- Add TensorBoard visualization for reward and success-rate curves.
