import cv2
import numpy as np

from aim_arm_perception.target_detector import TargetDetector


def main() -> int:
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.circle(image, (200, 120), 24, (0, 140, 255), -1)

    detector = TargetDetector(min_area=200.0)
    detection = detector.detect(image)
    if detection is None:
        raise RuntimeError("Expected synthetic orange target to be detected")

    px, py = detection.pixel_xy
    if abs(px - 200) > 3 or abs(py - 120) > 3:
        raise RuntimeError(f"Unexpected detection center: {(px, py)}")

    x, y, z = detection.workspace_xyz
    if not (0.25 < x < 0.35 and -0.05 < y < 0.15 and z == 0.05):
        raise RuntimeError(f"Unexpected workspace estimate: {detection.workspace_xyz}")

    print(
        "Perception smoke test passed: "
        f"pixel={detection.pixel_xy}, workspace={detection.workspace_xyz}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

