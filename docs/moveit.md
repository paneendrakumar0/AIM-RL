# MoveIt

`aim_arm_moveit_config` defines:

- `arm` planning group from `base_link` to `tool0`.
- Home and ready named states.
- KDL kinematics settings.
- Joint limits matching the URDF.
- An OMPL planning pipeline using RRTConnect by default.
- A MoveIt controller mapping to the simulated `arm_controller` trajectory action.
- A standalone `move_group.launch.py` launch file.
- A `planning_simulation.launch.py` launch file that combines controlled Gazebo and MoveIt.

Install the optional ROS dependencies before running the planning pipeline:

```bash
./scripts/install_ros_optional_dependencies.sh
```

Then build and launch:

```bash
source /opt/ros/humble/setup.bash
cd colcon_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch aim_arm_moveit_config planning_simulation.launch.py
```

The base validation loop checks the launch syntax and planning/controller configuration even when MoveIt is unavailable. When MoveIt is installed, `scripts/run_all_checks.sh` also starts `move_group` and verifies that its ROS node is available.

