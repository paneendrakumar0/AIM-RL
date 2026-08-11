#include <chrono>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include <geometry_msgs/msg/pose.hpp>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <rclcpp/rclcpp.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>

namespace
{

void add_box(
  moveit_msgs::msg::CollisionObject & object,
  double size_x, double size_y, double size_z,
  double x, double y, double z)
{
  shape_msgs::msg::SolidPrimitive primitive;
  primitive.type = shape_msgs::msg::SolidPrimitive::BOX;
  primitive.dimensions = {size_x, size_y, size_z};

  geometry_msgs::msg::Pose pose;
  pose.orientation.w = 1.0;
  pose.position.x = x;
  pose.position.y = y;
  pose.position.z = z;

  object.primitives.push_back(primitive);
  object.primitive_poses.push_back(pose);
}

moveit_msgs::msg::CollisionObject make_table()
{
  moveit_msgs::msg::CollisionObject table;
  table.header.frame_id = "world";
  table.id = "workspace_table";
  table.operation = moveit_msgs::msg::CollisionObject::ADD;

  // Preserve the Gazebo tabletop while leaving a mounting clearance around
  // base_link. The robot is spawned 5 cm above Gazebo's world origin, while
  // MoveIt's fixed world_to_base transform starts at zero.
  add_box(table, 0.87, 0.80, 0.05, 0.615, 0.0, 0.025);
  add_box(table, 0.33, 0.22, 0.05, 0.015, 0.29, 0.025);
  add_box(table, 0.33, 0.22, 0.05, 0.015, -0.29, 0.025);
  return table;
}

moveit_msgs::msg::CollisionObject make_target()
{
  moveit_msgs::msg::CollisionObject target;
  target.header.frame_id = "world";
  target.id = "target_block";
  target.operation = moveit_msgs::msg::CollisionObject::ADD;
  add_box(target, 0.06, 0.06, 0.06, 0.55, 0.10, 0.085);
  return target;
}

}  // namespace

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("aim_arm_planning_scene_loader");
  moveit::planning_interface::PlanningSceneInterface planning_scene;
  const std::vector<moveit_msgs::msg::CollisionObject> objects{
    make_table(), make_target()};

  constexpr auto retry_delay = std::chrono::seconds(1);
  constexpr int max_attempts = 30;
  for (int attempt = 1; attempt <= max_attempts; ++attempt) {
    if (planning_scene.applyCollisionObjects(objects)) {
      RCLCPP_INFO(
        node->get_logger(),
        "Planning scene synchronized: workspace_table, target_block");
      rclcpp::shutdown();
      return 0;
    }
    RCLCPP_WARN(
      node->get_logger(), "Planning scene service unavailable (attempt %d/%d)",
      attempt, max_attempts);
    std::this_thread::sleep_for(retry_delay);
  }

  RCLCPP_ERROR(node->get_logger(), "Failed to synchronize the Gazebo workcell");
  rclcpp::shutdown();
  return 1;
}
