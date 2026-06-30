#include "aim_arm_control/aim_arm_kinematics.hpp"

#include <cstdlib>
#include <iostream>

int main()
{
  const aim_arm_control::CartesianTarget target{0.55, 0.10, 0.35};
  const auto solution = aim_arm_control::solveGeometricIk(target);
  if (!solution) {
    std::cerr << "Expected reachable target failed IK\n";
    return EXIT_FAILURE;
  }

  const auto names = aim_arm_control::jointNames();
  for (std::size_t i = 0; i < names.size(); ++i) {
    std::cout << names[i] << "=" << solution->positions[i] << "\n";
  }

  const aim_arm_control::CartesianTarget unreachable{2.0, 0.0, 2.0};
  if (aim_arm_control::solveGeometricIk(unreachable)) {
    std::cerr << "Expected unreachable target produced IK\n";
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}

