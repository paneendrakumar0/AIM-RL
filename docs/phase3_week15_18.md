# Phase 3, Weeks 15-18: Perception Pipeline

## Implemented

- `aim_arm_perception` Python package.
- OpenCV HSV target detector for an orange object.
- Pixel-to-workspace projection for a top-down camera assumption.
- ROS 2 `target_tracker_node` that subscribes to `sensor_msgs/msg/Image`.
- Publishes detected target coordinates as `geometry_msgs/msg/PoseStamped` on `/aim_arm/target_pose`.
- Synthetic-image smoke test.
- Gazebo world includes an overhead camera sensor publishing `/camera/image_raw`.
- Gazebo world includes an orange target block for camera tracking.

## Current Assumption

The detector assumes a top-down calibrated camera over the workspace. It maps image rows to workspace X and image columns to workspace Y. This is enough to connect perception to the existing Cartesian target node, and it can later be replaced with depth-camera or calibrated homography logic.

## Manual Test

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 run aim_arm_perception perception_smoke_test
ros2 run aim_arm_perception target_tracker_node
```
