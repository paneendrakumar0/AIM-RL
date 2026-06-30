# Bringup

## Dry-Run Software Pipeline

The bringup launch starts:

- `robot_state_publisher`
- `synthetic_camera_node`
- `target_tracker_node`
- `cartesian_target_node`
- `serial_bridge_node` in dry-run mode

Run:

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 launch aim_arm_bringup software_pipeline.launch.py
```

This connects the intended topic chain:

```text
/camera/image_raw
  <- synthetic camera frames by default
  -> aim_arm_perception
/aim_arm/target_pose
  -> aim_arm_control
/arm_controller/joint_trajectory
  -> aim_arm_hardware
serial packet dry-run output
```

To point at a real microcontroller later:

```bash
ros2 launch aim_arm_bringup software_pipeline.launch.py dry_run:=false serial_port:=/dev/ttyUSB0
```

To use a real camera topic instead of the synthetic publisher:

```bash
ros2 launch aim_arm_bringup software_pipeline.launch.py use_synthetic_camera:=false image_topic:=/your/camera/topic
```
