"""High-level backend decision manager.

This layer is intentionally side-effect free: compilation and runtime probes
can call it repeatedly while the public algorithm API remains unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import tempfile
from .capabilities import backend_candidates, classify_device


@dataclass
class BackendDecision:
    selected: str
    candidates: list[str]
    device: str
    reason: str


class BackendManager:
    def __init__(self, device="unknown", validated=None):
        self.device = device
        self.validated = dict(validated) if validated is not None else self._load_runtime_status()

    @staticmethod
    def _load_runtime_status():
        root = os.environ.get("PIXEL_REFINE_AOT_CACHE", os.path.join(tempfile.gettempdir(), "pixel_refine_aot_cache"))
        result = {}
        for backend in ("cpu", "vulkan", "opengl"):
            try:
                with open(os.path.join(root, f"runtime_{backend}.json"), encoding="utf-8") as f:
                    result[backend] = json.load(f).get("status", "unknown")
            except (OSError, ValueError, TypeError):
                pass
        return result

    def decide(self, requested="auto"):
        requested = (requested or "auto").lower()
        candidates = [requested] if requested != "auto" else backend_candidates(self.device)
        rejected = []
        for backend in candidates:
            status = self.validated.get(backend, "unknown")
            caps = classify_device(self.device, backend)
            if status in ("quarantined", "unsupported") or not caps.safe:
                rejected.append(f"{backend}: {caps.reason or status}")
                continue
            return BackendDecision(backend, candidates, self.device,
                                   "selected after capability/status filtering")
        return BackendDecision("cpu", candidates, self.device,
                               "all candidates rejected: " + "; ".join(rejected))

    def run_with_fallback(self, operation, requested="auto"):
        """Run an operation against isolated backend contexts.

        ``operation(backend)`` must create/upload resources for that backend;
        this prevents accidental reuse of native buffers across contexts.
        Returns ``(result, backend, errors)``.
        """
        decision = self.decide(requested)
        errors = {}
        for backend in decision.candidates:
            if self.validated.get(backend) in ("quarantined", "unsupported"):
                continue
            try:
                return operation(backend), backend, errors
            except Exception as exc:
                errors[backend] = f"{type(exc).__name__}: {exc}"
        if "cpu" not in errors and decision.selected != "cpu":
            try:
                return operation("cpu"), "cpu", errors
            except Exception as exc:
                errors["cpu"] = f"{type(exc).__name__}: {exc}"
        raise RuntimeError(f"All backend candidates failed: {errors}")


def preflight_backend(device="unknown", requested="auto", validated=None):
    """Choose one backend before native buffers and graph resources exist.

    This is intentionally side-effect free.  A wrapper should use the
    returned decision to construct its engine and buffers as one context;
    fallback must never switch contexts midway through an active graph.
    """
    return BackendManager(device=device, validated=validated).decide(requested)
