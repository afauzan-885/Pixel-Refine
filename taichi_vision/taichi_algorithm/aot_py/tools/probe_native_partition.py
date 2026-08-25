"""Reproducible native full-frame versus block-partition probe.

Run from the repository root, for example:

    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition --backend cpu
    $env:PIXEL_REFINE_AOT_ARCH='vulkan'; $env:AOT_ARCH='vulkan'; $env:AOT_DEVICE='0'; $env:TARGET_VENDOR='intel'; python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition --backend vulkan --device 0
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition --backend opengl --device 0
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition --backend cuda --device 0

The process selects one backend before importing the AOT facade.  Output is a
single JSON record suitable for attaching to the native partition evidence
registry; it reports the actual runtime name and device rather than assuming a
Vulkan ordinal identifies a vendor.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable, Mapping
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


# Support both ``python -m ...probe_native_partition`` and the documented
# direct file invocation.  The latter otherwise sets ``sys.path[0]`` to the
# tools directory and cannot import the repository package.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _cuda_device_name(device: int) -> str:
    """Resolve a CUDA ordinal to the driver-reported physical device name.

    The bridge currently exposes an empty runtime name for CUDA, so a probe
    must query the installed NVIDIA driver before its result can be attached
    to exact-device evidence.  Failure is deliberately represented as an
    empty string; callers then keep the result diagnostic-only instead of
    inventing a vendor or model.
    """

    try:
        ordinal = int(device)
    except (TypeError, ValueError):
        return ""
    if ordinal < 0:
        return ""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                f"--id={ordinal}",
                "--query-gpu=name",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()),
        "",
    )


# Keep the default probe compatible with the evidence command recorded in
# ``native_evidence.py``.  The stencil/local tranche is opt-in through
# ``--operations all`` (or an explicit comma-separated list), so extending
# this diagnostic cannot silently turn an existing CI/evidence command into a
# much longer or riskier run.
BASE_OPERATIONS = (
    "copy",
    "absdiff",
    "rgb2gray",
    "split_3ch",
    "merge_3ch",
    "extract_channel",
    "insert_channel",
    "cvtColor",
)
OPTIONAL_OPERATIONS = (
    "box_filter",
    "gaussian_blur",
    "median_filter",
    "sobel",
    "laplacian",
    "highlight_recovery",
    "smooth_flow_gpu",
    # Extended local/stencil wrappers with maintained _run_blockwise paths.
    "morphology",
    "filter2d",
    "threshold",
    "normalize",
    "joint_bilateral_guidance",
    "enhance_image",
    "joint_bilateral_filter",
    "guided_filter",
    "non_local_means",
)
GLOBAL_DIAGNOSTIC_OPERATIONS = ("otsu_threshold",)
ALL_OPERATIONS = BASE_OPERATIONS + OPTIONAL_OPERATIONS + GLOBAL_DIAGNOSTIC_OPERATIONS
DEFAULT_OPERATIONS = BASE_OPERATIONS

# Tolerances are intentionally explicit and operation-specific.  The local
# wrappers use float32 AOT graphs; tiled reductions can therefore differ by a
# few ulps even when the same backend/artifact is used.  Integer/data-movement
# operations remain exact requirements.
OPERATION_TOLERANCES = {
    **{name: 0.0 for name in BASE_OPERATIONS},
    "otsu_threshold": 0.0,
    "box_filter": 2e-5,
    "gaussian_blur": 5e-5,
    "median_filter": 0.0,
    "sobel": 2e-5,
    "laplacian": 2e-5,
    "highlight_recovery": 1e-4,
    "smooth_flow_gpu": 5e-5,
    "morphology": 2e-5,
    "filter2d": 2e-5,
    "threshold": 0.0,
    "normalize": 2e-5,
    "joint_bilateral_guidance": 2e-5,
    "enhance_image": 2e-5,
    "joint_bilateral_filter": 2e-5,
    "guided_filter": 2e-5,
    "non_local_means": 2e-5,
}


def _validate_runtime_selection(runtime: Any, backend: str, device: int) -> None:
    """Fail closed when the already-created runtime is not the probe target.

    Importing ``taichi_algorithm`` can create the process-wide AOT singleton
    before :func:`run` gets a chance to set its environment.  In that case a
    requested Vulkan probe could otherwise execute against an OpenGL context
    and produce plausible, but invalid, evidence.  The probe must never
    relabel that result as the requested backend.
    """

    aliases = {
        "vk": "vulkan",
        "gl": "opengl",
        "egl": "opengl",
        "opengl_es": "gles",
        "opengl_es3": "gles",
    }
    expected_backend = aliases.get(str(backend).strip().lower(), str(backend).strip().lower())
    actual_backend = str(getattr(runtime, "arch", "")).strip().lower()
    actual_backend = aliases.get(actual_backend, actual_backend)
    try:
        expected_device = int(device)
    except (TypeError, ValueError):
        expected_device = 0
    try:
        actual_device = int(getattr(runtime, "device_id", 0))
    except (TypeError, ValueError):
        actual_device = -1

    # Desktop OpenGL/GLES expose one logical device through the process-wide
    # context; their ordinal is intentionally not compared with a Vulkan/CUDA
    # ordinal.  All other backends are ordinal-qualified evidence.
    device_mismatch = expected_backend not in {"opengl", "gles"} and actual_device != expected_device
    if actual_backend != expected_backend or device_mismatch:
        raise RuntimeError(
            "Native probe backend mismatch: requested "
            f"{expected_backend!r} device {expected_device}, but the active "
            f"runtime is {actual_backend or 'unknown'!r} device {actual_device}. "
            "Set PIXEL_REFINE_AOT_ARCH (and AOT_ARCH/AOT_DEVICE) before importing "
            "taichi_algorithm, then start a fresh Python process."
        )


def _parse_operations(spec: str | Iterable[str] | None) -> tuple[str, ...]:
    """Normalize a probe operation selection without importing the AOT API.

    ``base`` (also the default), ``all``, or a comma-separated list are
    accepted.  Duplicate names are removed while preserving canonical order
    from the user's selection.  Unknown names fail before backend/runtime
    initialization so a typo can never accidentally run a different graph.
    """

    if spec is None:
        return DEFAULT_OPERATIONS
    if isinstance(spec, str):
        text = spec.strip()
        if not text or text.lower() in {"base", "default"}:
            return DEFAULT_OPERATIONS
        if text.lower() == "all":
            return ALL_OPERATIONS
        names = [part.strip() for part in text.split(",") if part.strip()]
    else:
        names = [str(part).strip() for part in spec if str(part).strip()]
        if not names:
            return DEFAULT_OPERATIONS

    unknown = [name for name in names if name not in ALL_OPERATIONS]
    if unknown:
        raise ValueError(
            "unknown probe operation(s): "
            + ", ".join(sorted(set(unknown)))
            + "; choose from "
            + ", ".join(ALL_OPERATIONS)
        )
    selected = []
    for name in names:
        if name not in selected:
            selected.append(name)
    return tuple(selected)


def _as_values(value: Any) -> tuple[np.ndarray, ...]:
    if isinstance(value, (tuple, list)):
        return tuple(np.asarray(item) for item in value)
    return (np.asarray(value),)


def _max_error(first: Any, second: Any) -> float:
    values_a = _as_values(first)
    values_b = _as_values(second)
    if len(values_a) != len(values_b):
        return float("inf")
    errors = []
    for left, right in zip(values_a, values_b):
        if left.shape != right.shape:
            return float("inf")
        if left.size:
            errors.append(
                float(
                    np.max(
                        np.abs(
                            left.astype(np.float64, copy=False)
                            - right.astype(np.float64, copy=False)
                        )
                    )
                )
            )
        else:
            errors.append(0.0)
    return max(errors, default=0.0)


def _telemetry_snapshot(engine: Any) -> dict[str, Any]:
    """Return a JSON-safe copy of the last block dispatch telemetry."""

    getter = getattr(engine, "get_last_block_execution", None)
    if not callable(getter):
        return {}
    try:
        value = getter()
    except Exception:
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _block_plan_snapshot(engine: Any) -> dict[str, Any]:
    """Expose the planner decision used by a wrapper, when available."""

    local = getattr(engine, "_local", None)
    value = getattr(local, "last_block_plan", None)
    return dict(value) if isinstance(value, Mapping) else {}


def _reset_telemetry(engine: Any) -> None:
    setter = getattr(engine, "set_last_block_execution", None)
    if callable(setter):
        try:
            setter({})
        except Exception:
            pass


def _operation_inputs(rng: np.random.Generator) -> dict[str, Any]:
    """Build small deterministic fixtures for all probe operation families."""

    rgb = rng.integers(0, 256, size=(19, 23, 3), dtype=np.uint8)
    first = rng.random((19, 23), dtype=np.float32)
    second = rng.random((19, 23), dtype=np.float32)
    # Keep the stencil inputs float32 so the native AOT graphs are exercised
    # instead of their documented dtype/reference fallbacks.
    gray = rng.random((19, 23), dtype=np.float32)
    highlight = (rng.random((19, 23, 3), dtype=np.float32) * 1.5).astype(
        np.float32, copy=False
    )
    flow = rng.normal(0.0, 0.25, size=(19, 23, 2)).astype(np.float32)
    guide = rng.random((19, 23), dtype=np.float32)
    blur = rng.random((19, 23), dtype=np.float32)
    lut = np.linspace(0.0, 1.0, 256, dtype=np.float32)
    return {
        "rgb": rgb,
        "first": first,
        "second": second,
        "gray": gray,
        "highlight": highlight,
        "flow": flow,
        "guide": guide,
        "blur": blur,
        "lut": lut,
    }


def _invoke_operation(aot: Any, name: str, data: Mapping[str, Any]) -> Any:
    """Invoke one canonical wrapper with a signature known to be stable."""

    if name == "copy":
        return aot.copy(data["rgb"])
    if name == "absdiff":
        return aot.absdiff(data["first"], data["second"])
    if name == "rgb2gray":
        return aot.rgb2gray(data["rgb"])
    if name == "split_3ch":
        return tuple(aot.split_3ch(data["rgb"]))
    if name == "merge_3ch":
        rgb = data["rgb"]
        return aot.merge_3ch(*[rgb[..., index] for index in range(3)])
    if name == "extract_channel":
        return aot.extract_channel(data["rgb"], 1)
    if name == "insert_channel":
        destination = data["rgb"].copy()
        return aot.insert_channel(data["rgb"][..., 1], destination, 1).copy()
    if name == "cvtColor":
        return aot.cvtColor(data["rgb"], aot.COLOR_RGB2GRAY)
    if name == "otsu_threshold":
        return aot.otsu_threshold_aot(data["first"], max_val=255.0, return_gpu=False)
    if name == "box_filter":
        return aot.box_filter(data["gray"], kernel_size=3, return_gpu=False)
    if name == "gaussian_blur":
        return aot.gaussian_blur(
            data["gray"], sigma=1.0, kernel_size=3, return_gpu=False
        )
    if name == "median_filter":
        return aot.median_filter(data["gray"], return_gpu=False)
    if name == "sobel":
        return tuple(aot.sobel(data["gray"], return_gpu=False))
    if name == "laplacian":
        return aot.laplacian(data["gray"], return_gpu=False)
    if name == "highlight_recovery":
        return aot.highlight_recovery(
            data["highlight"],
            wb_r=1.05,
            wb_g=1.0,
            wb_b=0.95,
            strength=0.8,
            return_gpu=False,
        )
    if name == "smooth_flow_gpu":
        return aot.smooth_flow_gpu(data["flow"], sigma=1.0, kernel_size=3)
    if name == "morphology":
        return aot.dilate_aot(data["gray"], ksize=3, iterations=1)
    if name == "filter2d":
        return aot.filter2d_aot(
            data["gray"],
            np.asarray(
                [[0.0, 1.0, 0.0], [1.0, 4.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float32
            )
            / 8.0,
        )
    if name == "threshold":
        _threshold, result = aot.threshold_aot(
            data["gray"], thresh=0.5, maxval=1.0, thresh_type="BINARY"
        )
        return result
    if name == "normalize":
        return aot.normalize_aot(data["gray"], alpha=0.0, beta=1.0, norm_type="MINMAX")
    if name == "joint_bilateral_guidance":
        return aot.joint_bilateral_guidance_aot(
            data["gray"], data["guide"], preset="medium", radius=1
        )
    if name == "enhance_image":
        return aot.enhance_image_aot(
            data["gray"],
            data["blur"],
            data["lut"],
            micro_contrast=1.2,
            clarity=0.2,
            noise_coring=0.05,
        )
    if name == "joint_bilateral_filter":
        return aot.joint_bilateral_filter(
            data["gray"], data["guide"], preset="medium", radius=1
        )
    if name == "guided_filter":
        return aot.guided_filter_aot(
            data["guide"], data["gray"], radius=1, epsilon=1.0e-4
        )
    if name == "non_local_means":
        return aot.non_local_means(
            data["gray"],
            h_param=10.0,
            search_window=3,
            patch_size=1,
            refinement_strength=1.0,
            shrinkage_strength=1.0,
        )
    raise ValueError(f"unsupported probe operation {name!r}")


def _quarantine_flag(*telemetry: Mapping[str, Any]) -> bool:
    for record in telemetry:
        if not record:
            continue
        if str(record.get("status", "")).lower() == "quarantined":
            return True
        if "quarantin" in str(record.get("error", "")).lower():
            return True
        if "quarantin" in str(record.get("reason", "")).lower():
            return True
    return False


_PLAN_OPERATION_ALIASES = {
    "smooth_flow_gpu": "smooth_flow",
}


def _block_selected(
    operation: str,
    plan: Mapping[str, Any],
    telemetry: Mapping[str, Any],
) -> bool:
    """Require telemetry/planner ownership by the requested operation.

    Some wrappers invoke a nested local helper (for example Otsu may copy its
    source).  A selected ``copy`` plan is not evidence that the outer global
    reduction was partitioned, so operation names must match (with only the
    documented smooth-flow alias accepted).
    """

    expected = _PLAN_OPERATION_ALIASES.get(operation, operation)
    planned = str(plan.get("operation", ""))
    observed = str(telemetry.get("operation", ""))
    if planned == expected and bool(plan.get("selected")):
        return True
    if observed == expected:
        return bool(telemetry.get("block_count", 0)) and str(
            telemetry.get("mode", "")
        ).lower() not in {"", "full_frame"}
    return False


def _operation_record(
    name: str,
    full: Any,
    tiled: Any,
    *,
    full_telemetry: Mapping[str, Any],
    block_telemetry: Mapping[str, Any],
    full_plan: Mapping[str, Any],
    block_plan: Mapping[str, Any],
    error: str | None = None,
    phase: str | None = None,
) -> dict[str, Any]:
    tolerance = float(OPERATION_TOLERANCES.get(name, 0.0))
    selected = _block_selected(name, block_plan, block_telemetry)
    quarantined = _quarantine_flag(full_telemetry, block_telemetry, block_plan)
    full_values: tuple[np.ndarray, ...] = ()
    tiled_values: tuple[np.ndarray, ...] = ()
    output_arity_match = False
    output_shapes_match = False
    output_dtypes_match = False
    if full is None or tiled is None:
        max_error = float("inf")
        parity_passed = False
    else:
        full_values = _as_values(full)
        tiled_values = _as_values(tiled)
        output_arity_match = len(full_values) == len(tiled_values)
        output_shapes_match = bool(
            output_arity_match
            and all(
                left.shape == right.shape
                for left, right in zip(full_values, tiled_values)
            )
        )
        # Numerical error is computed after conversion to float64, so a
        # float32/full versus float64/block result could otherwise pass while
        # violating the native graph's output ABI.  Dtype parity is therefore
        # a first-class promotion gate, not merely diagnostic metadata.
        output_dtypes_match = bool(
            output_arity_match
            and all(
                left.dtype == right.dtype
                for left, right in zip(full_values, tiled_values)
            )
        )
        max_error = _max_error(full, tiled)
        parity_passed = bool(
            max_error <= tolerance
            and output_arity_match
            and output_shapes_match
            and output_dtypes_match
        )
    output_contract_match = bool(
        output_arity_match and output_shapes_match and output_dtypes_match
    )
    native_status = str(block_telemetry.get("status", ""))
    if selected and native_status in {"", "ok"} and not quarantined:
        fallback = "none"
    elif quarantined:
        fallback = "quarantined"
    elif selected:
        fallback = str(block_telemetry.get("mode", "unknown"))
    else:
        fallback = "full_frame"
    supported = bool(
        selected
        and not quarantined
        and native_status in {"", "ok"}
        and output_contract_match
    )
    record: dict[str, Any] = {
        "max_abs_error": max_error,
        "tolerance": tolerance,
        "parity_passed": parity_passed,
        # Separate numerical/ABI correctness from native block qualification.
        # A supported same-backend full-frame fallback can be correct without
        # being evidence that the operation is partitionable.
        "correctness_passed": parity_passed,
        "output_contract_match": output_contract_match,
        "output_arity_match": output_arity_match,
        "output_shapes_match": output_shapes_match,
        "output_dtypes_match": output_dtypes_match,
        # ``passed`` deliberately includes native block selection.  An exact
        # result produced by a full-frame fallback is useful evidence of
        # correctness but must not be reported as block support.
        "passed": bool(parity_passed and supported),
        "supported": supported,
        "block_selected": selected,
        "fallback": fallback,
        "quarantined": quarantined,
        "full_telemetry": dict(full_telemetry),
        "block_telemetry": dict(block_telemetry),
        "full_plan": dict(full_plan),
        "block_plan": dict(block_plan),
    }
    # Keep the operation's output contract explicit on both sides of the
    # comparison.  ``engine`` telemetry describes dispatch only; it does not
    # describe Python tuple arity.  In particular, split_3ch can use a
    # host-tile path with no block telemetry, so relying on telemetry alone
    # would make a successful three-output run look like an opaque scalar.
    # These fields are intentionally diagnostic and do not promote a native
    # operation by themselves; promotion still requires the normal strict
    # evidence gate.
    if full is not None:
        full_values = _as_values(full)
        record["dtype"] = [str(value.dtype) for value in full_values]
        record["shape"] = [list(value.shape) for value in full_values]
        record["expected_output_arity"] = len(full_values)
        record["expected_output_shapes"] = [
            list(value.shape) for value in full_values
        ]
        record["expected_output_dtypes"] = [
            str(value.dtype) for value in full_values
        ]
    # Keep the diagnostic explicit for tuple-returning wrappers.  The engine
    # telemetry intentionally describes dispatch, not Python return arity, so
    # recording both sides here prevents a multi-output operation from being
    # mistaken for a scalar result merely because its block telemetry is
    # empty (as is the case for the host-tile split path).
    if tiled is not None:
        tiled_values = _as_values(tiled)
        record["output_arity"] = len(tiled_values)
        record["output_shapes"] = [list(value.shape) for value in tiled_values]
        record["output_dtypes"] = [str(value.dtype) for value in tiled_values]
        # Backward-compatible aliases retained for consumers of earlier probe
        # JSON reports.
        record["block_output_arity"] = len(tiled_values)
        record["block_output_shapes"] = [list(value.shape) for value in tiled_values]
        record["block_output_dtypes"] = [str(value.dtype) for value in tiled_values]
    elif full is not None:
        # A failed block invocation still exposes the expected tuple contract
        # without claiming that a block result was produced.  Do not add
        # ``output_*`` here: those keys mean that a block result was observed.
        pass
    if error is not None:
        record["supported"] = False
        record["passed"] = False
        record["error"] = str(error)[:512]
        if phase:
            record["error_phase"] = str(phase)
        record["reason"] = str(error)[:512]
    elif quarantined:
        record["reason"] = (
            "native block operation was quarantined; same-backend fallback retained"
        )
    elif not selected:
        record["reason"] = (
            "block path was not selected; same-backend full-frame fallback"
        )
    elif not output_contract_match:
        record["reason"] = (
            "block output contract mismatch (arity, shape, or dtype); "
            "native promotion rejected"
        )
    return record


def run(
    backend: str,
    device: int,
    block_size: int,
    operations: str | Iterable[str] | None = None,
) -> dict[str, Any]:
    selected_operations = _parse_operations(operations)
    os.environ["BACKEND"] = str(backend)
    os.environ["AOT_ARCH"] = str(backend)
    os.environ["AOT_DEVICE"] = str(int(device))
    os.environ.setdefault("TARGET_VENDOR", "nvidia")

    # Import only after backend selection variables are set.
    from taichi_vision.taichi_algorithm import aot_api as aot
    from taichi_vision.taichi_aot import engine
    _validate_runtime_selection(engine, backend, device)

    rng = np.random.default_rng(1234)
    data = _operation_inputs(rng)
    operations_result: dict[str, Any] = {}

    # ``adaptive_memory=False`` makes the full pass a genuine full-frame
    # baseline.  The block pass then explicitly selects the requested grid;
    # no pressure-triggered planner decision is mixed into the comparison.
    aot.set_block_mode(enabled=False, threshold_bytes=1, adaptive_memory=False)
    for name in selected_operations:
        full_value = None
        tiled_value = None
        full_telemetry: Mapping[str, Any] = {}
        block_telemetry: Mapping[str, Any] = {}
        full_plan: Mapping[str, Any] = {}
        block_plan: Mapping[str, Any] = {}
        try:
            # Restore the explicit full-frame baseline after the previous
            # operation's block pass.
            aot.set_block_mode(enabled=False, threshold_bytes=1, adaptive_memory=False)
            _reset_telemetry(engine)
            full_value = _invoke_operation(aot, name, data)
            full_telemetry = _telemetry_snapshot(engine)
            full_plan = _block_plan_snapshot(engine)
        except (AttributeError, TypeError, ValueError, NotImplementedError) as exc:
            operations_result[name] = _operation_record(
                name,
                None,
                None,
                full_telemetry=full_telemetry,
                block_telemetry=block_telemetry,
                full_plan=full_plan,
                block_plan=block_plan,
                error=str(exc),
                phase="full",
            )
            continue
        except Exception as exc:
            operations_result[name] = _operation_record(
                name,
                None,
                None,
                full_telemetry=full_telemetry,
                block_telemetry=block_telemetry,
                full_plan=full_plan,
                block_plan=block_plan,
                error=str(exc),
                phase="full",
            )
            continue

        try:
            aot.clear_block_quarantine(name)
            aot.set_block_mode(
                enabled=True,
                size=int(block_size),
                threshold_bytes=1,
                cache_entries=4,
                cache_bytes=4 * 1024 * 1024,
                adaptive_memory=False,
                device_cache_enabled=False,
            )
            _reset_telemetry(engine)
            tiled_value = _invoke_operation(aot, name, data)
            block_telemetry = _telemetry_snapshot(engine)
            block_plan = _block_plan_snapshot(engine)
        except (AttributeError, TypeError, ValueError, NotImplementedError) as exc:
            block_telemetry = _telemetry_snapshot(engine)
            block_plan = _block_plan_snapshot(engine)
            operations_result[name] = _operation_record(
                name,
                full_value,
                None,
                full_telemetry=full_telemetry,
                block_telemetry=block_telemetry,
                full_plan=full_plan,
                block_plan=block_plan,
                error=str(exc),
                phase="block",
            )
            continue
        except Exception as exc:
            block_telemetry = _telemetry_snapshot(engine)
            block_plan = _block_plan_snapshot(engine)
            operations_result[name] = _operation_record(
                name,
                full_value,
                None,
                full_telemetry=full_telemetry,
                block_telemetry=block_telemetry,
                full_plan=full_plan,
                block_plan=block_plan,
                error=str(exc),
                phase="block",
            )
            continue

        operations_result[name] = _operation_record(
            name,
            full_value,
            tiled_value,
            full_telemetry=full_telemetry,
            block_telemetry=block_telemetry,
            full_plan=full_plan,
            block_plan=block_plan,
        )

    runtime_device_name = str(
        getattr(engine, "gpu_name", "") or getattr(engine, "device_name", "")
    )
    if not runtime_device_name and str(getattr(engine, "arch", backend)).lower() == "cuda":
        runtime_device_name = _cuda_device_name(device)
    # Capture identity metadata when the runtime exposes it.  Missing driver
    # details remain valid diagnostics, but the evidence registry can now
    # distinguish legacy name-only records from reproducible target identity.
    runtime_target_id = str(getattr(engine, "target_id", "") or "").strip() or None
    runtime_architecture = (
        str(getattr(engine, "architecture", "") or "").strip() or None
    )
    runtime_driver = (
        str(
            getattr(engine, "driver_version", "")
            or getattr(engine, "driver", "")
            or ""
        ).strip()
        or None
    )
    runtime_vendor = (
        str(
            getattr(engine, "vendor", "")
            or getattr(engine, "vendor_name", "")
            or ""
        ).strip()
        or None
    )
    return {
        "backend": str(getattr(engine, "arch", backend)),
        "runtime_backend": str(getattr(engine, "arch", backend)),
        "device_id": int(getattr(engine, "device_id", device) or device),
        "device_name": runtime_device_name,
        "target_id": runtime_target_id,
        "architecture": runtime_architecture,
        "driver_version": runtime_driver,
        "vendor": runtime_vendor,
        "block_size": int(block_size),
        "requested_operations": list(selected_operations),
        "operations": operations_result,
        "all_passed": bool(
            operations_result
            and all(item["passed"] for item in operations_result.values())
        ),
        "all_correct": bool(
            operations_result
            and all(item.get("correctness_passed", False) for item in operations_result.values())
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # OpenGL is intentionally included as a diagnostic target even though it
    # has one serialized context/queue and therefore never implies overlap.
    # The actual renderer/device identity is still read from the initialized
    # engine; callers may set TARGET_VENDOR for Intel vs NVIDIA.
    parser.add_argument(
        "--backend", choices=("cpu", "cuda", "vulkan", "opengl"), required=True
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--block-size", type=int, default=7)
    parser.add_argument(
        "--operations",
        default="base",
        help=(
            "base (default), all, or a comma-separated operation list; "
            "available: " + ", ".join(ALL_OPERATIONS)
        ),
    )
    args = parser.parse_args()
    try:
        selected = _parse_operations(args.operations)
    except ValueError as exc:
        parser.error(str(exc))
    print(
        json.dumps(
            run(args.backend, args.device, args.block_size, selected),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
