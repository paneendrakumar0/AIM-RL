# Phase 1, Weeks 5-6: First Motion Command Node

## Implemented

- `aim_arm_control` ROS 2 C++ package.
- Geometric IK helper for the current 6-DOF arm dimensions.
- `cartesian_target_node` subscriber for `geometry_msgs/msg/PoseStamped` targets.
- Joint trajectory publisher for `/arm_controller/joint_trajectory`.
- `ik_smoke_test` executable for non-ROS validation of reachable and unreachable targets.

## Current Behavior

The node listens on:

```text
/aim_arm/target_pose
```

and publishes:

```text
/arm_controller/joint_trajectory
```

The current IK solver is intentionally simple. It solves shoulder pan, shoulder lift, elbow, and wrist pitch for a reachable Cartesian wrist pose, with wrist roll and wrist yaw held at zero. MoveIt 2 should replace this backend once the MoveIt stack is installed and configured.

## Manual Test

After building:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 run aim_arm_control cartesian_target_node
```

In another terminal:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 topic pub --once /aim_arm/target_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: world}, pose: {position: {x: 0.55, y: 0.1, z: 0.35}, orientation: {w: 1.0}}}"
```

