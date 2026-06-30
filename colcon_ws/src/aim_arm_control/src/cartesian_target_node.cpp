#include "aim_arm_control/aim_arm_kinematics.hpp"

#include <chrono>
#include <memory>
#include <string>

#include "geometry_msgs/msg/pose_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory_point.hpp"

namespace aim_arm_control
{

class CartesianTargetNode : public rclcpp::Node
{
public:
  CartesianTargetNode()
  : Node("cartesian_target_node")
  {
    trajectory_topic_ = declare_parameter<std::string>(
      "trajectory_topic", "/arm_controller/joint_trajectory");
    target_topic_ = declare_parameter<std::string>(
      "target_topic", "/aim_arm/target_pose");
    motion_duration_sec_ = declare_parameter<double>("motion_duration_sec", 2.0);

    publisher_ = create_publisher<trajectory_msgs::msg::JointTrajectory>(
      trajectory_topic_, 10);
    subscription_ = create_subscription<geometry_msgs::msg::PoseStamped>(
      target_topic_,
      10,
      [this](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        handleTarget(*msg);
      });

    RCLCPP_INFO(
      get_logger(),
      "Listening for Cartesian targets on %s and publishing trajectories on %s",
      target_topic_.c_str(),
      trajectory_topic_.c_str());
  }

private:
  void handleTarget(const geometry_msgs::msg::PoseStamped & msg)
  {
    const CartesianTarget target{
      msg.pose.position.x,
      msg.pose.position.y,
      msg.pose.position.z,
    };

    const auto solution = solveGeometricIk(target);
    if (!solution) {
      RCLCPP_WARN(
        get_logger(),
        "Target is outside geometric IK reach: x=%.3f y=%.3f z=%.3f",
        target.x,
        target.y,
        target.z);
      return;
    }

    trajectory_msgs::msg::JointTrajectory trajectory;
    const auto names = jointNames();
    trajectory.joint_names.assign(names.begin(), names.end());

    trajectory_msgs::msg::JointTrajectoryPoint point;
    point.positions.assign(
      solution->positions.begin(),
      solution->positions.end());
    point.time_from_start = rclcpp::Duration::from_seconds(motion_duration_sec_);
    trajectory.points.push_back(point);

    publisher_->publish(trajectory);
    RCLCPP_INFO(
      get_logger(),
      "Published IK trajectory for target x=%.3f y=%.3f z=%.3f",
      target.x,
      target.y,
      target.z);
  }

  std::string trajectory_topic_;
  std::string target_topic_;
  double motion_duration_sec_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr publisher_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr subscription_;
};

}  // namespace aim_arm_control

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<aim_arm_control::CartesianTargetNode>());
  rclcpp::shutdown();
  return 0;
}

