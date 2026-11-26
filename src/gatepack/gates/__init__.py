"""Gate registry. Adding a gate = one module in this folder + one line in GATE_MODULES."""
from __future__ import annotations

from importlib import import_module

from ..core import Gate

GATE_MODULES = (
    "kdp_metadata",
    "kdp_cover_safezone",
    "kdp_pagecount",
    "epub",
    "dead_air",
    "freeze",
    "loudness",
    "tail",
    "subtitles",
)


def all_gates() -> dict[str, Gate]:
    gates = {}
    for name in GATE_MODULES:
        gate = import_module(f"{__name__}.{name}").GATE
        if gate.id in gates:
            raise RuntimeError(f"duplicate gate id {gate.id}")
        gates[gate.id] = gate
    return gates


def get(gate_id: str) -> Gate:
    gates = all_gates()
    if gate_id not in gates:
        raise KeyError(gate_id)
    return gates[gate_id]
