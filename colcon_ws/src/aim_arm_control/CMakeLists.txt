cmake_minimum_required(VERSION 3.8)
project(aim_arm_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(trajectory_msgs REQUIRED)

add_library(aim_arm_kinematics src/aim_arm_kinematics.cpp)
target_include_directories(aim_arm_kinematics PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>")
target_compile_features(aim_arm_kinematics PUBLIC cxx_std_17)

add_executable(cartesian_target_node src/cartesian_target_node.cpp)
target_link_libraries(cartesian_target_node aim_arm_kinematics)
ament_target_dependencies(cartesian_target_node
  geometry_msgs
  rclcpp
  trajectory_msgs)

add_executable(ik_smoke_test src/ik_smoke_test.cpp)
target_link_libraries(ik_smoke_test aim_arm_kinematics)

install(
  TARGETS aim_arm_kinematics cartesian_target_node ik_smoke_test
  EXPORT export_aim_arm_control
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_export_include_directories(include)
ament_export_libraries(aim_arm_kinematics)
ament_package()

