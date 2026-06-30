#include "aim_arm_hardware/serial_packet.hpp"

#include <array>
#include <cstdlib>
#include <iostream>
#include <string>

int main()
{
  const std::array<double, 6> positions{0.0, 0.5, -0.5, 1.234, -1.234, 3.14159};
  const std::string packet = aim_arm_hardware::encodeJointPacket(positions);

  if (packet.rfind("$AIM,0,500,-500,1234,-1234,3142*", 0) != 0) {
    std::cerr << "Unexpected serial packet payload: " << packet;
    return EXIT_FAILURE;
  }
  if (packet.back() != '\n') {
    std::cerr << "Serial packet should end with newline\n";
    return EXIT_FAILURE;
  }

  std::cout << "Serial packet smoke test passed: " << packet;
  return EXIT_SUCCESS;
}

