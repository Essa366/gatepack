"""Render docs/demo.svg from real gatepack runs on the test fixtures.

The SVG shows the exact text the commands print; nothing is edited by hand.
Run it again after changing a gate's output:

    pip install -e ".[cover]" rich
    python scripts/make_demo_svg.py

Needs ffmpeg on PATH (the loudness command).
"""

from __future__ import annotations

import io
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
OUT = ROOT / "docs" / "demo.svg"

COMMANDS = [
    "gatepack check kdp-metadata kdp-metadata/fail/trademark_and_working_note.json",
    "gatepack check kdp-cover-safezone kdp-cover-safezone/fail/paperback_spine_text_60_pages.png --trim 6x9 --pages 60",
    "gatepack check loudness loudness/pass/tone_minus14_lufs.flac",
]

# Long "rule sources" and "measured" lines are real output, but they make the image too wide to read
# on a phone. They are dropped from the picture only; the README states this under the image.
SKIP_PREFIXES = ("  rule sources:", "    - ", "  measured:")


def run(command: str) -> tuple[str, int]:
    argv = shlex.split(command)
    argv = [sys.executable, "-m", "gatepack", *argv[1:]]
    proc = subprocess.run(argv, cwd=FIXTURES, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode == 2:
        sys.exit(f"'{command}' could not run (exit 2):\n{proc.stdout}{proc.stderr}")
    lines = [ln for ln in proc.stdout.splitlines() if not ln.startswith(SKIP_PREFIXES)]
    return "\n".join(lines), proc.returncode


def main() -> int:
    try:
        from rich.console import Console
        from rich.text import Text
    except ImportError:
        sys.exit("This script needs rich: pip install rich")

    console = Console(
        record=True, width=120, file=io.StringIO(), force_terminal=True, color_system="truecolor"
    )
    for i, command in enumerate(COMMANDS):
        output, code = run(command)
        if i:
            console.print()
        console.print(Text("$ ", style="bold #8b949e") + Text(command, style="bold #79c0ff"))
        console.print(Text(output))
        console.print(Text(f"# exit code {code}", style="#8b949e"))
    OUT.write_text(console.export_svg(title="gatepack"), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
