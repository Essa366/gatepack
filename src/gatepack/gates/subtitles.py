"""Local timing and readability checks for UTF-8 SRT and WebVTT files."""
import re
from pathlib import Path

from ..core import Finding, Gate, GateError, Option, Source

SPEC = Source("W3C WebVTT cue timings", "https://www.w3.org/TR/webvtt1/#webvtt-cue-timings")


def milliseconds(token, vtt):
    hours = r"(?:(\d{2,}):)?" if vtt else r"(\d{2,}):"
    separator = r"\." if vtt else ","
    match = re.fullmatch(hours + r"([0-5]\d):([0-5]\d)" + separator + r"(\d{3})", token, re.ASCII)
    if not match:
        raise ValueError("invalid timestamp")
    h, m, s, ms = (int(part or 0) for part in match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def is_vtt_header(block):
    signature, *metadata = block.split("\n")
    if "-->" in block or not re.fullmatch(r"WEBVTT(?:[ \t].*)?", signature):
        return False
    return all(re.fullmatch(r"(?:Kind:|Language:|X-TIMESTAMP-MAP=)[ \t]*\S.*", line)
               for line in metadata)


def check(path, overlaps="allow", max_line_length=0):
    path = Path(path)
    if path.suffix.lower() not in {".srt", ".vtt"}:
        raise GateError("expected a .srt or .vtt file")
    if max_line_length < 0 or overlaps not in {"allow", "reject"}:
        raise GateError("invalid subtitle quality policy")
    vtt = path.suffix.lower() == ".vtt"
    basis = "standard" if vtt else "heuristic"
    text = path.read_text(encoding="utf-8-sig").rstrip("\n")
    separator = r"\n{2,}" if vtt else r"\n[ \t]*\n+"
    blocks = re.split(separator, text) if text else []
    findings = []
    if vtt:
        if blocks and is_vtt_header(blocks[0]):
            blocks.pop(0)
        else:
            findings.append(Finding("FAIL", "header", "Expected WEBVTT followed by a blank line.", basis))
    count = 0
    last_start = latest_end = -1
    for block in blocks:
        lines = block.split("\n")
        if vtt:
            # NOTE always opens a comment; STYLE and REGION may also be cue identifiers.
            marker = lines[0].rstrip(" \t")
            if re.match(r"NOTE(?:[ \t]|$)", lines[0]) or (
                    marker in {"STYLE", "REGION"} and not any("-->" in line for line in lines[:2])):
                if "-->" in block:
                    findings.append(Finding("FAIL", "separator",
                                            "Insert a blank line between the WebVTT block and the next cue.", basis))
                continue
        count += 1
        if (vtt and "-->" not in lines[0]) or (not vtt and lines[0].isascii() and lines[0].isdigit()):
            lines = lines[1:]
        elif not vtt:
            findings.append(Finding("FAIL", "index", f"Cue {count}: expected a numeric SRT index.", basis))
        timing = lines[0] if lines else ""
        fields = re.split(r"[ \t]+", timing.strip(" \t")) if vtt else timing.split()
        try:
            if len(fields) < 3 or fields[1] != "-->":
                raise ValueError
            start = milliseconds(fields[0], vtt)
            end = milliseconds(fields[2], vtt)
        except ValueError:
            findings.append(Finding("FAIL", "timing", f"Cue {count}: invalid timing line.", basis))
            continue
        if end <= start:
            findings.append(Finding("FAIL", "duration", f"Cue {count}: end must be after start.", basis))
        if start < last_start:
            findings.append(Finding("FAIL", "order", f"Cue {count}: start times must be ordered.", basis))
        if overlaps == "reject" and start < latest_end:
            findings.append(Finding("FAIL", "overlap", f"Cue {count} overlaps an earlier cue.", "heuristic"))
        last_start, latest_end = start, max(latest_end, end)
        for line in lines[1:]:
            if re.match(r"^[ \t]*[0-9]{2,}:[0-9]{2}(?::[0-9]{2})?[.,][0-9]{3}[ \t]+-->[ \t]+[0-9]+:", line):
                findings.append(Finding("FAIL", "separator",
                                        f"Cue {count}: insert a blank line before the next cue.", basis))
            if max_line_length and len(line) > max_line_length:
                findings.append(Finding("WARN", "line-length", f"Cue {count}: {len(line)} characters exceeds {max_line_length}."))
    if not count:
        findings.append(Finding("WARN", "empty", "No subtitle cues found."))
    return findings, {"cues": count}


GATE = Gate(
    id="subtitles", title="Subtitle timing", category="video",
    summary="Check local SRT and WebVTT cue timing and optional readability limits.",
    sources=(SPEC,), check=check,
    options=(Option("overlaps", str, "allow", "policy for overlapping cues", ("allow", "reject")),
             Option("max_line_length", int, 0, "warn above this many source characters per line (0 disables)")),
)
