# AIM-RL Status

## Validated Locally

- ROS 2 workspace builds with six packages.
- 6-DOF URDF/Xacro expands and parses.
- Gazebo Classic world XML parses.
- Optional `ros2_control` XML expands.
- C++ Cartesian target node publishes six-joint trajectories.
- Synthetic camera publishes images.
- OpenCV target tracker publishes `/aim_arm/target_pose`.
- Dry-run serial bridge encodes clamped joint packets.
- Topic-flow smoke test confirms camera -> target pose -> joint trajectory.

## Current Blockers for Live Advanced Modes

- MoveIt 2 is not installed.
- `gazebo_ros2_control` and ROS 2 controller packages are not installed.
- Gymnasium and PyTorch are not installed.
- No physical microcontroller is attached for serial write verification.

## Next Implementation Targets

- Add a MoveIt package once MoveIt 2 is installed.
- Add a ROS/Gazebo stepping backend for the RL environment once controllers are live.
- Expand Arduino firmware from parsing-only to actuator pin output once hardware is selected.
