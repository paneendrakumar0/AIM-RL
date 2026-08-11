#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Capture one ROS image topic frame.")
    parser.add_argument("--topic", default="/camera/image_raw")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    rclpy.init()
    node = Node("aim_rl_image_capture")
    bridge = CvBridge()
    captured = False

    def receive(message: Image) -> None:
        nonlocal captured
        frame = bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
        if not cv2.imwrite(str(output), frame):
            raise RuntimeError(f"Failed to write image to {output}")
        captured = True

    subscription = node.create_subscription(
        Image,
        args.topic,
        receive,
        qos_profile_sensor_data,
    )
    deadline = time.monotonic() + args.timeout
    while not captured and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.25)

    publishers = node.get_publishers_info_by_topic(args.topic) if not captured else []
    node.destroy_node()
    del subscription
    rclpy.shutdown()
    if not captured:
        print(
            f"No image received on {args.topic} within {args.timeout:.1f}s; "
            f"publishers={len(publishers)}"
        )
        for publisher in publishers:
            print(
                f"  node={publisher.node_namespace}/{publisher.node_name} "
                f"reliability={publisher.qos_profile.reliability} "
                f"durability={publisher.qos_profile.durability}"
            )
        return 1

    print(f"Captured {args.topic} to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
