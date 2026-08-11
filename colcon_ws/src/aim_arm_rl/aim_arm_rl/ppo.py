from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np


class TorchUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class PPOConfig:
    observation_dim: int = 15
    action_dim: int = 6
    hidden_dim: int = 128
    learning_rate: float = 3.0e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    entropy_coef: float = 0.01
    value_coef: float = 0.5
    max_grad_norm: float = 0.5
    rollout_steps: int = 2048
    minibatch_size: int = 256
    update_epochs: int = 10
    device: str = "cuda"
    seed: int = 7


class RolloutBuffer:
    def __init__(self, config: PPOConfig) -> None:
        self.config = config
        self.observations = np.zeros(
            (config.rollout_steps, config.observation_dim), dtype=np.float32
        )
        self.actions = np.zeros((config.rollout_steps, config.action_dim), dtype=np.float32)
        self.rewards = np.zeros(config.rollout_steps, dtype=np.float32)
        self.dones = np.zeros(config.rollout_steps, dtype=np.float32)
        self.values = np.zeros(config.rollout_steps, dtype=np.float32)
        self.log_probs = np.zeros(config.rollout_steps, dtype=np.float32)
        self.index = 0

    def reset(self) -> None:
        self.index = 0

    def add(
        self,
        observation: np.ndarray,
        action: np.ndarray,
        reward: float,
        done: bool,
        value: float,
        log_prob: float,
    ) -> None:
        if self.index >= self.config.rollout_steps:
            raise IndexError("RolloutBuffer is full")
        self.observations[self.index] = observation
        self.actions[self.index] = action
        self.rewards[self.index] = reward
        self.dones[self.index] = float(done)
        self.values[self.index] = value
        self.log_probs[self.index] = log_prob
        self.index += 1

    def compute_advantages(self, last_value: float = 0.0) -> np.ndarray:
        advantages = np.zeros_like(self.rewards)
        gae = 0.0
        for step in reversed(range(self.index)):
            next_value = last_value if step == self.index - 1 else self.values[step + 1]
            non_terminal = 1.0 - self.dones[step]
            delta = (
                self.rewards[step]
                + self.config.gamma * next_value * non_terminal
                - self.values[step]
            )
            gae = delta + self.config.gamma * self.config.gae_lambda * non_terminal * gae
            advantages[step] = gae
        return advantages[: self.index]

    def returns_and_advantages(
        self, last_value: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        advantages = self.compute_advantages(last_value)
        returns = advantages + self.values[: self.index]
        return returns, advantages


def require_torch():
    try:
        import torch
    except ModuleNotFoundError as exc:
        raise TorchUnavailableError(
            "PyTorch is not installed. Install requirements-rl.txt before training."
        ) from exc
    return torch


def seed_everything(seed: int) -> None:
    np.random.seed(seed)
    torch = require_torch()
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_actor_critic(config: Optional[PPOConfig] = None):
    config = config or PPOConfig()
    torch = require_torch()
    seed_everything(config.seed)
    nn = torch.nn

    class ActorCritic(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.shared = nn.Sequential(
                nn.Linear(config.observation_dim, config.hidden_dim),
                nn.Tanh(),
                nn.Linear(config.hidden_dim, config.hidden_dim),
                nn.Tanh(),
            )
            self.actor_mean = nn.Linear(config.hidden_dim, config.action_dim)
            self.actor_log_std = nn.Parameter(torch.zeros(config.action_dim))
            self.critic = nn.Linear(config.hidden_dim, 1)

        def forward(self, observations):
            features = self.shared(observations)
            mean = self.actor_mean(features)
            std = torch.exp(self.actor_log_std).expand_as(mean)
            value = self.critic(features).squeeze(-1)
            return mean, std, value

    requested_device = config.device
    if requested_device == "cuda" and not torch.cuda.is_available():
        requested_device = "cpu"
    return ActorCritic().to(requested_device)


def save_checkpoint(
    model,
    path: str,
    config: Optional[PPOConfig] = None,
    optimizer=None,
    update: int = 0,
) -> None:
    torch = require_torch()
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "config": (config or PPOConfig()).__dict__,
        "update": update,
    }
    if optimizer is not None:
        checkpoint["optimizer_state_dict"] = optimizer.state_dict()
    torch.save(checkpoint, checkpoint_path)


def load_checkpoint(path: str, config: Optional[PPOConfig] = None):
    torch = require_torch()
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    if config is None:
        config = PPOConfig(**checkpoint.get("config", {}))
    model = build_actor_critic(config)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model


def collect_rollout(
    env,
    model,
    buffer: RolloutBuffer,
    config: PPOConfig,
    observation: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, float, Dict[str, float]]:
    torch = require_torch()
    device = next(model.parameters()).device
    buffer.reset()

    if observation is None:
        observation, _ = env.reset(seed=config.seed)

    completed_rewards = []
    episode_reward = 0.0
    successes = 0
    done = False

    for _ in range(config.rollout_steps):
        observation_tensor = torch.as_tensor(
            observation, dtype=torch.float32, device=device
        ).unsqueeze(0)
        with torch.no_grad():
            mean, std, value = model(observation_tensor)
            distribution = torch.distributions.Normal(mean, std)
            unsquashed_action = distribution.sample()
            sampled_action = torch.tanh(unsquashed_action)
            log_prob = (
                distribution.log_prob(unsquashed_action)
                - torch.log(1.0 - sampled_action.pow(2) + 1.0e-6)
            ).sum(dim=-1)

        env_action = sampled_action.squeeze(0).cpu().numpy().astype(np.float32)
        next_observation, reward, terminated, truncated, info = env.step(env_action)
        done = terminated or truncated
        buffer.add(
            observation,
            env_action,
            reward,
            done,
            float(value.item()),
            float(log_prob.item()),
        )

        episode_reward += reward
        observation = next_observation
        if done:
            completed_rewards.append(episode_reward)
            successes += int(bool(info.get("touched", False)))
            episode_reward = 0.0
            observation, _ = env.reset()

    if done:
        last_value = 0.0
    else:
        with torch.no_grad():
            observation_tensor = torch.as_tensor(
                observation, dtype=torch.float32, device=device
            ).unsqueeze(0)
            _, _, value = model(observation_tensor)
        last_value = float(value.item())

    reward_samples = completed_rewards or [episode_reward]
    metrics = {
        "mean_episode_reward": float(np.mean(reward_samples)),
        "episodes": float(len(completed_rewards)),
        "successes": float(successes),
    }
    return observation, last_value, metrics


def ppo_update(
    model,
    optimizer,
    buffer: RolloutBuffer,
    config: PPOConfig,
    last_value: float = 0.0,
) -> Dict[str, float]:
    if buffer.index == 0:
        raise ValueError("Cannot update PPO with an empty rollout buffer")

    torch = require_torch()
    device = next(model.parameters()).device
    returns, advantages = buffer.returns_and_advantages(last_value)
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1.0e-8)

    observations = torch.as_tensor(
        buffer.observations[: buffer.index], dtype=torch.float32, device=device
    )
    actions = torch.as_tensor(
        buffer.actions[: buffer.index], dtype=torch.float32, device=device
    )
    old_log_probs = torch.as_tensor(
        buffer.log_probs[: buffer.index], dtype=torch.float32, device=device
    )
    returns_tensor = torch.as_tensor(returns, dtype=torch.float32, device=device)
    advantages_tensor = torch.as_tensor(
        advantages, dtype=torch.float32, device=device
    )

    totals = {"policy_loss": 0.0, "value_loss": 0.0, "entropy": 0.0}
    minibatches = 0
    for _ in range(config.update_epochs):
        indices = torch.randperm(buffer.index, device=device)
        for start in range(0, buffer.index, config.minibatch_size):
            batch = indices[start : start + config.minibatch_size]
            mean, std, values = model(observations[batch])
            distribution = torch.distributions.Normal(mean, std)
            bounded_actions = torch.clamp(actions[batch], -0.999999, 0.999999)
            unsquashed_actions = torch.atanh(bounded_actions)
            new_log_probs = (
                distribution.log_prob(unsquashed_actions)
                - torch.log(1.0 - bounded_actions.pow(2) + 1.0e-6)
            ).sum(dim=-1)
            entropy = distribution.entropy().sum(dim=-1).mean()

            ratio = torch.exp(new_log_probs - old_log_probs[batch])
            unclipped = ratio * advantages_tensor[batch]
            clipped = torch.clamp(
                ratio,
                1.0 - config.clip_epsilon,
                1.0 + config.clip_epsilon,
            ) * advantages_tensor[batch]
            policy_loss = -torch.min(unclipped, clipped).mean()
            value_loss = torch.nn.functional.mse_loss(values, returns_tensor[batch])
            loss = (
                policy_loss
                + config.value_coef * value_loss
                - config.entropy_coef * entropy
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
            optimizer.step()

            totals["policy_loss"] += float(policy_loss.detach().cpu().item())
            totals["value_loss"] += float(value_loss.detach().cpu().item())
            totals["entropy"] += float(entropy.detach().cpu().item())
            minibatches += 1

    return {name: value / minibatches for name, value in totals.items()}


def ppo_update_smoke(config: Optional[PPOConfig] = None) -> float:
    config = config or PPOConfig(rollout_steps=8, minibatch_size=4, update_epochs=1)
    torch = require_torch()
    seed_everything(config.seed)
    model = build_actor_critic(config)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    device = next(model.parameters()).device

    observations = torch.randn(config.minibatch_size, config.observation_dim, device=device)
    actions = torch.zeros(config.minibatch_size, config.action_dim, device=device)
    target_values = torch.ones(config.minibatch_size, device=device)
    advantages = torch.ones(config.minibatch_size, device=device)

    mean, std, values = model(observations)
    distribution = torch.distributions.Normal(mean, std)
    log_probs = distribution.log_prob(actions).sum(dim=-1)
    entropy = distribution.entropy().sum(dim=-1).mean()

    policy_loss = -(log_probs * advantages).mean()
    value_loss = torch.nn.functional.mse_loss(values, target_values)
    loss = policy_loss + config.value_coef * value_loss - config.entropy_coef * entropy

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
    optimizer.step()

    return float(loss.detach().cpu().item())
