#pragma once

#include <array>
#include <optional>
#include <string>

namespace aim_arm_control
{

struct CartesianTarget
{
  double x;
  double y;
  double z;
};

struct JointSolution
{
  std::array<double, 6> positions;
};

struct ArmGeometry
{
  double base_height{0.12};
  double shoulder_height{0.16};
  double upper_arm_length{0.42};
  double forearm_length{0.36};
  double wrist_length{0.14};
  double tool_length{0.10};
};

std::optional<JointSolution> solveGeometricIk(
  const CartesianTarget & target,
  const ArmGeometry & geometry = ArmGeometry{});

std::array<std::string, 6> jointNames();

}  // namespace aim_arm_control

