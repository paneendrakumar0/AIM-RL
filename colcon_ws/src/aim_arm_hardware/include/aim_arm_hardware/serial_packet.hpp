#pragma once

#include <array>
#include <cstdint>
#include <string>

namespace aim_arm_hardware
{

std::string encodeJointPacket(const std::array<double, 6> & radians);
uint8_t checksum(const std::string & payload);

}  // namespace aim_arm_hardware

