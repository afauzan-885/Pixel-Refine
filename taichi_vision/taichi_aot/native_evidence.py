"""Device-specific evidence for native full-frame versus block parity.

Compilation, semantic NumPy parity, and execution on a real backend are
different claims.  This registry records only the last one.  Every record is
keyed by canonical operation, backend, and observed device identity; a
Vulkan NVIDIA result therefore cannot silently qualify Intel Vulkan, OpenGL,
CUDA, or another driver.

The registry is diagnostic data only.  Registering evidence never mutates
``AUTO_BLOCK_SAFE`` or the operation contract table and never changes runtime
dispatch by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numbers
import threading
from typing import Any, Mapping, Optional, Sequence

from .block import canonical_operation_name


# Only this scope proves the contract consumed by the opt-in native
# full-frame-versus-block promotion gate.  Other ``native_*`` scopes may be
# useful diagnostics, but must not be treated as partition qualification.
NATIVE_PARTITION_SCOPE = "native_full_frame_vs_block"


@dataclass(frozen=True)
class NativePartitionEvidence:
    """One observed native parity result for one backend/device."""

    operation: str
    backend: str
    device: str
    command: str
    passed: bool = True
    max_abs_error: float = 0.0
    tolerance: float = 0.0
    interpolations: tuple[str, ...] = ("linear",)
    block_size: Any = None
    shape: Any = None
    dtype: Any = None
    device_id: Optional[int] = None
    scope: str = "native_full_frame_vs_block"
    source: str = "command_probe"
    note: str = ""
    # Optional target identity captured by the probe.  These fields are
    # deliberately appended so older positional construction remains valid.
    target_id: Optional[str] = None
    architecture: Optional[str] = None
    driver_version: Optional[str] = None
    vendor: Optional[str] = None

    def __post_init__(self) -> None:
        operation = canonical_operation_name(self.operation)
        backend = str(self.backend or "").strip().lower()
        device = str(self.device or "").strip()
        command = str(self.command or "").strip()
        if not operation:
            raise ValueError("native evidence operation must not be empty")
        if not backend:
            raise ValueError("native evidence backend must not be empty")
        if not device:
            raise ValueError("native evidence device must not be empty")
        if not command:
            raise ValueError("native evidence command must not be empty")
        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "backend", backend)
        object.__setattr__(self, "device", device)
        object.__setattr__(self, "command", command)
        # Probe payloads often arrive through JSON, where a malformed
        # ``passed`` value such as ``"false"`` is truthy in Python.  Never
        # allow that to qualify native evidence accidentally.  Preserve the
        # historical bool/int inputs, while accepting the conventional JSON
        # spellings and rejecting everything else fail-closed.
        raw_passed = self.passed
        if isinstance(raw_passed, bool):
            passed = raw_passed
        elif isinstance(raw_passed, numbers.Integral) and int(raw_passed) in (0, 1):
            passed = bool(int(raw_passed))
        elif isinstance(raw_passed, str):
            normalized_passed = raw_passed.strip().casefold()
            if normalized_passed in {"true", "1"}:
                passed = True
            elif normalized_passed in {"false", "0"}:
                passed = False
            else:
                raise ValueError(
                    "native evidence passed must be a boolean or JSON boolean string"
                )
        else:
            raise ValueError(
                "native evidence passed must be a boolean or JSON boolean string"
            )
        object.__setattr__(self, "passed", passed)
        max_abs_error = float(self.max_abs_error)
        # An error metric is a magnitude.  Negative values cannot come from
        # the probe's absolute-difference calculation and must not qualify a
        # record merely because ``-1 <= tolerance``.  Rejecting them at the
        # evidence boundary keeps malformed reports fail-closed.
        if max_abs_error < 0.0 or not math.isfinite(max_abs_error):
            raise ValueError(
                "native evidence max_abs_error must be finite and non-negative"
            )
        object.__setattr__(self, "max_abs_error", max_abs_error)
        tolerance = float(self.tolerance)
        if tolerance < 0.0 or not math.isfinite(tolerance):
            raise ValueError("native evidence tolerance must be finite and non-negative")
        object.__setattr__(self, "tolerance", tolerance)
        raw_interpolations = self.interpolations
        # Accept a single interpolation name from JSON/config callers without
        # splitting it into characters (``"linear"`` -> ``("linear",)``).
        # Keep the existing iterable form backward compatible.
        if isinstance(raw_interpolations, str):
            raw_interpolations = (raw_interpolations,)
        interpolation_values = tuple(
            str(value).strip().lower()
            for value in (raw_interpolations or ())
            if str(value).strip()
        )
        object.__setattr__(self, "interpolations", interpolation_values)
        object.__setattr__(
            self, "scope", str(self.scope or "native_full_frame_vs_block")
        )
        object.__setattr__(self, "source", str(self.source or "command_probe"))
        object.__setattr__(self, "note", str(self.note or ""))
        if self.device_id is not None:
            # An ordinal is part of the observed device identity.  Avoid
            # permissive ``int()`` coercion (True -> 1, 1.5 -> 1) which could
            # make malformed probe metadata look like exact-device evidence.
            value = self.device_id
            if isinstance(value, bool):
                raise ValueError(
                    "native evidence device_id must be a non-negative integer"
                )
            if isinstance(value, numbers.Integral):
                ordinal = int(value)
            elif isinstance(value, numbers.Real):
                numeric = float(value)
                if not math.isfinite(numeric) or not numeric.is_integer():
                    raise ValueError(
                        "native evidence device_id must be a non-negative integer"
                    )
                ordinal = int(numeric)
            elif isinstance(value, str):
                try:
                    ordinal = int(value.strip(), 10)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        "native evidence device_id must be a non-negative integer"
                    ) from exc
            else:
                raise ValueError(
                    "native evidence device_id must be a non-negative integer"
                )
            if ordinal < 0:
                raise ValueError(
                    "native evidence device_id must be a non-negative integer"
                )
            object.__setattr__(self, "device_id", ordinal)
        for field_name in ("target_id", "architecture", "driver_version", "vendor"):
            value = getattr(self, field_name)
            if value is not None:
                value = str(value).strip()
                object.__setattr__(self, field_name, value or None)

    @property
    def qualified(self) -> bool:
        """Whether the recorded command passed without a numerical error."""

        return bool(
            self.passed
            and math.isfinite(self.max_abs_error)
            and self.max_abs_error <= self.tolerance
        )

    @property
    def native_runtime(self) -> bool:
        """Whether the scope explicitly describes a native device run."""

        return self.scope.startswith("native_")

    @property
    def partition_qualified(self) -> bool:
        """Whether this record can satisfy the strict partition gate.

        ``native_runtime`` intentionally remains broad for reporting legacy
        native scopes.  Promotion is narrower: it requires the canonical
        full-frame-versus-block evidence scope and a positive block size.
        This prevents a semantic/native pipeline diagnostic from silently
        qualifying automatic block dispatch.
        """

        if not self.qualified or self.scope != NATIVE_PARTITION_SCOPE:
            return False
        # A block size is a discrete launch/layout parameter.  ``int(value)``
        # alone is too permissive here: ``True`` becomes 1 and ``8.75``
        # becomes 8, allowing malformed probe metadata to qualify native
        # promotion.  Accept integral values (including NumPy integer
        # scalars) and legacy decimal strings, but reject booleans,
        # fractional/non-finite numbers, and arbitrary objects.
        value = self.block_size
        if isinstance(value, bool):
            return False
        if isinstance(value, numbers.Integral):
            return int(value) > 0
        if isinstance(value, numbers.Real):
            numeric = float(value)
            return math.isfinite(numeric) and numeric.is_integer() and numeric > 0.0
        if isinstance(value, str):
            try:
                return int(value.strip(), 10) > 0
            except (TypeError, ValueError):
                return False
        return False

    @property
    def identity_complete(self) -> bool:
        """Whether the record carries a reproducible target identity.

        Legacy records intentionally remain valid for their historical exact
        device scope.  New evidence can opt into this stronger identity by
        providing target, architecture, driver, and vendor metadata.  Probe
        registration additionally verifies that a vendor-qualified target ID
        agrees with the runtime vendor before the record enters the registry.
        """

        return all(
            getattr(self, field_name)
            for field_name in ("target_id", "architecture", "driver_version", "vendor")
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "backend": self.backend,
            "device": self.device,
            "device_id": self.device_id,
            "target_id": self.target_id,
            "architecture": self.architecture,
            "driver_version": self.driver_version,
            "vendor": self.vendor,
            "identity_complete": self.identity_complete,
            "command": self.command,
            "passed": self.passed,
            "qualified": self.qualified,
            "partition_qualified": self.partition_qualified,
            "native_runtime": self.native_runtime,
            "max_abs_error": self.max_abs_error,
            "tolerance": self.tolerance,
            "interpolations": self.interpolations,
            "block_size": self.block_size,
            "shape": self.shape,
            "dtype": self.dtype,
            "scope": self.scope,
            "source": self.source,
            "note": self.note,
        }


_NATIVE_EVIDENCE: dict[tuple[str, str, str], NativePartitionEvidence] = {}
_NATIVE_EVIDENCE_LOCK = threading.RLock()


def _canonical_vendor(value: object) -> str:
    """Normalize the vendor spellings used by graphics/CPU probes.

    Target IDs are release identities (for example
    ``vulkan_x86_64_windows_nvidia``), while runtime probes commonly report
    marketing strings such as ``NVIDIA Corporation`` or ``Intel(R)``.  Keep
    this comparison conservative and small: unknown vendors are retained as
    normalized text rather than guessed into a known family.
    """

    text = str(value or "").strip().casefold()
    if not text:
        return ""
    compact = "".join(character for character in text if character.isalnum())
    aliases = {
        "nvidia": "nvidia",
        "nvidiacorporation": "nvidia",
        "intel": "intel",
        "intelcorporation": "intel",
        "intelr": "intel",
        "amd": "amd",
        "advancedmicrodevices": "amd",
        "advancedmicrodevicesinc": "amd",
        "qualcomm": "qualcomm",
        "arm": "arm",
        "armlimited": "arm",
    }
    normalized = aliases.get(compact)
    if normalized:
        return normalized
    # Driver APIs sometimes append a product/legal suffix (for example
    # ``NVIDIA GeForce`` or ``Intel(R) Corporation``).  Recognize only the
    # known vendor tokens; unknown strings remain unknown and fail closed.
    if "nvidia" in compact:
        return "nvidia"
    if "intel" in compact:
        return "intel"
    if "advancedmicrodevices" in compact or compact.startswith("amd"):
        return "amd"
    if "qualcomm" in compact:
        return "qualcomm"
    if compact.startswith("arm"):
        return "arm"
    return compact


def _coerce_probe_bool(value: object, field_name: str) -> bool:
    """Decode a JSON-like probe flag without Python truthiness traps.

    Probe payloads are commonly loaded from JSON, where ``"false"`` is a
    string.  Calling ``bool("false")`` would incorrectly select a block or
    qualify a failed operation.  Keep the accepted spellings aligned with
    :class:`NativePartitionEvidence` and reject every ambiguous value before
    any record is inserted into the process-local registry.
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, numbers.Integral) and int(value) in (0, 1):
        return bool(int(value))
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "1"}:
            return True
        if normalized in {"false", "0"}:
            return False
    raise ValueError(
        f"native probe {field_name} must be a boolean or JSON boolean string"
    )


def _coerce_probe_metric(value: object, field_name: str) -> float:
    """Decode a finite non-negative probe metric before registry mutation."""

    # Do not let ``float(True)`` or a non-finite JSON number reach the
    # evidence constructor.  More importantly, validating this while the
    # complete operation payload is still staged prevents an invalid later
    # operation from leaving earlier records in the process-local registry.
    if isinstance(value, bool):
        raise ValueError(f"native probe {field_name} must be finite and non-negative")
    try:
        metric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"native probe {field_name} must be finite and non-negative"
        ) from exc
    if not math.isfinite(metric) or metric < 0.0:
        raise ValueError(f"native probe {field_name} must be finite and non-negative")
    return metric


def _validate_probe_target_vendor(
    target_id: object,
    backend: str,
    vendor: object,
) -> None:
    """Reject a target/device vendor mismatch before recording evidence.

    A target suffix is authoritative only when it names a known vendor.  A
    generic target (for example ``vulkan_arm64_android``) remains valid for
    any vendor and is still scoped by its backend and observed device name.
    Vendor-qualified targets, however, must carry matching runtime metadata;
    accepting a missing or contradictory vendor would make an exact-device
    result unsafe for packaging promotion.
    """

    target_text = str(target_id or "").strip().casefold()
    if not target_text:
        raise ValueError("native probe target_id must not be empty")
    parts = target_text.split("_")
    target_backend = parts[0] if parts else ""
    if target_backend != backend:
        # ``opengl`` is the canonical desktop backend; GLES has its own
        # target family and must not be silently conflated with desktop GL.
        raise ValueError(
            "native probe target identity mismatch: "
            f"backend {backend!r}, target_id {target_id!r}"
        )
    known_vendors = {"nvidia", "intel", "amd", "qualcomm", "arm"}
    target_vendor = next(
        (part for part in reversed(parts) if part in known_vendors),
        "",
    )
    if not target_vendor:
        return
    actual_vendor = _canonical_vendor(vendor)
    if not actual_vendor or actual_vendor != target_vendor:
        raise ValueError(
            "native probe target vendor mismatch: target_id "
            f"{target_id!r} requires {target_vendor!r}, runtime reported "
            f"{vendor!r}"
        )


def register_native_partition_evidence(
    evidence: NativePartitionEvidence | Mapping[str, Any] | None = None,
    *,
    operation: Optional[str] = None,
    backend: Optional[str] = None,
    device: Optional[str] = None,
    command: Optional[str] = None,
    passed: bool = True,
    max_abs_error: float = 0.0,
    tolerance: float = 0.0,
    interpolations: tuple[str, ...] = ("linear",),
    block_size: Any = None,
    shape: Any = None,
    dtype: Any = None,
    device_id: Optional[int] = None,
    target_id: Optional[str] = None,
    architecture: Optional[str] = None,
    driver_version: Optional[str] = None,
    vendor: Optional[str] = None,
    scope: str = "native_full_frame_vs_block",
    source: str = "command_probe",
    note: str = "",
    replace: bool = True,
) -> NativePartitionEvidence:
    """Register one explicit command-backed native evidence record."""

    if isinstance(evidence, NativePartitionEvidence):
        if any(value is not None for value in (operation, backend, device, command)):
            raise TypeError("evidence object cannot be combined with identity fields")
        record = evidence
    else:
        fields = {
            "passed": passed,
            "max_abs_error": max_abs_error,
            "tolerance": tolerance,
            "interpolations": interpolations,
            "block_size": block_size,
            "shape": shape,
            "dtype": dtype,
            "device_id": device_id,
            "target_id": target_id,
            "architecture": architecture,
            "driver_version": driver_version,
            "vendor": vendor,
            "scope": scope,
            "source": source,
            "note": note,
        }
        if isinstance(evidence, Mapping):
            values = dict(evidence)
            operation = values.pop("operation", operation)
            backend = values.pop("backend", backend)
            device = values.pop("device", device)
            command = values.pop("command", command)
            for name in tuple(fields):
                if name in values:
                    fields[name] = values.pop(name)
            if values:
                raise TypeError(f"unknown native evidence fields: {sorted(values)}")
        record = NativePartitionEvidence(
            operation=operation or "",
            backend=backend or "",
            device=device or "",
            command=command or "",
            **fields,
        )
    key = (record.operation, record.backend, record.device)
    with _NATIVE_EVIDENCE_LOCK:
        if not replace and key in _NATIVE_EVIDENCE:
            raise KeyError(f"native evidence already registered: {key}")
        _NATIVE_EVIDENCE[key] = record
    return record


def lookup_native_partition_evidence(
    operation: str,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> tuple[NativePartitionEvidence, ...]:
    """Return exact operation/backend/device records without wildcarding."""

    canonical = canonical_operation_name(operation)
    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    with _NATIVE_EVIDENCE_LOCK:
        records = tuple(
            record
            for record in _NATIVE_EVIDENCE.values()
            if record.operation == canonical
            and (backend_name is None or record.backend == backend_name)
            and (device_name is None or record.device == device_name)
        )
    return tuple(sorted(records, key=lambda item: (item.backend, item.device)))


get_native_partition_evidence = lookup_native_partition_evidence


def native_partition_evidence_supported(
    operation: str,
    backend: str,
    device: Optional[str] = None,
    interpolation: Optional[str] = None,
) -> bool:
    """Return true only for a passed, exact backend/device native record.

    ``interpolation`` is an optional specialization gate for operations such
    as ``resize``.  Existing callers that do not provide it retain the prior
    operation-level behavior; callers that do provide it cannot accidentally
    treat a record qualified only for another interpolation as native.
    """

    interpolation_name = (
        None
        if interpolation is None
        else str(interpolation).strip().lower()
    )
    if interpolation is not None and not interpolation_name:
        return False

    return any(
        record.partition_qualified
        and (
            interpolation_name is None
            or interpolation_name in record.interpolations
        )
        for record in lookup_native_partition_evidence(operation, backend, device)
    )


def native_partition_promotion_report(
    backend: str,
    device: str,
    operations: Optional[Sequence[str] | str] = None,
    *,
    target_id: Optional[str] = None,
) -> dict[str, Any]:
    """Review exact-device evidence for a *read-only* native promotion.

    This is deliberately stricter than :func:`native_partition_evidence_supported`.
    The latter answers whether one operation has a matching partition record;
    this review answers whether a complete, explicitly identified set of
    records is safe to hand to a packaging/qualification reviewer.  It never
    mutates the registry, operation contracts, or dispatch flags.

    Promotion requires every requested operation to have exactly one record
    for the supplied backend and device, canonical full-frame-vs-block scope,
    a positive block size, passing parity, and complete target identity
    metadata.  If ``target_id`` is omitted, all records must still carry the
    same non-empty target identity.  This prevents a record from one target
    directory or driver from being treated as evidence for another target.
    """

    backend_name = str(backend or "").strip().lower()
    device_name = str(device or "").strip()
    if not backend_name or not device_name:
        raise ValueError("native promotion review requires backend and exact device")

    if operations is None:
        requested = tuple(
            sorted(
                {
                    record.operation
                    for record in native_partition_evidence_snapshot().values()
                    if record.backend == backend_name and record.device == device_name
                }
            )
        )
    elif isinstance(operations, str):
        requested = (canonical_operation_name(operations),)
    else:
        requested = tuple(
            dict.fromkeys(canonical_operation_name(value) for value in operations)
        )
    requested = tuple(operation for operation in requested if operation)

    expected_target = None if target_id is None else str(target_id).strip()
    reasons: list[str] = []
    accepted: list[NativePartitionEvidence] = []
    rejected: list[dict[str, Any]] = []
    missing: list[str] = []
    observed_target_ids: set[str] = set()

    for operation in requested:
        records = lookup_native_partition_evidence(
            operation, backend_name, device_name
        )
        if not records:
            missing.append(operation)
            continue
        if len(records) != 1:
            reason = f"{operation}: duplicate exact-device evidence records"
            reasons.append(reason)
            rejected.append({"operation": operation, "reasons": [reason]})
            continue
        record = records[0]
        record_reasons: list[str] = []
        if not record.native_runtime:
            record_reasons.append("record scope is not native")
        if not record.qualified:
            record_reasons.append("native parity is not qualified")
        if not record.partition_qualified:
            record_reasons.append("record is not partition_qualified")
        if not record.identity_complete:
            record_reasons.append("target identity metadata is incomplete")
        record_target = str(record.target_id or "").strip()
        if record_target:
            observed_target_ids.add(record_target)
            try:
                _validate_probe_target_vendor(
                    record_target, backend_name, record.vendor
                )
            except ValueError as exc:
                record_reasons.append(str(exc))
        if expected_target and record_target != expected_target:
            record_reasons.append(
                f"target_id {record_target!r} does not match expected "
                f"{expected_target!r}"
            )
        if record_reasons:
            reasons.extend(record_reasons)
            rejected.append(
                {
                    "operation": operation,
                    "target_id": record.target_id,
                    "reasons": record_reasons,
                    "record": record.as_dict(),
                }
            )
        else:
            accepted.append(record)

    if len(observed_target_ids) > 1:
        reasons.append("exact-device records contain multiple target identities")
    if not expected_target and not observed_target_ids and requested:
        reasons.append("no target identity is available for promotion")
    if missing:
        reasons.extend(f"missing exact-device evidence: {operation}" for operation in missing)
    eligible = bool(requested) and not reasons and len(accepted) == len(requested)
    return {
        "scope": "native_full_frame_vs_block_promotion_review",
        "backend": backend_name,
        "device": device_name,
        "target_id": expected_target
        if expected_target is not None
        else (next(iter(observed_target_ids)) if len(observed_target_ids) == 1 else None),
        "requested_operations": requested,
        "accepted_operations": tuple(record.operation for record in accepted),
        "accepted_count": len(accepted),
        "missing_operations": tuple(missing),
        "missing_count": len(missing),
        "rejected": tuple(rejected),
        "rejected_count": len(rejected),
        "promotion_eligible": bool(eligible),
        "status": "promotion_eligible" if eligible else "fail_closed",
        # Review metadata must never be consumed as a dispatch signal.
        "automatic_safe": False,
        "dispatch_promotion": False,
        "registry_mutated": False,
        "reasons": tuple(reasons),
    }


def native_partition_promotion_matrix_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    target_id_by_scope: Optional[Mapping[tuple[str, str], str]] = None,
) -> dict[str, Any]:
    """Return deterministic promotion reviews for every observed device scope.

    ``native_partition_promotion_report`` intentionally reviews one exact
    backend/device pair.  Release and qualification tooling also needs a
    compact *matrix* view, however, so that a qualified NVIDIA OpenGL result
    cannot be mistaken for Intel OpenGL (or another backend).  This helper
    enumerates the registry without mutating it, invokes the strict exact
    scope review, and returns scopes in sorted ``(backend, device)`` order.

    ``target_id_by_scope`` is optional and keyed by the same two-tuple used in
    the report.  It lets callers require a target identity for each scope
    without making target IDs global.  Unknown keys are ignored; missing keys
    retain the exact-review behavior (all records must agree on one identity).
    The result is diagnostic only and must never be used as a dispatch flag.
    """

    target_map: Mapping[tuple[str, str], str] = target_id_by_scope or {}
    with _NATIVE_EVIDENCE_LOCK:
        scopes = sorted(
            {
                (record.backend, record.device)
                for record in _NATIVE_EVIDENCE.values()
            },
            key=lambda item: (item[0], item[1]),
        )

    reports: list[dict[str, Any]] = []
    for backend_name, device_name in scopes:
        expected_target = target_map.get((backend_name, device_name))
        reports.append(
            native_partition_promotion_report(
                backend_name,
                device_name,
                operations,
                target_id=expected_target,
            )
        )

    eligible_scopes = tuple(
        (report["backend"], report["device"])
        for report in reports
        if report["promotion_eligible"]
    )
    rejected_scopes = tuple(
        (report["backend"], report["device"])
        for report in reports
        if not report["promotion_eligible"]
    )
    backend_names = sorted({report["backend"] for report in reports})
    backend_summary = {
        backend_name: {
            "scope_count": sum(
                report["backend"] == backend_name for report in reports
            ),
            "eligible_scope_count": sum(
                report["backend"] == backend_name
                and report["promotion_eligible"]
                for report in reports
            ),
            "rejected_scope_count": sum(
                report["backend"] == backend_name
                and not report["promotion_eligible"]
                for report in reports
            ),
            "scopes": tuple(
                (report["backend"], report["device"])
                for report in reports
                if report["backend"] == backend_name
            ),
        }
        for backend_name in backend_names
    }
    return {
        "scope": "native_full_frame_vs_block_promotion_matrix",
        "scope_count": len(reports),
        "promotion_eligible_count": len(eligible_scopes),
        "promotion_rejected_count": len(rejected_scopes),
        # An empty evidence registry is not a successful (zero-work) review.
        # Expose the aggregate gate explicitly so release tooling cannot
        # mistake ``scope_count == 0`` for complete native coverage.  This is
        # diagnostic only, like the per-scope promotion result below.
        "status": (
            "promotion_eligible"
            if reports and not rejected_scopes
            else "fail_closed"
        ),
        "fail_closed": bool(not reports or rejected_scopes),
        "eligible_scopes": eligible_scopes,
        "rejected_scopes": rejected_scopes,
        "backend_summary": backend_summary,
        "reports": tuple(reports),
        # Matrix reviews are evidence for humans/tooling only; they never
        # promote dispatch or mutate the registry.
        "automatic_safe": False,
        "dispatch_promotion": False,
        "registry_mutated": False,
    }


# Long-form alias for callers that prefer the evidence-oriented name.
native_partition_evidence_promotion_report = native_partition_promotion_report


def native_partition_evidence_report(
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Return auditable counts and records for an exact backend/device scope."""

    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    with _NATIVE_EVIDENCE_LOCK:
        records = tuple(
            record
            for record in _NATIVE_EVIDENCE.values()
            if (backend_name is None or record.backend == backend_name)
            and (device_name is None or record.device == device_name)
        )
    qualified = tuple(record for record in records if record.qualified)
    native_records = tuple(record for record in records if record.native_runtime)
    native_qualified = tuple(
        record for record in native_records if record.qualified
    )
    native_partition_qualified = tuple(
        record for record in native_records if record.partition_qualified
    )
    identity_complete_records = tuple(
        record for record in native_records if record.identity_complete
    )
    native_failed = tuple(record for record in native_records if not record.qualified)
    if not native_records:
        native_status = "unverified"
    elif not native_failed:
        native_status = "qualified"
    else:
        native_status = "partial"
    operations = tuple(sorted({record.operation for record in records}))
    return {
        "backend": backend_name,
        "device": device_name,
        "record_count": len(records),
        "qualified_count": len(qualified),
        # These fields deliberately distinguish semantic records from an
        # observed native-device run.  A semantic/CPU adapter must never make
        # a graphics target look qualified in a release audit.
        "native_record_count": len(native_records),
        "native_qualified_count": len(native_qualified),
        "native_partition_qualified_count": len(native_partition_qualified),
        "identity_complete_count": len(identity_complete_records),
        "identity_complete_percent": round(
            100.0 * len(identity_complete_records) / len(native_records), 4
        ) if native_records else 0.0,
        "native_failed_count": len(native_failed),
        "native_coverage_percent": round(
            100.0 * len(native_qualified) / len(native_records), 4
        ) if native_records else 0.0,
        "native_status": native_status,
        "native_partition_status": (
            "unverified"
            if not native_records
            else (
                "qualified"
                if len(native_partition_qualified) == len(native_records)
                else "partial"
            )
        ),
        "operations": operations,
        "qualified_operations": tuple(
            sorted({record.operation for record in qualified})
        ),
        "records": tuple(
            record.as_dict()
            for record in sorted(
                records, key=lambda item: (item.operation, item.backend, item.device)
            )
        ),
    }


def native_partition_evidence_snapshot() -> (
    Mapping[tuple[str, str, str], NativePartitionEvidence]
):
    with _NATIVE_EVIDENCE_LOCK:
        return dict(_NATIVE_EVIDENCE)


def clear_native_partition_evidence() -> None:
    """Clear process-local evidence (used by isolated tests only)."""

    with _NATIVE_EVIDENCE_LOCK:
        _NATIVE_EVIDENCE.clear()


def register_probe_result(
    result: Mapping[str, Any],
    *,
    command: str,
    source: str = "command_probe",
    replace: bool = True,
) -> tuple[NativePartitionEvidence, ...]:
    """Convert JSON from ``probe_native_partition.py`` into records."""

    # Probe reports cross a JSON/process boundary.  Calling ``.get`` on an
    # arbitrary object would otherwise leak an implementation ``AttributeError``
    # instead of reporting a malformed schema, and a non-mapping object with
    # no operations could be accepted as an empty (apparently valid) report.
    # Reject it before any normalization or registry work; Mapping keeps
    # compatibility with dict-like JSON adapters.
    if not isinstance(result, Mapping):
        raise ValueError("native probe result must be a mapping")

    backend_aliases = {
        "vk": "vulkan",
        "gl": "opengl",
        "egl": "opengl",
        "opengl_es": "gles",
    }
    backend = str(result.get("backend", "")).strip().lower()
    backend = backend_aliases.get(backend, backend)
    runtime_backend = str(result.get("runtime_backend", "") or "").strip().lower()
    runtime_backend = backend_aliases.get(runtime_backend, runtime_backend)
    if runtime_backend and runtime_backend != backend:
        raise ValueError(
            "native probe backend identity mismatch: "
            f"requested {backend!r}, runtime {runtime_backend!r}"
        )
    device = str(result.get("device_name", "")) or "CPU"
    device_id = result.get("device_id")
    target_id = result.get("target_id")
    if target_id:
        target_text = str(target_id).strip().lower()
        target_backend = target_text.split("_", 1)[0]
        if backend_aliases.get(target_backend, target_backend) != backend:
            raise ValueError(
                "native probe target identity mismatch: "
                f"backend {backend!r}, target_id {target_id!r}"
            )
    architecture = result.get("architecture")
    driver_version = result.get("driver_version")
    vendor = result.get("vendor") or result.get("vendor_name")
    if target_id:
        _validate_probe_target_vendor(target_id, backend, vendor)
    block_size = result.get("block_size")
    # Validate all operation status flags before inserting anything.  This
    # keeps a malformed later operation from leaving a partially registered
    # probe result behind.
    raw_operations = result.get("operations", {})
    if raw_operations is None:
        raw_operations = {}
    if not isinstance(raw_operations, Mapping):
        raise ValueError("native probe operations must be a mapping")
    operation_payloads = []
    for operation, raw_details in raw_operations.items():
        if not isinstance(raw_details, Mapping):
            # ``dict([1, 2])`` and similar coercions either raise obscure
            # errors or accept malformed JSON-shaped data.  Reject it at the
            # probe boundary, before any operation can enter the registry.
            raise ValueError(
                f"native probe operation {operation!r} details must be a mapping"
            )
        details = dict(raw_details)
        block_selected = None
        if "block_selected" in details:
            block_selected = _coerce_probe_bool(
                details["block_selected"], "block_selected"
            )
        passed = _coerce_probe_bool(details.get("passed", False), "passed")
        # Stage all numeric/interpolation fields before writing any record.
        # This keeps malformed telemetry fail-closed and preserves the
        # all-or-nothing behavior of a single probe report.
        # Legacy probe JSON omitted max_abs_error for operations that only
        # reported a boolean status.  Keep that public ingestion format
        # compatible; explicit values are still validated strictly below.
        max_abs_error = _coerce_probe_metric(
            details.get("max_abs_error", 0.0), "max_abs_error"
        )
        tolerance = _coerce_probe_metric(
            details.get("tolerance", 0.0), "tolerance"
        )
        raw_interpolations = details.get("interpolations", ("linear",))
        if isinstance(raw_interpolations, str):
            interpolations = (raw_interpolations,)
        else:
            try:
                interpolations = tuple(raw_interpolations)
            except TypeError as exc:
                raise ValueError(
                    f"native probe operation {operation!r} interpolations must be iterable"
                ) from exc
        operation_payloads.append(
            (
                operation,
                details,
                block_selected,
                passed,
                max_abs_error,
                tolerance,
                interpolations,
            )
        )

    records = []
    for (
        operation,
        details,
        block_selected,
        passed,
        max_abs_error,
        tolerance,
        interpolations,
    ) in operation_payloads:
        # A probe can intentionally report a correct full-frame fallback when
        # a global operation has no native partition executor.  Such a record
        # is useful diagnostics, but it is not native partition evidence and
        # must never be inserted into this registry.  Older probe JSON may not
        # carry ``block_selected``; preserve their compatibility by accepting
        # an absent field while rejecting an explicit false value.
        if block_selected is False:
            continue
        canonical_operation = _OBSERVED_OPTIONAL_OPERATION_ALIASES.get(
            str(operation), str(operation)
        )
        records.append(
            register_native_partition_evidence(
                operation=canonical_operation,
                backend=backend,
                device=device,
                device_id=device_id,
                target_id=target_id,
                architecture=architecture,
                driver_version=driver_version,
                vendor=vendor,
                command=command,
                passed=passed,
                max_abs_error=max_abs_error,
                tolerance=tolerance,
                interpolations=interpolations,
                block_size=block_size,
                shape=details.get("shape"),
                dtype=details.get("dtype"),
                source=source,
                replace=replace,
            )
        )
    return tuple(records)


_OBSERVED_PROBE_COMMAND_CPU = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend cpu --device 0 --block-size 7"
)
_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend vulkan --device 0 --block-size 7"
)

# The optional local/stencil tranche was rerun on the exact same targets after
# the probe gained explicit operation selection.  Keep the command complete
# so an audit can reproduce the result rather than treating a hand-written
# operation list as implicit evidence.
_OBSERVED_OPTIONAL_OPERATIONS = (
    "box_filter",
    "gaussian_blur",
    "median_filter",
    "sobel",
    "laplacian",
    "highlight_recovery",
    # The public probe wrapper is named ``smooth_flow_gpu``; the maintained
    # block operation key is the canonical ``smooth_flow``.
    "smooth_flow_gpu",
)
_OBSERVED_OPTIONAL_OPERATION_ALIASES = {
    "smooth_flow_gpu": "smooth_flow",
}
_OBSERVED_OPTIONAL_PROBE_ARGUMENTS = (
    "--operations box_filter,gaussian_blur,median_filter,sobel,"
    "laplacian,highlight_recovery,smooth_flow_gpu"
)
_OBSERVED_PROBE_COMMAND_CPU_OPTIONAL = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend cpu --device 0 --block-size 7 "
    + _OBSERVED_OPTIONAL_PROBE_ARGUMENTS
)
_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_OPTIONAL = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend vulkan --device 0 --block-size 7 "
    + _OBSERVED_OPTIONAL_PROBE_ARGUMENTS
)

_OBSERVED_OPTIONAL_SHAPES = {
    "box_filter": [[19, 23]],
    "gaussian_blur": [[19, 23]],
    "median_filter": [[19, 23]],
    "sobel": [[19, 23], [19, 23]],
    "laplacian": [[19, 23]],
    "highlight_recovery": [[19, 23, 3]],
    "smooth_flow_gpu": [[19, 23, 2]],
}
_OBSERVED_OPTIONAL_DTYPES = {
    "box_filter": ["float32"],
    "gaussian_blur": ["float32"],
    "median_filter": ["float32"],
    "sobel": ["float32", "float32"],
    "laplacian": ["float32"],
    "highlight_recovery": ["float32"],
    "smooth_flow_gpu": ["float32"],
}

# Extended local/stencil tranche.  This is intentionally CPU-only until the
# same operation list has been rerun on a target-qualified graphics device.
_OBSERVED_EXTENDED_OPERATIONS = (
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
_OBSERVED_EXTENDED_PROBE_ARGUMENTS = (
    "--operations morphology,filter2d,threshold,normalize,"
    "joint_bilateral_guidance,enhance_image,joint_bilateral_filter,"
    "guided_filter,non_local_means"
)
_OBSERVED_PROBE_COMMAND_CPU_EXTENDED = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend cpu --device 0 --block-size 7 "
    + _OBSERVED_EXTENDED_PROBE_ARGUMENTS
)
_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_EXTENDED = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend vulkan --device 0 --block-size 7 "
    + _OBSERVED_EXTENDED_PROBE_ARGUMENTS
)
_OBSERVED_PROBE_COMMAND_VULKAN_INTEL_EXTENDED = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='vulkan'; $env:AOT_ARCH='vulkan'; "
    "$env:PIXEL_REFINE_BACKEND='vulkan'; $env:AOT_DEVICE='0'; "
    "$env:PIXEL_REFINE_AOT_DEVICE='0'; $env:TARGET_VENDOR='intel'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend vulkan --device 0 --block-size 7 "
    + _OBSERVED_EXTENDED_PROBE_ARGUMENTS
)
_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_RESIZE = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='vulkan'; $env:AOT_ARCH='vulkan'; "
    "$env:BACKEND='vulkan'; $env:PIXEL_REFINE_BACKEND='vulkan'; "
    "$env:AOT_DEVICE='0'; $env:PIXEL_REFINE_AOT_DEVICE='0'; "
    "$env:TARGET_VENDOR='nvidia'; venv\\Scripts\\python.exe -u -m "
    "taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition "
    "--backend vulkan --device 0 --block-size 7 --interpolations linear "
    "--expected-vendor nvidia --expected-device \"NVIDIA GeForce MX150\""
)
_OBSERVED_PROBE_COMMAND_VULKAN_INTEL_RESIZE = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='vulkan'; $env:AOT_ARCH='vulkan'; "
    "$env:BACKEND='vulkan'; $env:PIXEL_REFINE_BACKEND='vulkan'; "
    "$env:AOT_DEVICE='0'; $env:PIXEL_REFINE_AOT_DEVICE='0'; "
    "$env:TARGET_VENDOR='intel'; venv\\Scripts\\python.exe -u -m "
    "taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition "
    "--backend vulkan --device 0 --block-size 7 --interpolations linear "
    "--expected-vendor intel --expected-device \"Intel(R) UHD Graphics 620\""
)
_OBSERVED_PROBE_COMMAND_CUDA_BASE = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='cuda'; $env:AOT_ARCH='cuda'; "
    "$env:PIXEL_REFINE_BACKEND='cuda'; $env:AOT_DEVICE='0'; "
    "$env:PIXEL_REFINE_AOT_DEVICE='0'; $env:CUDA_DEVICE='0'; "
    "$env:PIXEL_REFINE_CUDA_DEVICE='0'; $env:TARGET_VENDOR='nvidia'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend cuda --device 0 --block-size 7 "
    "--operations base"
)
_OBSERVED_PROBE_COMMAND_CUDA_EXTENDED = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='cuda'; $env:AOT_ARCH='cuda'; "
    "$env:PIXEL_REFINE_BACKEND='cuda'; $env:AOT_DEVICE='0'; "
    "$env:PIXEL_REFINE_AOT_DEVICE='0'; $env:CUDA_DEVICE='0'; "
    "$env:PIXEL_REFINE_CUDA_DEVICE='0'; $env:TARGET_VENDOR='nvidia'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend cuda --device 0 --block-size 7 "
    + _OBSERVED_EXTENDED_PROBE_ARGUMENTS
)
_OBSERVED_PROBE_COMMAND_CUDA_RESIZE = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:PIXEL_REFINE_AOT_ARCH='cuda'; $env:AOT_ARCH='cuda'; "
    "$env:BACKEND='cuda'; $env:PIXEL_REFINE_BACKEND='cuda'; "
    "$env:AOT_DEVICE='0'; $env:PIXEL_REFINE_AOT_DEVICE='0'; "
    "$env:CUDA_DEVICE='0'; $env:PIXEL_REFINE_CUDA_DEVICE='0'; "
    "$env:TARGET_VENDOR='nvidia'; venv\\Scripts\\python.exe -u -m "
    "taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition "
    "--backend cuda --device 0 --block-size 7 --interpolations linear "
    "--expected-vendor nvidia --expected-device \"NVIDIA GeForce MX150\""
)
_OBSERVED_PROBE_COMMAND_OPENGL_NVIDIA_EXTENDED = (
    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
    "$env:BACKEND='opengl'; "
    "$env:TARGET_VENDOR='nvidia'; "
    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
    "probe_native_partition.py --backend opengl --device 0 --block-size 7 "
    + _OBSERVED_EXTENDED_PROBE_ARGUMENTS
)
_OBSERVED_EXTENDED_SHAPES = {
    "morphology": [[19, 23]],
    "filter2d": [[19, 23]],
    "threshold": [[19, 23]],
    "normalize": [[19, 23]],
    "joint_bilateral_guidance": [[19, 23]],
    "enhance_image": [[19, 23]],
    "joint_bilateral_filter": [[19, 23]],
    "guided_filter": [[19, 23]],
    "non_local_means": [[19, 23]],
}
_OBSERVED_EXTENDED_DTYPES = {
    operation: ["float32"] for operation in _OBSERVED_EXTENDED_OPERATIONS
}
_OBSERVED_RESIZE_CASES = (
    {"source_shape": [23, 31], "target_dsize": [17, 19], "target_shape": [19, 17]},
    {
        "source_shape": [29, 37, 3],
        "target_dsize": [13, 22],
        "target_shape": [22, 13, 3],
    },
    {"source_shape": [17, 25], "target_dsize": [31, 11], "target_shape": [11, 31]},
    {
        "source_shape": [31, 27, 3],
        "target_dsize": [15, 19],
        "target_shape": [19, 15, 3],
    },
)


def register_verified_native_partition_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Load the checked-in records from the reproducible native probes.

    These are scoped to the exact devices observed on 2026-08-10: Windows
    CPU and NVIDIA GeForce MX150 Vulkan.  The checked-in records cover the
    eight local/data-movement operations that selected a native block path;
    global reductions such as ``otsu_threshold`` are intentionally excluded
    when the probe reports a full-frame fallback.  No OpenGL, Intel, CUDA, or
    other vendor is inferred from these records.  The function is explicit so
    a caller can clear/reload process-local diagnostics as part of a test.
    """

    operations = (
        "copy",
        "absdiff",
        "rgb2gray",
        "split_3ch",
        "merge_3ch",
        "extract_channel",
        "insert_channel",
        "cvtColor",
    )
    records: list[NativePartitionEvidence] = []
    for operation in operations:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="cpu",
                device="CPU (x86_64 Windows)",
                device_id=0,
                command=_OBSERVED_PROBE_COMMAND_CPU,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-10",
                note="actual CPU bridge run; exact semantic parity",
                replace=replace,
            )
        )
    for operation in operations:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="vulkan",
                device="NVIDIA GeForce MX150",
                # The requested Vulkan ordinal was 0; the runtime resolved
                # the observed physical device as ordinal 2.  Keep both the
                # command and the post-init identity in the record.
                device_id=2,
                command=_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-10",
                note="actual Vulkan NVIDIA bridge run; runtime device identity verified",
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_stencil_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the command-backed local/stencil tranche for exact targets.

    This helper is intentionally separate from the base evidence loader.  It
    records only the seven operations whose selected probe records reported
    ``block_selected=true`` and ``passed=true`` on both the Windows CPU and
    NVIDIA GeForce MX150 Vulkan runs.  It does not touch operation contracts,
    ``AUTO_BLOCK_SAFE``, or dispatch policy; callers still need an exact
    backend/device match when consuming the records.
    """

    target_specs = (
        (
            "cpu",
            "CPU (x86_64 Windows)",
            0,
            _OBSERVED_PROBE_COMMAND_CPU_OPTIONAL,
            "observed_optional_command_2026-08-10_cpu",
            "actual CPU bridge optional local/stencil run; exact semantic parity",
        ),
        (
            "vulkan",
            "NVIDIA GeForce MX150",
            2,
            _OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_OPTIONAL,
            "observed_optional_command_2026-08-10_vulkan_nvidia_mx150",
            "actual Vulkan NVIDIA optional local/stencil run; device identity verified",
        ),
    )
    records: list[NativePartitionEvidence] = []
    for backend, device, device_id, command, source, note in target_specs:
        for operation in _OBSERVED_OPTIONAL_OPERATIONS:
            canonical = _OBSERVED_OPTIONAL_OPERATION_ALIASES.get(operation, operation)
            records.append(
                register_native_partition_evidence(
                    operation=canonical,
                    backend=backend,
                    device=device,
                    device_id=device_id,
                    command=command,
                    passed=True,
                    max_abs_error=0.0,
                    block_size=7,
                    shape=_OBSERVED_OPTIONAL_SHAPES[operation],
                    dtype=_OBSERVED_OPTIONAL_DTYPES[operation],
                    scope="native_full_frame_vs_block",
                    source=source,
                    note=note,
                    replace=replace,
                )
            )
    return tuple(records)


def register_verified_native_local_stencil_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register exact CPU and NVIDIA Vulkan records for the extended tranche.

    The records are scoped to the two targets actually exercised by the
    reproducible probe: ``CPU (x86_64 Windows)`` and the runtime-identified
    ``NVIDIA GeForce MX150`` Vulkan device (physical ``device_id=2``).  No
    OpenGL, Intel, CUDA, or other vendor is inferred from these records.  A
    target must be rerun with the same operation list before it can be added
    here.
    """

    target_specs = (
        (
            "cpu",
            "CPU (x86_64 Windows)",
            0,
            _OBSERVED_PROBE_COMMAND_CPU_EXTENDED,
            "observed_extended_command_2026-08-10_cpu",
            "actual CPU bridge run; block_selected=true and parity passed for the bounded local/stencil parameters",
        ),
        (
            "vulkan",
            "NVIDIA GeForce MX150",
            2,
            _OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_EXTENDED,
            "observed_extended_command_2026-08-10_vulkan_nvidia_mx150",
            "actual Vulkan NVIDIA run; runtime device identity verified and block parity passed for bounded local/stencil parameters",
        ),
    )
    records: list[NativePartitionEvidence] = []
    for backend, device, device_id, command, source, note in target_specs:
        for operation in _OBSERVED_EXTENDED_OPERATIONS:
            records.append(
                register_native_partition_evidence(
                    operation=operation,
                    backend=backend,
                    device=device,
                    device_id=device_id,
                    command=command,
                    passed=True,
                    max_abs_error=0.0,
                    block_size=7,
                    shape=_OBSERVED_EXTENDED_SHAPES[operation],
                    dtype=_OBSERVED_EXTENDED_DTYPES[operation],
                    scope="native_full_frame_vs_block",
                    source=source,
                    note=note,
                    replace=replace,
                )
            )
    return tuple(records)


def register_verified_native_vulkan_intel_local_stencil_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the nine extended local/stencil operations observed on Intel Vulkan.

    This record is intentionally separate from the NVIDIA/CPU loaders.  The
    probe ran against the physical Intel UHD Graphics 620 Vulkan device at
    ordinal 0, after the target-qualified Intel TCM modules were rebuilt and
    the shared executor import contract was corrected.  It does not promote
    any backend globally; consumers still require the exact device identity.
    """

    device = "Intel(R) UHD Graphics 620"
    records: list[NativePartitionEvidence] = []
    for operation in _OBSERVED_EXTENDED_OPERATIONS:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="vulkan",
                device=device,
                device_id=0,
                command=_OBSERVED_PROBE_COMMAND_VULKAN_INTEL_EXTENDED,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                shape=_OBSERVED_EXTENDED_SHAPES[operation],
                dtype=_OBSERVED_EXTENDED_DTYPES[operation],
                scope="native_full_frame_vs_block",
                source="observed_extended_command_2026-08-13_vulkan_intel_uhd620",
                note=(
                    "actual Intel UHD 620 Vulkan run; block_selected=true, "
                    "status=ok, parity passed; target-qualified TCM"
                ),
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_vulkan_intel_base_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the eight base partition operations observed on Intel Vulkan.

    This is the exact-device base probe on Intel UHD Graphics 620 (ordinal 0),
    block size 7.  All requested base operations selected a native block path,
    returned status ``ok`` where telemetry was available, and had zero parity
    error.  The record does not qualify another Vulkan device or backend.
    """

    operations = (
        "copy", "absdiff", "rgb2gray", "split_3ch", "merge_3ch",
        "extract_channel", "insert_channel", "cvtColor",
    )
    shapes = {
        "copy": [[19, 23, 3]], "absdiff": [[19, 23]],
        "rgb2gray": [[19, 23]], "split_3ch": [[19, 23], [19, 23], [19, 23]],
        "merge_3ch": [[19, 23, 3]], "extract_channel": [[19, 23]],
        "insert_channel": [[19, 23, 3]], "cvtColor": [[19, 23]],
    }
    dtypes = {
        "copy": ["uint8"], "absdiff": ["float32"], "rgb2gray": ["uint8"],
        "split_3ch": ["uint8", "uint8", "uint8"], "merge_3ch": ["uint8"],
        "extract_channel": ["uint8"], "insert_channel": ["uint8"],
        "cvtColor": ["float32"],
    }
    command = (
        "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
        "$env:PIXEL_REFINE_AOT_ARCH='vulkan'; $env:AOT_ARCH='vulkan'; "
        "$env:BACKEND='vulkan'; $env:PIXEL_REFINE_BACKEND='vulkan'; "
        "$env:AOT_DEVICE='0'; $env:PIXEL_REFINE_AOT_DEVICE='0'; "
        "$env:TARGET_VENDOR='intel'; venv\\Scripts\\python.exe -u -m "
        "taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition "
        "--backend vulkan --device 0 --block-size 7 --operations base"
    )
    records: list[NativePartitionEvidence] = []
    for operation in operations:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="vulkan",
                device="Intel(R) UHD Graphics 620",
                device_id=0,
                command=command,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                shape=shapes[operation],
                dtype=dtypes[operation],
                scope="native_full_frame_vs_block",
                source="observed_base_command_2026-08-13_vulkan_intel_uhd620",
                note=(
                    "actual Intel UHD 620 Vulkan base run; block_selected=true, "
                    "parity error 0.0; target-qualified TCM"
                ),
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_vulkan_nvidia_resize_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the four-case linear resize probe on the exact NVIDIA Vulkan device.

    The probe used deliberately non-multiple source/output dimensions and a
    block size of 7.  Every case passed both cold and warm full-frame parity
    with zero error.  Cold execution selected the native ``batch_offset``
    executor; the warm call reported output-tile cache hits.  This evidence
    is scoped to the runtime-identified MX150 Vulkan device and does not
    qualify another GPU, interpolation mode, or backend.
    """

    return (
        register_native_partition_evidence(
            operation="resize",
            backend="vulkan",
            device="NVIDIA GeForce MX150",
            device_id=2,
            command=_OBSERVED_PROBE_COMMAND_VULKAN_NVIDIA_RESIZE,
            passed=True,
            max_abs_error=0.0,
            block_size=7,
            shape=[dict(case) for case in _OBSERVED_RESIZE_CASES],
            dtype=["float32"],
            scope="native_full_frame_vs_block",
            source="observed_resize_command_2026-08-13_vulkan_nvidia_mx150",
            note=(
                "actual Vulkan NVIDIA MX150 run; four non-multiple linear cases; "
                "cold/warm parity error 0.0; native mode=batch_offset; "
                "warm output-tile cache hits observed"
            ),
            replace=replace,
        ),
    )


def register_verified_native_vulkan_intel_resize_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the four-case linear resize probe on Intel UHD 620 Vulkan.

    The exact device run used non-multiple dimensions and block size 7.  All
    four cold and warm comparisons had zero error, selected the native
    ``batch_offset`` executor, and reported warm output-tile cache hits.  The
    record is intentionally limited to the runtime-identified Intel UHD 620;
    it does not qualify Vulkan devices from another vendor or OpenGL.
    """

    return (
        register_native_partition_evidence(
            operation="resize",
            backend="vulkan",
            device="Intel(R) UHD Graphics 620",
            device_id=0,
            command=_OBSERVED_PROBE_COMMAND_VULKAN_INTEL_RESIZE,
            passed=True,
            max_abs_error=0.0,
            block_size=7,
            shape=[dict(case) for case in _OBSERVED_RESIZE_CASES],
            dtype=["float32"],
            scope="native_full_frame_vs_block",
            source="observed_resize_command_2026-08-13_vulkan_intel_uhd620",
            note=(
                "actual Intel UHD 620 Vulkan run; four non-multiple linear cases; "
                "cold/warm parity error 0.0; native mode=batch_offset; "
                "warm output-tile cache hits observed"
            ),
            replace=replace,
        ),
    )


def register_verified_native_cuda_resize_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the four-case linear resize probe on CUDA MX150.

    All cases selected the native ``batch_offset`` executor and passed the
    probe's float32 tolerance.  The RGB cases measured a maximum absolute
    error of 1.1920928955078125e-7, so the record retains that value and an
    explicit 2e-5 tolerance instead of incorrectly claiming bit-exact output.
    """

    max_abs_error = 1.1920928955078125e-7
    return (
        register_native_partition_evidence(
            operation="resize",
            backend="cuda",
            device="NVIDIA GeForce MX150",
            device_id=0,
            command=_OBSERVED_PROBE_COMMAND_CUDA_RESIZE,
            passed=True,
            max_abs_error=max_abs_error,
            tolerance=2.0e-5,
            interpolations=("linear", "cubic", "area"),
            block_size=7,
            shape=[dict(case) for case in _OBSERVED_RESIZE_CASES],
            dtype=["float32"],
            scope="native_full_frame_vs_block",
            source="observed_resize_command_2026-08-13_cuda_mx150",
            note=(
                "actual CUDA Device 0 NVIDIA GeForce MX150; four non-multiple "
                "linear/cubic/area cases; native mode=offset or batch_offset; warm output-tile cache "
                "hits observed; max measured error 1.1920928955078125e-7 "
                "within float32 tolerance 2e-5"
            ),
            replace=replace,
        ),
    )


def register_verified_native_cuda_partition_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the 24 CUDA MX150 operations that passed the all-probe.

    ``otsu_threshold`` is deliberately excluded: its probe selected the
    documented full-frame path, so it is not native partition evidence.
    """

    device = "NVIDIA GeForce MX150"
    base = (
        "copy", "absdiff", "rgb2gray", "split_3ch", "merge_3ch",
        "extract_channel", "insert_channel", "cvtColor",
    )
    operations = base + _OBSERVED_OPTIONAL_OPERATIONS + _OBSERVED_EXTENDED_OPERATIONS
    shapes = {
        "copy": [[19, 23, 3]], "absdiff": [[19, 23]],
        "rgb2gray": [[19, 23]], "split_3ch": [[19, 23], [19, 23], [19, 23]],
        "merge_3ch": [[19, 23, 3]], "extract_channel": [[19, 23]],
        "insert_channel": [[19, 23, 3]], "cvtColor": [[19, 23]],
        **_OBSERVED_OPTIONAL_SHAPES, **_OBSERVED_EXTENDED_SHAPES,
    }
    dtypes = {
        "copy": ["uint8"], "absdiff": ["float32"], "rgb2gray": ["uint8"],
        "split_3ch": ["uint8", "uint8", "uint8"], "merge_3ch": ["uint8"],
        "extract_channel": ["uint8"], "insert_channel": ["uint8"],
        "cvtColor": ["float32"],
        **_OBSERVED_OPTIONAL_DTYPES, **_OBSERVED_EXTENDED_DTYPES,
    }
    canonical_alias = {"smooth_flow_gpu": "smooth_flow"}
    probe_operations = ",".join(operations + ("otsu_threshold",))
    command = (
        "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
        "$env:AOT_ARCH='cuda'; $env:BACKEND='cuda'; $env:AOT_DEVICE='0'; "
        "$env:TARGET_VENDOR='nvidia'; venv\\Scripts\\python.exe -u -m "
        "taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition "
        f"--backend cuda --device 0 --block-size 7 --operations {probe_operations}"
    )
    records: list[NativePartitionEvidence] = []
    for operation in operations:
        canonical = canonical_alias.get(operation, operation)
        records.append(
            register_native_partition_evidence(
                operation=canonical,
                backend="cuda",
                device=device,
                device_id=0,
                command=command,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                shape=shapes[operation],
                dtype=dtypes[operation],
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-13_cuda_mx150_all_minus_otsu",
                note=(
                    "actual CUDA Device 0 NVIDIA GeForce MX150; all-probe "
                    "subset block_selected=true, status=ok, parity error 0.0; "
                    "otsu_threshold excluded because it was full-frame"
                ),
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_opengl_stencil_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the observed NVIDIA OpenGL local/stencil probe.

    The probe was run against the actual NVIDIA GeForce MX150 OpenGL ICD on
    2026-08-10.  It is deliberately separate from Vulkan evidence: an OpenGL
    context/renderer cannot be inferred from a Vulkan device record, and the
    OpenGL path remains serialized (this evidence proves parity/selection, not
    queue overlap).
    """

    records: list[NativePartitionEvidence] = []
    for operation in _OBSERVED_EXTENDED_OPERATIONS:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="opengl",
                device="NVIDIA Corporation - NVIDIA GeForce MX150/PCIe/SSE2",
                device_id=0,
                command=_OBSERVED_PROBE_COMMAND_OPENGL_NVIDIA_EXTENDED,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                shape=_OBSERVED_EXTENDED_SHAPES[operation],
                dtype=_OBSERVED_EXTENDED_DTYPES[operation],
                scope="native_full_frame_vs_block",
                source="observed_extended_command_2026-08-10_opengl_nvidia",
                note="actual NVIDIA OpenGL ICD run; block_selected=true and parity passed; serialized context",
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_opengl_partition_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register all 17 observed base + extended NVIDIA OpenGL operations."""

    operations = (
        "copy",
        "absdiff",
        "rgb2gray",
        "split_3ch",
        "merge_3ch",
        "extract_channel",
        "insert_channel",
        "cvtColor",
    ) + _OBSERVED_EXTENDED_OPERATIONS
    records: list[NativePartitionEvidence] = []
    for operation in operations:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="opengl",
                device="NVIDIA Corporation - NVIDIA GeForce MX150/PCIe/SSE2",
                device_id=0,
                command=(
                    "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
                    "$env:BACKEND='opengl'; "
                    "$env:TARGET_VENDOR='nvidia'; "
                    "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
                    "probe_native_partition.py --backend opengl --device 0 --block-size 7 "
                    "--operations base"
                    if operation
                    in {
                        "copy",
                        "absdiff",
                        "rgb2gray",
                        "split_3ch",
                        "merge_3ch",
                        "extract_channel",
                        "insert_channel",
                        "cvtColor",
                    }
                    else _OBSERVED_PROBE_COMMAND_OPENGL_NVIDIA_EXTENDED
                ),
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-10_opengl_nvidia",
                note="actual NVIDIA OpenGL ICD run; block_selected=true and parity passed; serialized context",
                replace=replace,
            )
        )
    return tuple(records)


def register_verified_native_opengl_intel_evidence(
    *, replace: bool = True
) -> tuple[NativePartitionEvidence, ...]:
    """Register the passed Intel UHD 620 OpenGL subset.

    The Intel probe passed all eight base operations and eight of the nine
    extended operations.  ``guided_filter`` is intentionally omitted because
    its OpenGL Intel run selected a full-frame fallback due to the artifact
    module mismatch; omission keeps the registry honest.
    """

    base = (
        "copy",
        "absdiff",
        "rgb2gray",
        "split_3ch",
        "merge_3ch",
        "extract_channel",
        "insert_channel",
        "cvtColor",
    )
    extended = tuple(
        operation
        for operation in _OBSERVED_EXTENDED_OPERATIONS
        if operation != "guided_filter"
    )
    device = "Intel(R) UHD Graphics 620"
    base_command = (
        "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
        "$env:BACKEND='opengl'; $env:TARGET_VENDOR='intel'; "
        "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
        "probe_native_partition.py --backend opengl --device 0 --block-size 7 --operations base"
    )
    extended_command = (
        "$env:AOT_MODE='1'; $env:PYTHONPATH='E:\\APP Developer\\Pixel Refine'; "
        "$env:BACKEND='opengl'; $env:TARGET_VENDOR='intel'; "
        "python -u taichi_vision\\taichi_algorithm\\aot_py\\tools\\"
        "probe_native_partition.py --backend opengl --device 0 --block-size 7 "
        "--operations morphology,filter2d,threshold,normalize,"
        "joint_bilateral_guidance,enhance_image,joint_bilateral_filter,"
        "guided_filter,non_local_means"
    )
    records: list[NativePartitionEvidence] = []
    for operation in base:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="opengl",
                device=device,
                device_id=0,
                command=base_command,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-10_opengl_intel",
                note="actual Intel UHD 620 OpenGL ICD run; base operation passed",
                replace=replace,
            )
        )
    for operation in extended:
        records.append(
            register_native_partition_evidence(
                operation=operation,
                backend="opengl",
                device=device,
                device_id=0,
                command=extended_command,
                passed=True,
                max_abs_error=0.0,
                block_size=7,
                shape=_OBSERVED_EXTENDED_SHAPES[operation],
                dtype=_OBSERVED_EXTENDED_DTYPES[operation],
                scope="native_full_frame_vs_block",
                source="observed_command_2026-08-10_opengl_intel",
                note="actual Intel UHD 620 OpenGL ICD run; block parity passed",
                replace=replace,
            )
        )
    return tuple(records)


__all__ = [
    "NativePartitionEvidence",
    "register_native_partition_evidence",
    "lookup_native_partition_evidence",
    "get_native_partition_evidence",
    "native_partition_evidence_supported",
    "native_partition_promotion_report",
    "native_partition_promotion_matrix_report",
    "native_partition_evidence_promotion_report",
    "native_partition_evidence_report",
    "native_partition_evidence_snapshot",
    "clear_native_partition_evidence",
    "register_probe_result",
    "register_verified_native_partition_evidence",
    "register_verified_native_stencil_evidence",
    "register_verified_native_local_stencil_evidence",
    "register_verified_native_vulkan_intel_local_stencil_evidence",
    "register_verified_native_vulkan_intel_base_evidence",
    "register_verified_native_vulkan_nvidia_resize_evidence",
    "register_verified_native_vulkan_intel_resize_evidence",
    "register_verified_native_cuda_resize_evidence",
    "register_verified_native_cuda_partition_evidence",
    "register_verified_native_opengl_stencil_evidence",
    "register_verified_native_opengl_partition_evidence",
    "register_verified_native_opengl_intel_evidence",
]
