"""Liveness-slot assignment for model-specific static AOT graphs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class LiveInterval:
    """One internal buffer's lifetime in graph-dispatch indices, inclusive."""

    name: str
    dtype: str
    elements: int
    start: int
    end: int
    pinned: bool = False


@dataclass
class BufferSlot:
    index: int
    dtype: str
    elements: int
    members: List[str] = field(default_factory=list)
    end: int = -1


@dataclass(frozen=True)
class LivenessPlan:
    assignments: Dict[str, int]
    slots: Tuple[BufferSlot, ...]

    def validate(self, intervals: List[LiveInterval]) -> None:
        by_slot: Dict[int, List[LiveInterval]] = {}
        lookup = {interval.name: interval for interval in intervals}
        slot_lookup = {slot.index: slot for slot in self.slots}
        if len(slot_lookup) != len(self.slots):
            raise ValueError("liveness slot indices must be unique")
        expected = {item.name for item in intervals if not item.pinned}
        if set(self.assignments) != expected:
            raise ValueError("liveness assignments must cover every non-pinned interval")
        for name, slot in self.assignments.items():
            if name not in lookup:
                raise ValueError(f"liveness assignment references unknown interval {name!r}")
            if slot not in slot_lookup:
                raise ValueError(f"liveness assignment references unknown slot {slot}")
            interval = lookup[name]
            storage = slot_lookup[slot]
            if storage.dtype != interval.dtype:
                raise ValueError(f"liveness dtype mismatch for {name!r} in slot {slot}")
            if storage.elements < interval.elements:
                raise ValueError(f"liveness slot {slot} is too small for {name!r}")
            by_slot.setdefault(slot, []).append(lookup[name])
        for slot, members in by_slot.items():
            members.sort(key=lambda item: (item.start, item.end, item.name))
            for previous, current in zip(members, members[1:]):
                if previous.end >= current.start:
                    raise ValueError(
                        f"liveness overlap in slot {slot}: {previous.name} "
                        f"[{previous.start}, {previous.end}] and {current.name} "
                        f"[{current.start}, {current.end}]"
                    )


def assign_liveness_slots(intervals: List[LiveInterval]) -> LivenessPlan:
    """Reuse same-dtype slots only when the previous inclusive lifetime ended.

    Pinned values (inputs, constants, dummy storage and graph outputs) are
    intentionally excluded; callers expose those as dedicated graph arguments.
    """
    names = [item.name for item in intervals]
    if len(names) != len(set(names)):
        raise ValueError("liveness interval names must be unique")
    for item in intervals:
        if item.elements < 1 or item.start < 0 or item.end < item.start:
            raise ValueError(f"invalid liveness interval: {item}")

    assignments: Dict[str, int] = {}
    slots: List[BufferSlot] = []
    internal = sorted(
        (item for item in intervals if not item.pinned),
        key=lambda item: (item.start, -item.elements, item.name),
    )
    for item in internal:
        candidates = [
            slot for slot in slots
            if slot.dtype == item.dtype and slot.end < item.start
        ]
        if candidates:
            slot = min(candidates, key=lambda candidate: (candidate.elements, candidate.index))
            slot.elements = max(slot.elements, item.elements)
        else:
            slot = BufferSlot(len(slots), item.dtype, item.elements)
            slots.append(slot)
        slot.members.append(item.name)
        slot.end = item.end
        assignments[item.name] = slot.index

    plan = LivenessPlan(assignments, tuple(slots))
    plan.validate(intervals)
    return plan


__all__ = ["BufferSlot", "LiveInterval", "LivenessPlan", "assign_liveness_slots"]
