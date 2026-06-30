# AIM-RL

AI-driven robotic arm software stack for simulation-first reinforcement learning, ROS 2 middleware, perception, and eventual hardware deployment.

## Current Phase

Phase 1, Weeks 1-2: build the ROS 2 workspace and first digital twin.

This repository currently contains:

- `colcon_ws/src/aim_arm_description`: ROS 2 package for a 6-DOF manipulator description.
- `colcon_ws/src/aim_arm_control`: ROS 2 C++ package for early Cartesian target to joint trajectory commands.
- `colcon_ws/src/aim_arm_rl`: Python package for the reinforcement-learning environment bridge.
- `colcon_ws/src/aim_arm_perception`: OpenCV target tracking package for camera-to-target pose publishing.
- `colcon_ws/src/aim_arm_hardware`: serial bridge package for microcontroller joint commands.
- `colcon_ws/src/aim_arm_bringup`: launch package for the dry-run software pipeline.
- `firmware/aim_arm_serial_driver`: Arduino-side packet parser scaffold.
- `scripts/validate_phase1.sh`: repeatable validation loop for package metadata, URDF generation, XML parsing, and colcon build.
- `docs/phase1_week1_2.md`: implementation notes and next checks.

## Quick Start

```bash
cd /home/paneendra/AIM-RL
./scripts/validate_stack.sh
```

To visualize the robot after a successful build:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 launch aim_arm_description display.launch.py
```

To run the current validation smoke tests:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 run aim_arm_rl rl_smoke_test
```

To audit installed dependencies:

```bash
./scripts/audit_dependencies.sh
```
