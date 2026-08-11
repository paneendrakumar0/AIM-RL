# Findings and Recommendations

## Validated Findings

- The seven-package ROS 2 workspace builds successfully on Humble.
- Gazebo starts the six-joint arm with active `joint_state_broadcaster` and `arm_controller` instances.
- MoveIt loads the SRDF, KDL configuration, and OMPL RRTConnect planning pipeline.
- MoveIt plans the named `ready` state and executes it successfully through the simulated `FollowJointTrajectory` controller.
- The Gazebo camera plugin starts and advertises the remapped `/camera/image_raw` and `/camera/camera_info` topics.
- In the tested WSLg session, the camera publisher advertised successfully but did not deliver image frames; the accelerated Gazebo viewport also appeared black to desktop capture tools.
- PPO rollout training and checkpoint-based evaluation run on the mock arm environment.

## Prioritized Recommendations

1. **Synchronize collision geometry.** Publish the Gazebo table and target block into the MoveIt planning scene so plans account for the complete workcell.
2. **Add synchronous simulation stepping.** Replace the mock RL dynamics with a reset/step backend that commands Gazebo and waits for fresh joint and target state.
3. **Measure planning quality.** Record planning time, path length, execution duration, and controller error for repeatable comparisons.
4. **Harden camera validation.** Run the Gazebo camera smoke in a native GPU-enabled Linux/container environment, require at least one decoded frame, and retain the captured artifact in CI.
5. **Calibrate perception.** Replace the current planar pixel mapping with camera intrinsics, extrinsics, and depth or multi-view target estimation.
6. **Define actuator hardware.** Select motor drivers, encoders, limits, and emergency-stop behavior before mapping parsed Arduino commands to pins.
7. **Add CI tiers.** Keep static/base checks fast, then run MoveIt/Gazebo and PyTorch integration jobs in dependency-complete containers.

## Evidence

| Gazebo workcell definition | Validation findings |
| --- | --- |
| ![Gazebo digital twin workcell](../media/screenshots/gazebo_world_overview.png) | ![MoveIt validation findings](../media/screenshots/moveit_validation_findings.png) |

The workcell image is generated from the tracked world contents. The findings card records the live plan-execution checks. A real camera artifact can be requested by setting `CAPTURE_IMAGE_PATH` when running `scripts/smoke_moveit_execution.sh`; the smoke fails instead of creating misleading evidence when no frame arrives.

During evidence capture, the native Gazebo camera topic was available but its ROS image topic was initially absent. The audit traced that issue to a missing `gazebo_plugins` runtime package; the package manifest and dependency installer now declare it explicitly. Installing the plugin and correcting the fully-qualified remaps exposed the expected ROS topics. Frame delivery remains an environment-specific open finding under WSLg and is not represented as a passing screenshot.
