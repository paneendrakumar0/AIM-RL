import argparse
from dataclasses import replace

from aim_arm_rl.env import MockArmReachEnv
from aim_arm_rl.metrics import append_metrics
from aim_arm_rl.ppo import (
    PPOConfig,
    RolloutBuffer,
    TorchUnavailableError,
    build_actor_critic,
    collect_rollout,
    ppo_update,
    require_torch,
    save_checkpoint,
    seed_everything,
)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Train PPO on the AIM arm mock backend.")
    parser.add_argument("--updates", type=int, default=4)
    parser.add_argument("--rollout-steps", type=int, default=256)
    parser.add_argument("--minibatch-size", type=int, default=64)
    parser.add_argument("--update-epochs", type=int, default=4)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument(
        "--checkpoint", default="artifacts/checkpoints/ppo_latest.pt"
    )
    parser.add_argument("--metrics", default="artifacts/logs/ppo_training.csv")
    return parser.parse_args(args)


def main(args=None) -> int:
    options = parse_args(args)
    config = replace(
        PPOConfig(),
        rollout_steps=options.rollout_steps,
        minibatch_size=options.minibatch_size,
        update_epochs=options.update_epochs,
        device=options.device,
    )
    if options.updates < 1:
        raise ValueError("--updates must be at least 1")
    if config.minibatch_size < 1 or config.rollout_steps < 1:
        raise ValueError("Rollout and minibatch sizes must be positive")

    env = MockArmReachEnv()

    try:
        torch = require_torch()
        seed_everything(config.seed)
        model = build_actor_critic(config)
    except TorchUnavailableError as exc:
        print(exc)
        return 2

    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    buffer = RolloutBuffer(config)
    device = next(model.parameters()).device
    print(
        "PPO training started: "
        f"observation_dim={config.observation_dim}, "
        f"action_dim={config.action_dim}, "
        f"device={device}"
    )

    for update in range(1, options.updates + 1):
        _, last_value, rollout_metrics = collect_rollout(env, model, buffer, config)
        update_metrics = ppo_update(
            model, optimizer, buffer, config, last_value=last_value
        )
        row = {
            "update": update,
            "mean_episode_reward": f"{rollout_metrics['mean_episode_reward']:.6f}",
            "episodes": int(rollout_metrics["episodes"]),
            "successes": int(rollout_metrics["successes"]),
            "policy_loss": f"{update_metrics['policy_loss']:.6f}",
            "value_loss": f"{update_metrics['value_loss']:.6f}",
            "entropy": f"{update_metrics['entropy']:.6f}",
        }
        append_metrics(options.metrics, row)
        print(
            f"update={update}/{options.updates} "
            f"reward={rollout_metrics['mean_episode_reward']:.3f} "
            f"policy_loss={update_metrics['policy_loss']:.4f} "
            f"value_loss={update_metrics['value_loss']:.4f}"
        )

    save_checkpoint(
        model,
        options.checkpoint,
        config,
        optimizer=optimizer,
        update=options.updates,
    )
    print(f"Saved trained checkpoint: {options.checkpoint}")
    print(f"Saved training metrics: {options.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
