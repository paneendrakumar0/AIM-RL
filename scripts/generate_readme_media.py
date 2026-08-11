#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = REPO_ROOT / "media" / "screenshots"
RECORDINGS = REPO_ROOT / "media" / "recordings"


PALETTE = {
    "ink": (26, 31, 38),
    "muted": (88, 99, 112),
    "paper": (246, 248, 250),
    "panel": (255, 255, 255),
    "line": (207, 217, 226),
    "blue": (24, 115, 185),
    "teal": (0, 143, 130),
    "orange": (235, 119, 36),
    "green": (51, 146, 85),
    "red": (200, 67, 67),
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def rounded_rect(draw: ImageDraw.ImageDraw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start, end, fill, width=4):
    draw.line([start, end], fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    angle = np.arctan2(ey - sy, ex - sx)
    length = 14
    for delta in (2.55, -2.55):
        ax = ex + length * np.cos(angle + delta)
        ay = ey + length * np.sin(angle + delta)
        draw.line([(ex, ey), (ax, ay)], fill=fill, width=width)


def save_architecture():
    img = Image.new("RGB", (1500, 900), PALETTE["paper"])
    d = ImageDraw.Draw(img)
    title = font(54, True)
    subtitle = font(24)
    h = font(26, True)
    body = font(19)

    d.text((70, 48), "AIM-RL Robotic Arm Stack", font=title, fill=PALETTE["ink"])
    d.text((72, 118), "Simulation-first ROS 2, perception, reinforcement learning, and serial hardware bridge", font=subtitle, fill=PALETTE["muted"])

    boxes = [
        ("Digital Twin", "URDF/Xacro\nGazebo world\nCamera + target", (80, 220, 390, 420), PALETTE["blue"]),
        ("Perception", "OpenCV tracker\n/camera/image_raw\n/aim_arm/target_pose", (455, 220, 765, 420), PALETTE["teal"]),
        ("Motion", "Geometric IK\nJointTrajectory\nMoveIt scaffold", (830, 220, 1140, 420), PALETTE["orange"]),
        ("Hardware", "Serial packets\nChecksum\nArduino parser", (1205, 220, 1435, 420), PALETTE["green"]),
        ("RL Brain", "Gym-style env\nPPO scaffold\nCheckpoint path", (455, 560, 765, 760), (95, 86, 181)),
        ("Validation", "Stack build\nGazebo smoke\nTopic-flow smoke", (830, 560, 1140, 760), (54, 122, 108)),
    ]

    for name, text, rect, color in boxes:
        rounded_rect(d, rect, 18, PALETTE["panel"], outline=PALETTE["line"], width=2)
        d.rectangle((rect[0], rect[1], rect[2], rect[1] + 12), fill=color)
        d.text((rect[0] + 24, rect[1] + 36), name, font=h, fill=PALETTE["ink"])
        d.multiline_text((rect[0] + 24, rect[1] + 84), text, font=body, fill=PALETTE["muted"], spacing=8)

    arrow(d, (390, 320), (455, 320), PALETTE["muted"])
    arrow(d, (765, 320), (830, 320), PALETTE["muted"])
    arrow(d, (1140, 320), (1205, 320), PALETTE["muted"])
    arrow(d, (610, 560), (610, 430), PALETTE["muted"])
    arrow(d, (830, 650), (765, 650), PALETTE["muted"])
    arrow(d, (985, 560), (985, 430), PALETTE["muted"])

    d.text((80, 820), "Current dry-run path: synthetic/Gazebo camera -> tracker -> IK trajectory -> serial packet dry-run", font=subtitle, fill=PALETTE["ink"])
    img.save(SCREENSHOTS / "architecture.png")


def save_gazebo_world():
    img = Image.new("RGB", (1500, 900), (238, 242, 245))
    d = ImageDraw.Draw(img)
    title = font(48, True)
    h = font(24, True)
    small = font(18)

    d.text((70, 48), "Gazebo Digital Twin World", font=title, fill=PALETTE["ink"])
    d.text((72, 110), "World contents generated from aim_empty.world: table, target block, overhead camera, robot spawn path", font=font(22), fill=PALETTE["muted"])

    table = (260, 290, 1240, 700)
    rounded_rect(d, table, 12, (118, 126, 135), outline=(78, 84, 92), width=3)
    d.text((292, 315), "workspace_table", font=h, fill=(255, 255, 255))

    robot_base = (430, 495)
    d.ellipse((robot_base[0] - 70, robot_base[1] - 70, robot_base[0] + 70, robot_base[1] + 70), fill=(33, 44, 54), outline=(18, 24, 32), width=3)
    joints = [(430, 495), (570, 440), (735, 500), (880, 450), (995, 490)]
    for a, b in zip(joints, joints[1:]):
        d.line([a, b], fill=PALETTE["blue"], width=26)
        d.line([a, b], fill=(40, 154, 209), width=12)
    for x, y in joints:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=(237, 241, 244), outline=(80, 88, 98), width=3)
    d.text((335, 585), "aim_arm", font=h, fill=(255, 255, 255))

    target = (1030, 410, 1090, 470)
    rounded_rect(d, target, 6, PALETTE["orange"], outline=(154, 72, 20), width=3)
    d.text((1004, 485), "target_block", font=small, fill=(255, 255, 255))

    cam = (690, 165)
    d.rectangle((cam[0] - 70, cam[1] - 32, cam[0] + 70, cam[1] + 32), fill=(36, 43, 52), outline=(0, 0, 0), width=3)
    d.ellipse((cam[0] - 22, cam[1] - 22, cam[0] + 22, cam[1] + 22), fill=(65, 98, 130), outline=(10, 20, 30), width=2)
    d.polygon([(650, 205), (730, 205), (1100, 710), (280, 710)], outline=PALETTE["teal"], fill=None)
    d.line([(650, 205), (280, 710)], fill=PALETTE["teal"], width=3)
    d.line([(730, 205), (1100, 710)], fill=PALETTE["teal"], width=3)
    d.text((595, 210), "overhead_camera", font=h, fill=PALETTE["ink"])

    d.text((80, 820), "Smoke-tested launch: /gazebo, /gazebo_ros_camera, /robot_state_publisher", font=font(22), fill=PALETTE["ink"])
    img.save(SCREENSHOTS / "gazebo_world_overview.png")


def save_perception():
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    image[:] = (36, 41, 47)
    cv2.rectangle(image, (60, 90), (580, 420), (120, 126, 132), -1)
    cv2.rectangle(image, (60, 90), (580, 420), (85, 90, 98), 3)
    center = (400, 242)
    cv2.circle(image, center, 42, (0, 140, 255), -1)
    cv2.circle(image, center, 48, (255, 255, 255), 3)
    cv2.line(image, (center[0] - 70, center[1]), (center[0] + 70, center[1]), (255, 255, 255), 2)
    cv2.line(image, (center[0], center[1] - 70), (center[0], center[1] + 70), (255, 255, 255), 2)
    cv2.putText(image, "OpenCV target detection", (32, 46), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (245, 248, 250), 2, cv2.LINE_AA)
    cv2.putText(image, "pixel=(400,242)  ->  /aim_arm/target_pose", (32, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (245, 248, 250), 2, cv2.LINE_AA)
    cv2.imwrite(str(SCREENSHOTS / "perception_detection.png"), image)


def command_output(command: list[str]) -> str:
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    lines = result.stdout.strip().splitlines()
    return "\n".join(lines[-26:])


def save_terminal_screenshot(name: str, title: str, text: str):
    img = Image.new("RGB", (1400, 820), (18, 24, 31))
    d = ImageDraw.Draw(img)
    mono = font(23)
    title_font = font(34, True)
    d.rectangle((0, 0, 1400, 70), fill=(34, 42, 52))
    d.ellipse((26, 26, 42, 42), fill=(240, 86, 86))
    d.ellipse((54, 26, 70, 42), fill=(242, 190, 70))
    d.ellipse((82, 26, 98, 42), fill=(85, 200, 110))
    d.text((125, 18), title, font=title_font, fill=(236, 241, 246))

    y = 105
    for line in text.splitlines()[:26]:
        color = (196, 214, 226)
        if "passed" in line.lower() or " ok " in line:
            color = (116, 218, 151)
        if "missing" in line:
            color = (245, 191, 98)
        if "failed" in line.lower() or "error" in line.lower():
            color = (245, 120, 120)
        d.text((48, y), line[:110], font=mono, fill=color)
        y += 26
    img.save(SCREENSHOTS / name)


def save_topic_flow_recording():
    frames = []
    mono = font(24)
    title = font(38, True)
    steps = [
        ("1. Synthetic Camera", "/camera/image_raw\norange block enters workspace", PALETTE["blue"], 0.30),
        ("2. OpenCV Tracker", "/aim_arm/target_pose\nframe_id: world", PALETTE["teal"], 0.45),
        ("3. Cartesian IK", "/arm_controller/joint_trajectory\n6 joint positions", PALETTE["orange"], 0.60),
        ("4. Serial Bridge", "$AIM,j0,j1,j2,j3,j4,j5*XX\nchecksum + dry-run", PALETTE["green"], 0.75),
    ]
    for idx in range(32):
        img = Image.new("RGB", (1200, 675), PALETTE["paper"])
        d = ImageDraw.Draw(img)
        d.text((52, 34), "AIM-RL Dry-Run Topic Flow", font=title, fill=PALETTE["ink"])
        d.text((54, 86), "The live smoke test verifies this path with ROS 2 topics.", font=font(22), fill=PALETTE["muted"])
        progress = min(1.0, idx / 24)
        centers = [(170, 350), (450, 350), (730, 350), (1010, 350)]
        for i, (label, detail, color, threshold) in enumerate(steps):
            active = progress >= threshold - 0.20
            fill = color if active else (220, 226, 232)
            outline = color if active else (185, 195, 205)
            x, y = centers[i]
            rounded_rect(d, (x - 120, y - 92, x + 120, y + 92), 18, (255, 255, 255), outline=outline, width=4)
            d.ellipse((x - 28, y - 76, x + 28, y - 20), fill=fill)
            d.text((x - 100, y - 5), label, font=font(22, True), fill=PALETTE["ink"])
            d.multiline_text((x - 100, y + 32), detail, font=font(18), fill=PALETTE["muted"], spacing=6)
            if i < len(centers) - 1:
                arrow_color = PALETTE["muted"] if progress > threshold else (196, 204, 212)
                arrow(d, (x + 130, y), (centers[i + 1][0] - 130, y), arrow_color, width=4)
        dot_x = 170 + int((1010 - 170) * progress)
        d.ellipse((dot_x - 12, 515 - 12, dot_x + 12, 515 + 12), fill=PALETTE["orange"])
        d.line((170, 515, 1010, 515), fill=PALETTE["line"], width=4)
        d.text((54, 600), "Verified by scripts/smoke_topic_flow.sh", font=mono, fill=PALETTE["ink"])
        frames.append(img)
    frames[0].save(
        RECORDINGS / "topic_flow.gif",
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
    )


def save_findings_summary():
    img = Image.new("RGB", (1500, 900), PALETTE["paper"])
    d = ImageDraw.Draw(img)
    d.text((70, 48), "Live Simulation Findings", font=font(52, True), fill=PALETTE["ink"])
    d.text(
        (72, 116),
        "ROS 2 Humble + Gazebo Classic + MoveIt 2 validation",
        font=font(24),
        fill=PALETTE["muted"],
    )

    findings = [
        (
            "Planning",
            "OMPL planned with two\nworkcell collision objects.",
            PALETTE["blue"],
            "PASS",
        ),
        (
            "Execution",
            "FollowJointTrajectory finished\nthrough arm_controller.",
            PALETTE["green"],
            "PASS",
        ),
        (
            "Simulation",
            "Gazebo published joint states;\ncamera topics are advertised.",
            PALETTE["orange"],
            "PARTIAL",
        ),
        (
            "Workspace",
            "Seven ROS packages built;\nsix controlled joints verified.",
            PALETTE["orange"],
            "PASS",
        ),
    ]

    for index, (name, detail, color, status) in enumerate(findings):
        column = index % 2
        row = index // 2
        x = 70 + column * 715
        y = 190 + row * 240
        rounded_rect(d, (x, y, x + 650, y + 195), 18, PALETTE["panel"], PALETTE["line"], 2)
        d.rectangle((x, y, x + 12, y + 195), fill=color)
        d.text((x + 36, y + 28), name, font=font(28, True), fill=PALETTE["ink"])
        d.multiline_text((x + 36, y + 78), detail, font=font(22), fill=PALETTE["muted"], spacing=7)
        rounded_rect(d, (x + 510, y + 25, x + 615, y + 67), 12, color)
        d.text((x + 529, y + 32), status, font=font(20, True), fill=(255, 255, 255))

    rounded_rect(d, (70, 700, 1430, 830), 18, (239, 244, 248), PALETTE["line"], 2)
    d.text((95, 723), "Recommended next", font=font(24, True), fill=PALETTE["ink"])
    d.text(
        (95, 770),
        "1  Add synchronous RL stepping    2  Measure planning quality    3  Require a real camera frame in CI",
        font=font(20),
        fill=PALETTE["muted"],
    )
    img.save(SCREENSHOTS / "moveit_validation_findings.png")


def main():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    RECORDINGS.mkdir(parents=True, exist_ok=True)
    save_architecture()
    save_gazebo_world()
    save_perception()
    save_topic_flow_recording()
    save_findings_summary()

    validation_text = command_output(["./scripts/validate_stack.sh"])
    save_terminal_screenshot("validation_pass.png", "./scripts/validate_stack.sh", validation_text)

    audit_text = command_output(["./scripts/audit_dependencies.sh"])
    save_terminal_screenshot("dependency_audit.png", "./scripts/audit_dependencies.sh", audit_text)


if __name__ == "__main__":
    main()

