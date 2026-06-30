from __future__ import annotations

import numpy as np

from aim_arm_rl.env import MockArmReachEnv
from aim_arm_rl.metrics import append_metrics
from aim_arm_rl.ppo import (
    PPOConfig,
    TorchUnavailableError,
    build_actor_critic,
    require_torch,
    seed_everything,
)


def main() -> int:
    config = PPOConfig()
    env = MockArmReachEnv(max_steps=32)

    try:
        torch = require_torch()
        seed_everything(config.seed)
        model = build_actor_critic(config)
    except TorchUnavailableError as exc:
        print(exc)
        return 2

    observation, _ = env.reset()
    total_reward = 0.0
    terminated = False
    truncated = False
    steps = 0

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
        steps += 1

    append_metrics(
        "artifacts/logs/policy_eval.csv",
        {
            "steps": steps,
            "total_reward": f"{total_reward:.6f}",
            "final_distance": f"{info['distance']:.6f}",
            "terminated": terminated,
            "truncated": truncated,
        },
    )
    print(
        "Policy evaluation smoke passed: "
        f"steps={steps}, total_reward={total_reward:.3f}, "
        f"final_distance={info['distance']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
