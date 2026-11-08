import json
import sys
from pathlib import Path

THRESHOLDS = ((90, "brightgreen"), (80, "yellowgreen"), (70, "yellow"))


def badge(percent: float) -> dict[str, str | int]:
    """
    Build the shields.io endpoint badge for a coverage percentage.

    Args:
        percent (float): The total coverage, from 0 to 100.

    Returns:
        dict[str, str | int]: The endpoint mapping with the rounded percentage as message and the color of the threshold that percentage reaches.
    """
    shown = round(percent)
    color = next((color for minimum, color in THRESHOLDS if shown >= minimum), "red")
    return {"schemaVersion": 1, "label": "coverage", "message": f"{shown}%", "color": color}


def main() -> int:
    """
    Turn a coverage.py JSON report into a shields.io endpoint file.

    The first argument is the report written by `coverage json`, the second is the file to write.

    Returns:
        int: 0 once the file is written.
    """
    percent = json.loads(Path(sys.argv[1]).read_text())["totals"]["percent_covered"]
    Path(sys.argv[2]).write_text(json.dumps(badge(percent)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
