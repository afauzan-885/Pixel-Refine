"""Backend-neutral style values shared by the PySide6 and Flet adapters."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def _freeze_map(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for key, item in (value or {}).items():
        if isinstance(item, Mapping):
            item = _freeze_map(item)
        result[key] = item
    return MappingProxyType(result)


@dataclass(frozen=True)
class StyleSpec:
    """Immutable style descriptor with stable ``base``, ``states`` and ``parts``."""

    kind: str
    base: Mapping[str, Any]
    states: Mapping[str, Mapping[str, Any]]
    parts: Mapping[str, Mapping[str, Any]]

    def __post_init__(self) -> None:
        object.__setattr__(self, "base", _freeze_map(self.base))
        object.__setattr__(self, "states", _freeze_map(self.states))
        object.__setattr__(self, "parts", _freeze_map(self.parts))

    def with_overrides(self, **values: Any) -> "StyleSpec":
        """Return a copy with backend-neutral base values replaced or added."""
        return StyleSpec(
            self.kind,
            {**self.base, **values},
            self.states,
            self.parts,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly snapshot suitable for cross-backend tests."""
        return {
            "kind": self.kind,
            "base": dict(self.base),
            "states": {name: dict(values) for name, values in self.states.items()},
            "parts": {name: dict(values) for name, values in self.parts.items()},
        }
