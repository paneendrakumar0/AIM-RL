from __future__ import annotations

from dataclasses import dataclass
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


def build_actor_critic(config: Optional[PPOConfig] = None):
    config = config or PPOConfig()
    torch = require_torch()
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

