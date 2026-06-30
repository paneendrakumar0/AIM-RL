#include "aim_arm_hardware/serial_packet.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/types.h>
#include <termios.h>
#include <unistd.h>

#include "rclcpp/rclcpp.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"

namespace aim_arm_hardware
{

class SerialBridgeNode : public rclcpp::Node
{
public:
  SerialBridgeNode()
  : Node("serial_bridge_node")
  {
    port_ = declare_parameter<std::string>("port", "/dev/ttyUSB0");
    baud_rate_ = declare_parameter<int>("baud_rate", 115200);
    trajectory_topic_ = declare_parameter<std::string>(
      "trajectory_topic", "/arm_controller/joint_trajectory");
    dry_run_ = declare_parameter<bool>("dry_run", true);

    if (!dry_run_) {
      openSerialPort();
    }

    subscription_ = create_subscription<trajectory_msgs::msg::JointTrajectory>(
      trajectory_topic_,
      10,
      [this](const trajectory_msgs::msg::JointTrajectory::SharedPtr msg) {
        handleTrajectory(*msg);
      });

    RCLCPP_INFO(
      get_logger(),
      "Serial bridge listening on %s, dry_run=%s",
      trajectory_topic_.c_str(),
      dry_run_ ? "true" : "false");
  }

  ~SerialBridgeNode() override
  {
    if (serial_fd_ >= 0) {
      close(serial_fd_);
    }
  }

private:
  void openSerialPort()
  {
    serial_fd_ = open(port_.c_str(), O_RDWR | O_NOCTTY | O_SYNC);
    if (serial_fd_ < 0) {
      throw std::runtime_error(
        "Failed to open serial port " + port_ + ": " + std::strerror(errno));
    }

    termios tty{};
    if (tcgetattr(serial_fd_, &tty) != 0) {
      throw std::runtime_error("Failed to read serial attributes");
    }

    cfsetospeed(&tty, B115200);
    cfsetispeed(&tty, B115200);
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_iflag &= ~IGNBRK;
    tty.c_lflag = 0;
    tty.c_oflag = 0;
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 5;
    tty.c_iflag &= ~(IXON | IXOFF | IXANY);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD);
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    if (tcsetattr(serial_fd_, TCSANOW, &tty) != 0) {
      throw std::runtime_error("Failed to configure serial port");
    }
  }

  void handleTrajectory(const trajectory_msgs::msg::JointTrajectory & msg)
  {
    if (msg.points.empty() || msg.points.front().positions.size() < 6) {
      RCLCPP_WARN(get_logger(), "Ignoring trajectory without six joint positions");
      return;
    }

    std::array<double, 6> positions{};
    for (std::size_t i = 0; i < positions.size(); ++i) {
      positions[i] = msg.points.front().positions[i];
    }

    const std::string packet = encodeJointPacket(positions);
    if (dry_run_) {
      RCLCPP_INFO(get_logger(), "Dry-run serial packet: %s", packet.c_str());
      return;
    }

    const ssize_t written = write(serial_fd_, packet.data(), packet.size());
    if (written != static_cast<ssize_t>(packet.size())) {
      RCLCPP_ERROR(get_logger(), "Failed to write full serial packet");
    }
  }

  std::string port_;
  int baud_rate_;
  std::string trajectory_topic_;
  bool dry_run_;
  int serial_fd_{-1};
  rclcpp::Subscription<trajectory_msgs::msg::JointTrajectory>::SharedPtr subscription_;
};

}  // namespace aim_arm_hardware

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<aim_arm_hardware::SerialBridgeNode>());
  rclcpp::shutdown();
  return 0;
}

