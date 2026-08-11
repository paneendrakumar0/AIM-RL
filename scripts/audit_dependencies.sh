#!/usr/bin/env bash
set -euo pipefail

set +u
source /opt/ros/humble/setup.bash
set -u

required_ros_packages=(
  ament_cmake
  gazebo_ros
  gazebo_plugins
  geometry_msgs
  rclcpp
  rclpy
  robot_state_publisher
  sensor_msgs
  trajectory_msgs
  xacro
)

optional_ros_packages=(
  controller_manager
  gazebo_ros2_control
  joint_state_broadcaster
  joint_trajectory_controller
  moveit_ros_planning_interface
  moveit_setup_assistant
  ros2_control
)

python_modules=(
  cv2
  cv_bridge
  gymnasium
  numpy
  torch
)

echo "Required ROS packages"
for package in "${required_ros_packages[@]}"; do
  if ros2 pkg prefix "${package}" >/dev/null 2>&1; then
    echo "  ok      ${package}"
  else
    echo "  missing ${package}"
    exit_code=1
  fi
done

echo
echo "Optional ROS packages"
for package in "${optional_ros_packages[@]}"; do
  if ros2 pkg prefix "${package}" >/dev/null 2>&1; then
    echo "  ok      ${package}"
  else
    echo "  missing ${package}"
  fi
done

echo
echo "Python modules"
for module in "${python_modules[@]}"; do
  if python3 -c "import ${module}" >/dev/null 2>&1; then
    echo "  ok      ${module}"
  else
    echo "  missing ${module}"
  fi
done

exit "${exit_code:-0}"
