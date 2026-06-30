import numpy as np

from aim_arm_rl.env import MockArmReachEnv, compute_reward
from aim_arm_rl.ppo import PPOConfig, RolloutBuffer


def main() -> int:
    env = MockArmReachEnv()
    observation, info = env.reset()
    if observation.shape != (15,):
        raise RuntimeError(f"Unexpected observation shape: {observation.shape}")
    if info["distance"] <= 0.0:
        raise RuntimeError("Initial distance should be positive")

    reward = compute_reward(1.0, 0.8)
    if reward <= 0.0:
        raise RuntimeError("Closing distance should create positive reward")

    crash_reward = compute_reward(0.5, 0.5, crashed=True)
    if crash_reward >= -49.0:
        raise RuntimeError("Crash penalty is too small")

    action = np.array([0.1, -0.1, 0.2, -0.1, 0.0, 0.0], dtype=np.float32)
    next_observation, _, terminated, truncated, step_info = env.step(action)
    if next_observation.shape != (15,):
        raise RuntimeError("Step returned invalid observation")
    if "distance" not in step_info:
        raise RuntimeError("Step info is missing distance")
    if terminated and truncated:
        raise RuntimeError("Environment cannot terminate and truncate on first step")

    config = PPOConfig(rollout_steps=4, minibatch_size=2)
    buffer = RolloutBuffer(config)
    buffer.add(observation, np.zeros(6, dtype=np.float32), 1.0, False, 0.5, -0.1)
    buffer.add(next_observation, action, 0.5, True, 0.2, -0.2)
    advantages = buffer.compute_advantages()
    if advantages.shape != (2,):
        raise RuntimeError("Rollout advantages have invalid shape")

    print(
        "RL smoke test passed: "
        f"initial_distance={info['distance']:.3f}, "
        f"next_distance={step_info['distance']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
