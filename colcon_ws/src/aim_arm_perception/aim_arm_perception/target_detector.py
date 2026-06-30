from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class Detection:
    pixel_xy: Tuple[int, int]
    workspace_xyz: Tuple[float, float, float]
    area: float


class TargetDetector:
    def __init__(
        self,
        hsv_lower: Tuple[int, int, int] = (5, 80, 80),
        hsv_upper: Tuple[int, int, int] = (25, 255, 255),
        min_area: float = 100.0,
        workspace_width_m: float = 0.80,
        workspace_depth_m: float = 0.60,
        workspace_z_m: float = 0.05,
    ) -> None:
        self.hsv_lower = np.array(hsv_lower, dtype=np.uint8)
        self.hsv_upper = np.array(hsv_upper, dtype=np.uint8)
        self.min_area = min_area
        self.workspace_width_m = workspace_width_m
        self.workspace_depth_m = workspace_depth_m
        self.workspace_z_m = workspace_z_m

    def detect(self, bgr_image: np.ndarray) -> Optional[Detection]:
        if bgr_image.ndim != 3 or bgr_image.shape[2] != 3:
            raise ValueError("Expected BGR image with shape HxWx3")

        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        mask = cv2.medianBlur(mask, 5)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        if area < self.min_area:
            return None

        moments = cv2.moments(contour)
        if moments["m00"] == 0.0:
            return None

        pixel_x = int(moments["m10"] / moments["m00"])
        pixel_y = int(moments["m01"] / moments["m00"])
        workspace_xyz = self.pixel_to_workspace(
            pixel_x,
            pixel_y,
            bgr_image.shape[1],
            bgr_image.shape[0],
        )
        return Detection(
            pixel_xy=(pixel_x, pixel_y),
            workspace_xyz=workspace_xyz,
            area=area,
        )

    def pixel_to_workspace(
        self,
        pixel_x: int,
        pixel_y: int,
        image_width: int,
        image_height: int,
    ) -> Tuple[float, float, float]:
        x = (pixel_y / max(image_height - 1, 1)) * self.workspace_depth_m
        y = ((pixel_x / max(image_width - 1, 1)) - 0.5) * self.workspace_width_m
        return (float(x), float(y), self.workspace_z_m)

