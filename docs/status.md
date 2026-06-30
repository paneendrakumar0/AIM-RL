# AIM-RL Status

## Validated Locally

- ROS 2 workspace builds with six packages.
- 6-DOF URDF/Xacro expands and parses.
- Gazebo Classic world XML parses.
- Gazebo world contains an overhead camera and orange target block.
- Optional `ros2_control` XML expands.
- Controlled Gazebo launch scaffold is syntax-validated.
- ROS 2 control and MoveIt dependencies are installed.
- Controlled trajectory smoke verifies joint command path into Gazebo controller.
- C++ Cartesian target node publishes six-joint trajectories.
- Synthetic camera publishes images.
- OpenCV target tracker publishes `/aim_arm/target_pose`.
- Dry-run serial bridge encodes clamped joint packets.
- MoveIt configuration scaffold defines planning group and joint limits.
- Topic-flow smoke test confirms camera -> target pose -> joint trajectory.
- CPU PyTorch and Gymnasium are installed for RL trainer initialization.

## Current Blockers for Live Advanced Modes

- MoveIt 2 is not installed.
- `gazebo_ros2_control` and ROS 2 controller packages are not installed.
- No physical microcontroller is attached for serial write verification.

## Recently Unlocked

- Gymnasium is installed.
- CPU PyTorch is installed.
- PPO smoke training writes checkpoint and metrics artifacts.
- Policy evaluation smoke writes rollout metrics.

## Next Implementation Targets

- Expand MoveIt launch/planning pipelines once MoveIt 2 is installed.
- Add a ROS/Gazebo stepping backend for the RL environment once controllers are live.
- Expand Arduino firmware from parsing-only to actuator pin output once hardware is selected.
