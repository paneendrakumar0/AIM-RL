from setuptools import find_packages, setup

package_name = "aim_arm_rl"

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
    description="RL environment bridge for the AIM-RL manipulator.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "rl_smoke_test = aim_arm_rl.smoke_test:main",
            "train_ppo = aim_arm_rl.train_ppo:main",
        ],
    },
)
