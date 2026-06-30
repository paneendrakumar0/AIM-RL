#include "aim_arm_control/aim_arm_kinematics.hpp"

#include <algorithm>
#include <cmath>

namespace aim_arm_control
{
namespace
{
constexpr double kPi = 3.14159265358979323846;

double clamp(double value, double min_value, double max_value)
{
  return std::max(min_value, std::min(value, max_value));
}
}  // namespace

std::array<std::string, 6> jointNames()
{
  return {
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_pitch_joint",
    "wrist_roll_joint",
    "wrist_yaw_joint",
  };
}

std::optional<JointSolution> solveGeometricIk(
  const CartesianTarget & target,
  const ArmGeometry & geometry)
{
  const double shoulder_z = geometry.base_height + geometry.shoulder_height;
  const double radial = std::hypot(target.x, target.y);
  const double wrist_offset = geometry.wrist_length + geometry.tool_length;
  const double wrist_radial = radial - wrist_offset;
  const double wrist_z = target.z - shoulder_z;

  if (wrist_radial <= 0.02) {
    return std::nullopt;
  }

  const double distance = std::hypot(wrist_radial, wrist_z);
  const double reach_min = std::abs(geometry.upper_arm_length - geometry.forearm_length);
  const double reach_max = geometry.upper_arm_length + geometry.forearm_length;

  if (distance < reach_min || distance > reach_max) {
    return std::nullopt;
  }

  const double shoulder_pan = std::atan2(target.y, target.x);

  const double cos_elbow = clamp(
    (distance * distance -
    geometry.upper_arm_length * geometry.upper_arm_length -
    geometry.forearm_length * geometry.forearm_length) /
    (2.0 * geometry.upper_arm_length * geometry.forearm_length),
    -1.0,
    1.0);
  const double elbow = std::acos(cos_elbow);

  const double shoulder_to_target = std::atan2(wrist_z, wrist_radial);
  const double elbow_triangle = std::atan2(
    geometry.forearm_length * std::sin(elbow),
    geometry.upper_arm_length + geometry.forearm_length * std::cos(elbow));
  const double shoulder_lift = shoulder_to_target - elbow_triangle;
  const double wrist_pitch = -(shoulder_lift + elbow);

  if (shoulder_lift < -2.35619 || shoulder_lift > 2.35619) {
    return std::nullopt;
  }
  if (elbow < -2.61799 || elbow > 2.61799) {
    return std::nullopt;
  }
  if (wrist_pitch < -kPi || wrist_pitch > kPi) {
    return std::nullopt;
  }

  return JointSolution{{
    shoulder_pan,
    shoulder_lift,
    elbow,
    wrist_pitch,
    0.0,
    0.0,
  }};
}

}  // namespace aim_arm_control
