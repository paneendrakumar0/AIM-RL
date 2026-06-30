from __future__ import annotations

import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import Image

from aim_arm_perception.target_detector import TargetDetector


class TargetTrackerNode(Node):
    def __init__(self) -> None:
        super().__init__("target_tracker_node")
        self.image_topic = self.declare_parameter(
            "image_topic", "/camera/image_raw"
        ).value
        self.target_topic = self.declare_parameter(
            "target_topic", "/aim_arm/target_pose"
        ).value
        self.frame_id = self.declare_parameter("frame_id", "world").value
        self.bridge = CvBridge()
        self.detector = TargetDetector()
        self.publisher = self.create_publisher(PoseStamped, self.target_topic, 10)
        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.handle_image,
            10,
        )
        self.get_logger().info(
            f"Tracking target from {self.image_topic} and publishing {self.target_topic}"
        )

    def handle_image(self, msg: Image) -> None:
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        detection = self.detector.detect(image)
        if detection is None:
            return

        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.frame_id
        pose.pose.position.x = detection.workspace_xyz[0]
        pose.pose.position.y = detection.workspace_xyz[1]
        pose.pose.position.z = detection.workspace_xyz[2]
        pose.pose.orientation.w = 1.0
        self.publisher.publish(pose)


def main() -> int:
    rclpy.init()
    node = TargetTrackerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

