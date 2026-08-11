from __future__ import annotations

import argparse

import numpy as np

from aim_arm_rl.env import MockArmReachEnv
from aim_arm_rl.metrics import append_metrics
from aim_arm_rl.ppo import (
    PPOConfig,
    TorchUnavailableError,
    load_checkpoint,
    require_torch,
    seed_everything,
)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Evaluate an AIM arm PPO checkpoint.")
    parser.add_argument(
        "--checkpoint", default="artifacts/checkpoints/ppo_latest.pt"
    )
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--metrics", default="artifacts/logs/policy_eval.csv")
    return parser.parse_args(args)


def main(args=None) -> int:
    options = parse_args(args)
    if options.episodes < 1:
        raise ValueError("--episodes must be at least 1")
    config = PPOConfig()
    env = MockArmReachEnv(max_steps=32)

    try:
        torch = require_torch()
        seed_everything(config.seed)
        model = load_checkpoint(options.checkpoint)
    except (FileNotFoundError, TorchUnavailableError) as exc:
        print(exc)
        return 2

    rewards = []
    distances = []
    successes = 0
    total_steps = 0
    for _ in range(options.episodes):
        observation, _ = env.reset()
        total_reward = 0.0
        terminated = False
        truncated = False
        info = {}
        while not (terminated or truncated):
            with torch.no_grad():
                tensor = torch.as_tensor(
                    observation,
                    dtype=torch.float32,
                    device=next(model.parameters()).device,
                ).unsqueeze(0)
                mean, _, _ = model(tensor)
                action = mean.squeeze(0).cpu().numpy()
            action = np.tanh(action).astype(np.float32)
            observation, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            total_steps += 1
        rewards.append(total_reward)
        distances.append(float(info["distance"]))
        successes += int(bool(info.get("touched", False)))

    append_metrics(
        options.metrics,
        {
            "checkpoint": options.checkpoint,
            "episodes": options.episodes,
            "mean_reward": f"{np.mean(rewards):.6f}",
            "mean_final_distance": f"{np.mean(distances):.6f}",
            "success_rate": f"{successes / options.episodes:.6f}",
            "total_steps": total_steps,
        },
    )
    print(
        "Policy evaluation passed: "
        f"episodes={options.episodes}, mean_reward={np.mean(rewards):.3f}, "
        f"mean_final_distance={np.mean(distances):.3f}, "
        f"success_rate={successes / options.episodes:.1%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
