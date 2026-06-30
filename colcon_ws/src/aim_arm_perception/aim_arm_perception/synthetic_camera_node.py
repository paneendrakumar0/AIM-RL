from __future__ import annotations

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class SyntheticCameraNode(Node):
    def __init__(self) -> None:
        super().__init__("synthetic_camera_node")
        self.image_topic = self.declare_parameter("image_topic", "/camera/image_raw").value
        self.width = int(self.declare_parameter("width", 320).value)
        self.height = int(self.declare_parameter("height", 240).value)
        self.radius = int(self.declare_parameter("radius", 24).value)
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, self.image_topic, 10)
        self.tick = 0
        self.timer = self.create_timer(0.1, self.publish_frame)
        self.get_logger().info(f"Publishing synthetic camera frames on {self.image_topic}")

    def publish_frame(self) -> None:
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        center_x = int(self.width * (0.5 + 0.2 * np.sin(self.tick * 0.05)))
        center_y = int(self.height * 0.5)
        cv2.circle(image, (center_x, center_y), self.radius, (0, 140, 255), -1)
        msg = self.bridge.cv2_to_imgmsg(image, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "synthetic_camera"
        self.publisher.publish(msg)
        self.tick += 1


def main() -> int:
    rclpy.init()
    node = SyntheticCameraNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

