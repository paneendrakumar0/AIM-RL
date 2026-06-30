#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import math


REPO_ROOT = Path(__file__).resolve().parents[1]
MESH_DIR = REPO_ROOT / "colcon_ws" / "src" / "aim_arm_description" / "meshes" / "visual"


def normal(a, b, c):
    ux, uy, uz = (b[i] - a[i] for i in range(3))
    vx, vy, vz = (c[i] - a[i] for i in range(3))
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return (nx / length, ny / length, nz / length)


def write_ascii_stl(path: Path, name: str, triangles: Iterable[tuple[tuple[float, float, float], ...]]):
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"solid {name}\n")
        for tri in triangles:
            n = normal(*tri)
            handle.write(f"  facet normal {n[0]:.8f} {n[1]:.8f} {n[2]:.8f}\n")
            handle.write("    outer loop\n")
            for v in tri:
                handle.write(f"      vertex {v[0]:.8f} {v[1]:.8f} {v[2]:.8f}\n")
            handle.write("    endloop\n")
            handle.write("  endfacet\n")
        handle.write(f"endsolid {name}\n")


def rounded_link(length: float, root_radius: float, tip_radius: float, facets: int = 18):
    triangles = []
    root = []
    tip = []
    for i in range(facets):
        angle = 2.0 * math.pi * i / facets
        squash = 0.72 + 0.16 * math.cos(2 * angle)
        root.append((0.0, root_radius * math.cos(angle), root_radius * squash * math.sin(angle)))
        tip.append((length, tip_radius * math.cos(angle), tip_radius * squash * math.sin(angle)))

    root_center = (0.0, 0.0, 0.0)
    tip_center = (length, 0.0, 0.0)
    for i in range(facets):
        j = (i + 1) % facets
        triangles.append((root[i], tip[i], tip[j]))
        triangles.append((root[i], tip[j], root[j]))
        triangles.append((root_center, root[j], root[i]))
        triangles.append((tip_center, tip[i], tip[j]))
    return triangles


def cylinder(length: float, radius: float, facets: int = 32):
    triangles = []
    left = []
    right = []
    for i in range(facets):
        angle = 2.0 * math.pi * i / facets
        left.append((-length / 2.0, radius * math.cos(angle), radius * math.sin(angle)))
        right.append((length / 2.0, radius * math.cos(angle), radius * math.sin(angle)))
    left_center = (-length / 2.0, 0.0, 0.0)
    right_center = (length / 2.0, 0.0, 0.0)
    for i in range(facets):
        j = (i + 1) % facets
        triangles.append((left[i], right[i], right[j]))
        triangles.append((left[i], right[j], left[j]))
        triangles.append((left_center, left[j], left[i]))
        triangles.append((right_center, right[i], right[j]))
    return triangles


def tapered_tool(length: float = 0.16):
    return rounded_link(length, 0.045, 0.022, facets=16)


def main():
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    meshes = {
        "upper_arm_visual.stl": ("upper_arm_visual", rounded_link(0.42, 0.075, 0.060)),
        "forearm_visual.stl": ("forearm_visual", rounded_link(0.36, 0.060, 0.045)),
        "wrist_visual.stl": ("wrist_visual", cylinder(0.16, 0.050)),
        "tool_visual.stl": ("tool_visual", tapered_tool()),
        "joint_cap_visual.stl": ("joint_cap_visual", cylinder(0.11, 0.085)),
    }
    for filename, (name, triangles) in meshes.items():
        write_ascii_stl(MESH_DIR / filename, name, triangles)


if __name__ == "__main__":
    main()

