from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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


def save_checkpoint(model, path: str, config: Optional[PPOConfig] = None) -> None:
    torch = require_torch()
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": (config or PPOConfig()).__dict__,
        },
        checkpoint_path,
    )


def load_checkpoint(path: str, config: Optional[PPOConfig] = None):
    torch = require_torch()
    model = build_actor_critic(config)
    checkpoint = torch.load(path, map_location=next(model.parameters()).device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model


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
