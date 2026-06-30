from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ModuleNotFoundError:
    gym = None
    spaces = None


@dataclass(frozen=True)
class ArmReachState:
    joint_positions: np.ndarray
    joint_velocities: np.ndarray
    target_xyz: np.ndarray
    end_effector_xyz: np.ndarray

    def observation(self) -> np.ndarray:
        return np.concatenate(
            [
                self.joint_positions.astype(np.float32),
                self.joint_velocities.astype(np.float32),
                self.target_xyz.astype(np.float32),
            ]
        )


def compute_reward(
    previous_distance: float,
    current_distance: float,
    touched: bool = False,
    crashed: bool = False,
) -> float:
    progress_reward = previous_distance - current_distance
    reward = 10.0 * progress_reward - 0.01
    if touched:
        reward += 100.0
    if crashed:
        reward -= 50.0
    return float(reward)


class MockArmReachEnv:
    """Small deterministic environment for validating reward and loop plumbing."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        target_xyz: Optional[np.ndarray] = None,
        max_steps: int = 200,
        dt: float = 0.05,
    ) -> None:
        self.target_xyz = np.array(
            target_xyz if target_xyz is not None else [0.55, 0.10, 0.35],
            dtype=np.float32,
        )
        self.max_steps = max_steps
        self.dt = dt
        self.step_count = 0
        self.state = self._initial_state()
        self.previous_distance = self._distance(self.state)

        if spaces is not None:
            self.action_space = spaces.Box(
                low=-1.0,
                high=1.0,
                shape=(6,),
                dtype=np.float32,
            )
            self.observation_space = spaces.Box(
                low=-np.inf,
                high=np.inf,
                shape=(15,),
                dtype=np.float32,
            )

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict] = None,
    ) -> Tuple[np.ndarray, Dict]:
        del seed, options
        self.step_count = 0
        self.state = self._initial_state()
        self.previous_distance = self._distance(self.state)
        return self.state.observation(), {"distance": self.previous_distance}

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (6,):
            raise ValueError(f"Expected action shape (6,), got {action.shape}")

        clipped_action = np.clip(action, -1.0, 1.0)
        joint_velocities = clipped_action
        joint_positions = self.state.joint_positions + joint_velocities * self.dt

        end_effector_xyz = self._forward_proxy(joint_positions)
        self.state = ArmReachState(
            joint_positions=joint_positions.astype(np.float32),
            joint_velocities=joint_velocities.astype(np.float32),
            target_xyz=self.target_xyz,
            end_effector_xyz=end_effector_xyz.astype(np.float32),
        )

        current_distance = self._distance(self.state)
        touched = current_distance < 0.03
        crashed = bool(end_effector_xyz[2] < 0.02)
        reward = compute_reward(self.previous_distance, current_distance, touched, crashed)
        self.previous_distance = current_distance
        self.step_count += 1

        terminated = touched or crashed
        truncated = self.step_count >= self.max_steps
        info = {
            "distance": current_distance,
            "touched": touched,
            "crashed": crashed,
        }
        return self.state.observation(), reward, terminated, truncated, info

    def _initial_state(self) -> ArmReachState:
        joint_positions = np.zeros(6, dtype=np.float32)
        joint_velocities = np.zeros(6, dtype=np.float32)
        end_effector_xyz = self._forward_proxy(joint_positions)
        return ArmReachState(
            joint_positions=joint_positions,
            joint_velocities=joint_velocities,
            target_xyz=self.target_xyz,
            end_effector_xyz=end_effector_xyz.astype(np.float32),
        )

    @staticmethod
    def _forward_proxy(joint_positions: np.ndarray) -> np.ndarray:
        shoulder_pan = joint_positions[0]
        shoulder_lift = joint_positions[1]
        elbow = joint_positions[2]
        upper = 0.42
        forearm = 0.36
        wrist_tool = 0.24
        radial = (
            upper * np.cos(shoulder_lift)
            + forearm * np.cos(shoulder_lift + elbow)
            + wrist_tool * np.cos(shoulder_lift + elbow + joint_positions[3])
        )
        z = (
            0.28
            + upper * np.sin(shoulder_lift)
            + forearm * np.sin(shoulder_lift + elbow)
            + wrist_tool * np.sin(shoulder_lift + elbow + joint_positions[3])
        )
        return np.array(
            [
                radial * np.cos(shoulder_pan),
                radial * np.sin(shoulder_pan),
                z,
            ],
            dtype=np.float32,
        )

    @staticmethod
    def _distance(state: ArmReachState) -> float:
        return float(np.linalg.norm(state.target_xyz - state.end_effector_xyz))


if gym is not None:

    class GymnasiumArmReachEnv(MockArmReachEnv, gym.Env):
        pass

else:
    GymnasiumArmReachEnv = None

