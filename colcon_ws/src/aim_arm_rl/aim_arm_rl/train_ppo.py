from aim_arm_rl.env import MockArmReachEnv
from aim_arm_rl.ppo import (
    PPOConfig,
    TorchUnavailableError,
    build_actor_critic,
    ppo_update_smoke,
    save_checkpoint,
)


def main() -> int:
    config = PPOConfig()
    env = MockArmReachEnv()
    observation, info = env.reset()
    del observation, info

    try:
        model = build_actor_critic(config)
    except TorchUnavailableError as exc:
        print(exc)
        return 2

    device = next(model.parameters()).device
    print(
        "PPO trainer initialized: "
        f"observation_dim={config.observation_dim}, "
        f"action_dim={config.action_dim}, "
        f"device={device}"
    )
    save_checkpoint(model, "artifacts/checkpoints/ppo_initial.pt", config)
    print("Saved initial checkpoint: artifacts/checkpoints/ppo_initial.pt")
    loss = ppo_update_smoke(config)
    print(f"PPO update smoke loss={loss:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
