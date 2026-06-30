from setuptools import find_packages, setup

package_name = "aim_arm_perception"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools", "numpy"],
    zip_safe=True,
    maintainer="Paneendra Kumar",
    maintainer_email="paneendrakumar0@example.com",
    description="OpenCV target tracking for AIM-RL.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "target_tracker_node = aim_arm_perception.target_tracker_node:main",
            "perception_smoke_test = aim_arm_perception.smoke_test:main",
        ],
    },
)

