# Phase 1, Weeks 1-2: Digital Twin Foundation

## Objective

Create a clean ROS 2 workspace and a first 6-DOF manipulator URDF that can be parsed, built, and visualized before simulation and MoveIt 2 are introduced.

## Implemented

- Native ROS 2 workspace at `colcon_ws`.
- ROS 2 description package at `colcon_ws/src/aim_arm_description`.
- Xacro-driven URDF for a simple 6-DOF robotic arm using primitive geometry.
- Physical properties for every moving link: mass, inertia, visuals, and collisions.
- Joint limits for six revolute joints and a fixed tool frame.
- RViz launch path for visual inspection.
- Gazebo Classic launch path and a simple workspace table world.
- Optional `ros2_control`/Gazebo controller description, kept disabled by default until dependencies are installed.
- Validation script for repeatable checks.

## Validation Loop

Run:

```bash
./scripts/validate_phase1.sh
```

The loop verifies:

- Required ROS 2 tools are available.
- Package metadata is valid enough to build.
- Xacro expands into URDF.
- Generated URDF is valid XML.
- Core robot model counts are present.
- `colcon build` succeeds for the workspace.
- Optional controller-enabled Xacro expansion remains valid XML.

## Next Phase 1 Work

- Install `gazebo_ros2_control` and run a live controller-manager simulation test.
- Add a MoveIt 2 configuration package.
- Add a C++ target pose planning node after the MoveIt package exists.

## Simulation Preview

Run:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 launch aim_arm_description gazebo.launch.py
```

This launches Gazebo Classic with `aim_empty.world` and spawns the robot from `robot_description`.
