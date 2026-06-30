# Phase 4, Weeks 19-24: Hardware Bridge

## Implemented

- `aim_arm_hardware` C++ package.
- `serial_bridge_node` subscribes to `/arm_controller/joint_trajectory`.
- Serial packet encoder converts six joint radians to integer milliradians.
- Packet format:

```text
$AIM,j0,j1,j2,j3,j4,j5*XX\n
```

`XX` is an XOR checksum over the payload after `$` and before `*`.

- Dry-run mode is enabled by default so the node can run safely without hardware.
- Arduino sketch parses packets and stores six commanded joint values.
- Smoke test verifies packet formatting.

## Manual Test

```bash
source /opt/ros/humble/setup.bash
source colcon_ws/install/setup.bash
ros2 run aim_arm_hardware serial_packet_smoke_test
ros2 run aim_arm_hardware serial_bridge_node --ros-args -p dry_run:=true
```

To use real hardware later:

```bash
ros2 run aim_arm_hardware serial_bridge_node --ros-args -p dry_run:=false -p port:=/dev/ttyUSB0
```

