cmake_minimum_required(VERSION 3.8)
project(aim_arm_hardware)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(trajectory_msgs REQUIRED)

add_library(serial_packet src/serial_packet.cpp)
target_include_directories(serial_packet PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>")
target_compile_features(serial_packet PUBLIC cxx_std_17)

add_executable(serial_bridge_node src/serial_bridge_node.cpp)
target_link_libraries(serial_bridge_node serial_packet)
ament_target_dependencies(serial_bridge_node rclcpp trajectory_msgs)

add_executable(serial_packet_smoke_test src/serial_packet_smoke_test.cpp)
target_link_libraries(serial_packet_smoke_test serial_packet)

install(
  TARGETS serial_packet serial_bridge_node serial_packet_smoke_test
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_export_include_directories(include)
ament_export_libraries(serial_packet)
ament_package()

