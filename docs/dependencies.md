# Dependencies

## Installed and Used Now

The current repository validates against ROS 2 Humble with:

- `ament_cmake`
- `colcon`
- `gazebo_ros`
- `robot_state_publisher`
- `rviz2`
- `xacro`
- `cv_bridge`
- `python3-opencv`

## Needed for the Next Control Checkpoint

Install these before enabling simulated joint controllers:

```bash
sudo apt update
sudo apt install \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-gazebo-ros2-control \
  ros-humble-joint-trajectory-controller \
  ros-humble-joint-state-broadcaster
```

After installation, the model can be expanded with:

```bash
xacro colcon_ws/src/aim_arm_description/urdf/aim_arm.urdf.xacro enable_ros2_control:=true
```

## Needed for Reinforcement Learning Training

The Phase 2 bridge can build without Gymnasium/PyTorch, but real RL training needs:

```bash
python3 -m pip install -r requirements-rl.txt
```
