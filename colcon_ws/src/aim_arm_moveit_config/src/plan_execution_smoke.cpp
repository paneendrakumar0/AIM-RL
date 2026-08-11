#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

#include <moveit/move_group_interface/move_group_interface.h>
#include <rclcpp/rclcpp.hpp>

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>(
    "moveit_plan_execution_smoke",
    rclcpp::NodeOptions()
    .automatically_declare_parameters_from_overrides(true)
    .parameter_overrides({rclcpp::Parameter("use_sim_time", true)}));

  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() {executor.spin();});

  int result = 1;
  try {
    moveit::planning_interface::MoveGroupInterface move_group(node, "arm");
    move_group.setPlanningTime(10.0);
    move_group.setNumPlanningAttempts(5);
    move_group.setStartStateToCurrentState();

    if (!move_group.setNamedTarget("ready")) {
      throw std::runtime_error("MoveIt named target 'ready' is unavailable");
    }

    moveit::planning_interface::MoveGroupInterface::Plan plan;
    const auto plan_result = move_group.plan(plan);
    if (plan_result != moveit::core::MoveItErrorCode::SUCCESS) {
      throw std::runtime_error("MoveIt failed to plan to the 'ready' state");
    }

    const auto execute_result = move_group.execute(plan);
    if (execute_result != moveit::core::MoveItErrorCode::SUCCESS) {
      throw std::runtime_error("MoveIt failed to execute the planned trajectory");
    }

    std::cout << "MoveIt plan execution passed: target=ready" << std::endl;
    result = 0;
  } catch (const std::exception & error) {
    RCLCPP_ERROR(node->get_logger(), "%s", error.what());
  }

  executor.cancel();
  if (spinner.joinable()) {
    spinner.join();
  }
  rclcpp::shutdown();
  return result;
}
