#include "aim_arm_hardware/serial_packet.hpp"

#include <cmath>
#include <algorithm>
#include <iomanip>
#include <sstream>

namespace aim_arm_hardware
{

uint8_t checksum(const std::string & payload)
{
  uint8_t value = 0;
  for (const char character : payload) {
    value ^= static_cast<uint8_t>(character);
  }
  return value;
}

std::array<double, 6> clampJointPositions(const std::array<double, 6> & radians)
{
  constexpr std::array<double, 6> lower{
    -3.14159, -2.35619, -2.61799, -3.14159, -3.14159, -3.14159};
  constexpr std::array<double, 6> upper{
    3.14159, 2.35619, 2.61799, 3.14159, 3.14159, 3.14159};

  std::array<double, 6> clamped{};
  for (std::size_t i = 0; i < radians.size(); ++i) {
    clamped[i] = std::max(lower[i], std::min(radians[i], upper[i]));
  }
  return clamped;
}

std::string encodeJointPacket(const std::array<double, 6> & radians)
{
  const auto clamped_radians = clampJointPositions(radians);
  std::ostringstream payload;
  payload << "AIM";
  for (const double radian : clamped_radians) {
    const long milliradians = std::lround(radian * 1000.0);
    payload << ',' << milliradians;
  }

  const std::string payload_text = payload.str();
  std::ostringstream packet;
  packet << '$' << payload_text << '*'
         << std::uppercase << std::hex << std::setw(2) << std::setfill('0')
         << static_cast<int>(checksum(payload_text)) << '\n';
  return packet.str();
}

}  // namespace aim_arm_hardware
