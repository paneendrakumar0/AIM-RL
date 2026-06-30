from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping


def append_metrics(path: str, row: Mapping[str, object]) -> None:
    metrics_path = Path(path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not metrics_path.exists()

    with metrics_path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

