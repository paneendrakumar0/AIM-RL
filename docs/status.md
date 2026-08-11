# AIM-RL Status

## Validated Locally

- ROS 2 workspace builds with seven packages.
- 6-DOF URDF/Xacro expands and parses.
- Gazebo Classic world XML parses.
- Gazebo world contains an overhead camera and orange target block.
- Optional `ros2_control` XML expands.
- Controlled Gazebo launches with active joint-state and arm trajectory controllers.
- ROS 2 control and MoveIt configuration is validated statically and at runtime.
- Controlled trajectory smoke verifies joint command path into Gazebo controller.
- C++ Cartesian target node publishes six-joint trajectories.
- Synthetic camera publishes images.
- OpenCV target tracker publishes `/aim_arm/target_pose`.
- Dry-run serial bridge encodes clamped joint packets.
- MoveIt configuration defines the planning group, OMPL pipeline, joint limits, and trajectory controller mapping.
- MoveIt plans and executes the named `ready` state through the simulated trajectory controller.
- MoveIt mirrors the Gazebo tabletop and target block into its planning scene.
- Topic-flow smoke test confirms camera -> target pose -> joint trajectory.
- CPU PyTorch and Gymnasium are installed for RL trainer initialization.

## Current Blockers for Live Advanced Modes

- No physical microcontroller is attached for serial write verification.

## Recently Unlocked

- Gymnasium is installed.
- CPU PyTorch is installed.
- PPO training collects rollouts, performs clipped minibatch updates, and writes training-state checkpoints plus CSV metrics.
- Policy evaluation loads the trained checkpoint and writes aggregate rollout metrics.

## Next Implementation Targets

- Add a ROS/Gazebo stepping backend for the RL environment.
- Expand Arduino firmware from parsing-only to actuator pin output once hardware is selected.
