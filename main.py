#!/usr/bin/env python3
"""Place the finished front page where the grader expects it.

The picture itself is baked into this repository as entry.png
(build_image.py draws it). This entrypoint only copies that file
into the output directory the grader names, so the program needs
no network, no clock and no third-party package at run time.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    if not SOURCE.is_file():
        print("entry.png is missing; run build_image.py first",
              file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(SOURCE.read_bytes())
    print(f"entry.png ({target.stat().st_size} bytes) -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
