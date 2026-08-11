cmake_minimum_required(VERSION 3.8)
project(aim_arm_moveit_config)

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(rclcpp REQUIRED)
find_package(shape_msgs REQUIRED)

add_executable(planning_scene_loader src/planning_scene_loader.cpp)
ament_target_dependencies(
  planning_scene_loader
  geometry_msgs
  moveit_msgs
  moveit_ros_planning_interface
  rclcpp
  shape_msgs
)

add_executable(plan_execution_smoke src/plan_execution_smoke.cpp)
ament_target_dependencies(
  plan_execution_smoke
  moveit_msgs
  moveit_ros_planning_interface
  rclcpp
)

install(
  TARGETS plan_execution_smoke planning_scene_loader
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

