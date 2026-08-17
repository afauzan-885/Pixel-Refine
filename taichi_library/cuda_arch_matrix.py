"""CUDA architecture qualification helpers.

This module is deliberately independent from :mod:`taichi_aot.engine` so it
can be used by build jobs and CI without creating a CUDA context.  It keeps
three different claims separate:

``compile_only``
    The selected LLVM/NVCC toolchain accepts an ``sm_XX``/``compute_XX``
    target.  This does not exercise a driver or a GPU.
``runtime_candidate``
    The vendored Taichi source has a plausible generic NVPTX path for the
    capability, but this repository still needs a real-device test.
``native_qualified``
    Reserved for an observed strict-backend run on the matching GPU.  Static
    compilation must never set this value.

Historical reports may mention the Taichi 1.7.4/LLVM 15 bridge, whose CUDA
context used to clamp detected capabilities above 8.6.  That bridge is no
longer the active production candidate: the maintained build is regenerated
with a coherent LLVM20/NVPTX toolchain.  The historical note remains only so
old reports can be interpreted correctly.

Modern bridge builds may carry a validated ``cuda_bridge_manifest.json``
sidecar.  It can expand compile/runtime candidate routing only for the exact
SMs listed by that bridge; native qualification remains an observed-device
claim and is never inferred from compilation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterable, Mapping, Optional, Sequence


# Architectures relevant to the maintained desktop CUDA profile.  Legacy
# CC<5 is intentionally represented by profiles but excluded from the current
# LLVM20 native candidate set.
KNOWN_COMPUTE_CAPABILITIES: tuple[int, ...] = (
    10,
    11,
    12,
    13,
    20,
    21,
    30,
    32,
    35,
    37,
    50,
    52,
    53,
    60,
    61,
    62,
    70,
    72,
    75,
    80,
    86,
    87,
    89,
    90,
    100,
    101,
    103,
    120,
    121,
)

# These are the exact graph-lowering targets observed in the LLVM20 offline
# sweep (50 graphs per target).  A target accepted by clang/llc or nvcc is not
# automatically included here: it remains compile-only until every embedded
# TCM graph has passed the target-aware lowering gate.
CURRENT_TAICHI_LLVM20_TARGETS: frozenset[int] = frozenset({52, 53, 61, 120})
# Compatibility alias for older build/report consumers.  It is deliberately a
# value alias, not an LLVM15 artifact selector; new code must use the LLVM20
# name so reports cannot accidentally describe a stale toolchain envelope.
CURRENT_TAICHI_LLVM15_TARGETS = CURRENT_TAICHI_LLVM20_TARGETS

CUDA_BRIDGE_MANIFEST_SCHEMA = 1

# CUDA 12.8/12.9 introduced Blackwell baseline, family, and architecture
# variants.  Keep the numeric compute-capability API backward compatible, but
# give validators and manifests a lossless target token (for example
# ``sm_120a``).  CUDA 13 toolchains may spell the Thor target as ``sm_110``;
# it is an alias for the canonical 101 capability in this project model.
_CUDA_TARGET_RE = re.compile(r"^(?:sm_|compute_)?(?P<cc>\d{2,3})(?P<suffix>[af]?)$")
_CUDA_CC_ALIASES: dict[int, int] = {110: 101}
_BLACKWELL_VARIANT_CCS = frozenset({100, 101, 103, 120, 121})


def _cc_int(value: object) -> int:
    raw = str(value or "").strip().lower()
    raw = raw.replace("compute_", "").replace("sm_", "")
    if "." in raw:
        major, minor = raw.split(".", 1)
        return int(major) * 10 + int(minor[:1] or 0)
    return int(raw, 10)


def normalize_compute_capability(value: object) -> int:
    """Normalize ``6.1``, ``61``, ``sm_61`` and ``compute_61`` to ``61``."""

    if isinstance(value, CudaTarget):
        return value.compute_capability
    # Driver/toolkit metadata has historically used ``11.0``/``sm_110`` for
    # the Thor spelling of the Blackwell 10.1 target.  Keep the legacy
    # integer API lossless with respect to our canonical capability table by
    # applying the same alias used by ``normalize_cuda_target``.  Without
    # this normalization ``query_nvidia_smi`` silently dropped a perfectly
    # valid future device because it used this compatibility helper directly.
    raw_cc = _cc_int(value)
    cc = _CUDA_CC_ALIASES.get(raw_cc, raw_cc)
    if cc not in KNOWN_COMPUTE_CAPABILITIES:
        raise ValueError(f"unsupported/unknown CUDA compute capability: {value!r}")
    return cc


@dataclass(frozen=True)
class CudaTarget:
    """Lossless CUDA target token used by offline code-generation gates."""

    compute_capability: int
    suffix: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "compute_capability", normalize_compute_capability(self.compute_capability))
        suffix = str(self.suffix or "").strip().lower()
        if suffix not in {"", "a", "f"}:
            raise ValueError(f"unsupported CUDA target suffix: {self.suffix!r}")
        if suffix and self.compute_capability not in _BLACKWELL_VARIANT_CCS:
            raise ValueError("CUDA a/f target variants are only valid for Blackwell targets")
        object.__setattr__(self, "suffix", suffix)

    @property
    def sm(self) -> str:
        return f"sm_{self.compute_capability}{self.suffix}"

    @property
    def compute(self) -> str:
        return f"compute_{self.compute_capability}{self.suffix}"

    @property
    def family(self) -> str:
        if self.compute_capability in {100, 101, 103}:
            return "blackwell100"
        if self.compute_capability in {120, 121}:
            return "blackwell120"
        return architecture_name(self.compute_capability).lower()

    @property
    def minimum_ptx(self) -> str:
        if self.compute_capability in {103, 121}:
            return "8.8"
        if self.compute_capability in {100, 101, 120}:
            return "8.7"
        if self.compute_capability >= 52:
            return "7.3"
        return "6.0"

    @property
    def minimum_cuda_toolkit(self) -> str:
        if self.compute_capability in _BLACKWELL_VARIANT_CCS:
            return "12.9" if self.compute_capability in {103, 121} else "12.8"
        if self.compute_capability in {50, 52, 53}:
            return "6.5"
        return "8.0"

    def as_dict(self) -> dict[str, object]:
        return {
            "compute_capability": self.compute_capability,
            "sm": self.sm,
            "compute": self.compute,
            "suffix": self.suffix,
            "family": self.family,
            "minimum_ptx": self.minimum_ptx,
            "minimum_cuda_toolkit": self.minimum_cuda_toolkit,
        }


def normalize_cuda_target(value: object) -> CudaTarget:
    """Normalize ``sm_120a``/``compute_101``/``sm_110`` safely.

    The older :func:`normalize_compute_capability` intentionally returns only
    an integer for compatibility.  New build and validation code should use
    this function so architecture-specific Blackwell variants are not
    silently collapsed to their baseline target.
    """

    if isinstance(value, CudaTarget):
        return value
    raw = str(value or "").strip().lower()
    # ``nvidia-smi`` and public metadata commonly report ``8.9`` rather than
    # ``89``.  Normalize that spelling before applying the lossless token
    # grammar; an optional ``sm_``/``compute_`` prefix is accepted as well.
    decimal = re.fullmatch(r"(?:sm_|compute_)?(?P<major>\d+)\.(?P<minor>\d+)", raw)
    if decimal:
        raw = f"{int(decimal.group('major')) * 10 + int(decimal.group('minor')[:1])}"
    match = _CUDA_TARGET_RE.fullmatch(raw)
    if not match:
        raise ValueError(f"invalid CUDA target: {value!r}")
    raw_cc = int(match.group("cc"), 10)
    canonical_cc = _CUDA_CC_ALIASES.get(raw_cc, raw_cc)
    return CudaTarget(canonical_cc, match.group("suffix"))


def sm_name(value: object) -> str:
    # Keep architecture suffixes (for example ``sm_120a``) intact.  The
    # legacy integer normalizer intentionally remains available for callers
    # that only need a numeric compute capability.
    return normalize_cuda_target(value).sm


def compute_name(value: object) -> str:
    return normalize_cuda_target(value).compute


def bridge_manifest_path(bridge_path: object | None = None) -> Optional[Path]:
    """Return the sidecar manifest path for a CUDA bridge.

    The manifest is deliberately a sidecar rather than embedded in the DLL:
    it records which runtime bitcode and toolchain produced that exact bridge
    and can therefore be audited before loading it.  Missing manifests are
    treated as unknown, never as broad support.
    """

    raw = bridge_path or os.environ.get("AOT_ENGINE_DLL")
    if not raw:
        return None
    path = Path(str(raw)).expanduser()
    return path.with_name("cuda_bridge_manifest.json")


def _manifest_target_tokens(value: object, field: str) -> frozenset[CudaTarget]:
    """Parse manifest targets without collapsing architecture suffixes.

    A numeric-only manifest remains fully backward compatible, while newer
    manifests may distinguish Blackwell variants such as ``sm_120a`` and
    ``sm_120f``.  Treating those variants as the same integer would allow a
    bridge built for one variant to be routed to the other.
    """
    if value is None:
        return frozenset()
    if isinstance(value, (str, bytes)):
        values = [part for part in str(value).split(",") if part.strip()]
    else:
        try:
            values = list(value)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError(f"manifest field {field!r} must be a list") from exc
    try:
        normalized = tuple(normalize_cuda_target(item) for item in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"manifest field {field!r} contains an invalid SM") from exc
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"manifest field {field!r} contains duplicate SM targets")
    return frozenset(normalized)


def _manifest_targets(value: object, field: str) -> frozenset[int]:
    """Legacy numeric projection retained for internal/older callers."""

    return frozenset(item.compute_capability for item in _manifest_target_tokens(value, field))


def _manifest_target_value(target: CudaTarget) -> int | str:
    """Serialize a target losslessly while keeping old numeric manifests small."""

    return target.sm if target.suffix else target.compute_capability


def validate_bridge_manifest(payload: object) -> dict[str, object]:
    """Validate and normalize a CUDA bridge capability manifest."""

    if not isinstance(payload, Mapping):
        raise ValueError("CUDA bridge manifest must be a JSON object")
    schema = payload.get("schema_version", payload.get("schema"))
    if schema != CUDA_BRIDGE_MANIFEST_SCHEMA:
        raise ValueError(f"unsupported CUDA bridge manifest schema: {schema!r}")
    if str(payload.get("backend", "cuda")).strip().lower() != "cuda":
        raise ValueError("CUDA bridge manifest backend must be 'cuda'")
    runtime_sms = _manifest_target_tokens(payload.get("runtime_sms"), "runtime_sms")
    custom_sms = _manifest_target_tokens(payload.get("custom_runtime_sms"), "custom_runtime_sms")
    # A runtime bitcode file alone does not prove that every embedded CUDA
    # graph can lower for the target.  CC 5.0 is especially sensitive because
    # PTX dynamic alloca is unavailable there.  Builders may therefore record
    # the exact SMs that passed an IR/TCM lowering sweep separately.
    graph_sms = _manifest_target_tokens(payload.get("graph_lowering_sms"), "graph_lowering_sms")
    native_sms = _manifest_target_tokens(payload.get("native_runtime_sms"), "native_runtime_sms")
    if not custom_sms.issubset(runtime_sms):
        raise ValueError("custom_runtime_sms must be a subset of runtime_sms")
    if not graph_sms.issubset(runtime_sms):
        raise ValueError("graph_lowering_sms must be a subset of runtime_sms")
    if not native_sms.issubset(runtime_sms):
        raise ValueError("native_runtime_sms must be a subset of runtime_sms")
    if not native_sms.issubset(graph_sms):
        raise ValueError("native_runtime_sms must be a subset of graph_lowering_sms")
    # Newer build jobs may attach the validator's per-target summary.  Treat
    # it as evidence metadata, not as a way to broaden the target lists: every
    # evidence key must be an explicitly listed graph target and a full graph
    # claim requires a positive, equal passed/expected count plus a complete
    # inventory.  Older sidecars without this optional field remain valid.
    graph_evidence = payload.get("graph_lowering_evidence")
    if graph_evidence is not None:
        if not isinstance(graph_evidence, Mapping):
            raise ValueError("graph_lowering_evidence must be an object")
        evidence_targets: set[CudaTarget] = set()
        for raw_target, raw_evidence in graph_evidence.items():
            target = normalize_cuda_target(raw_target)
            # JSON object keys can spell the same target in several forms
            # (for example ``61`` and ``sm_61``).  Do not let aliases create
            # two conflicting evidence records for one architecture.
            if target in evidence_targets:
                raise ValueError(
                    "graph_lowering_evidence contains duplicate SM targets"
                )
            evidence_targets.add(target)
            if target not in graph_sms:
                raise ValueError("graph_lowering_evidence contains a target not in graph_lowering_sms")
            if not isinstance(raw_evidence, Mapping):
                raise ValueError("graph_lowering_evidence entries must be objects")
            # Do not coerce booleans/fractions: ``int(True)`` and
            # ``int(1.5)`` could otherwise turn malformed evidence into a
            # seemingly complete graph sweep.  Counts are serialization
            # metadata and must be exact non-boolean integers.
            raw_counts = {
                "expected_graphs": raw_evidence.get("expected_graphs", 0),
                "observed_results": raw_evidence.get("observed_results", 0),
                "passed_graphs": raw_evidence.get("passed_graphs", 0),
            }
            if any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in raw_counts.values()
            ):
                raise ValueError("graph_lowering_evidence counts must be integers")
            expected = raw_counts["expected_graphs"]
            observed = raw_counts["observed_results"]
            passed = raw_counts["passed_graphs"]
            full_graph = bool(raw_evidence.get("full_graph", False))
            if expected <= 0 or observed < 0 or passed < 0 or passed > observed:
                raise ValueError("graph_lowering_evidence contains invalid graph counts")
            if full_graph and (observed != expected or passed != expected or not bool(raw_evidence.get("inventory_complete", False))):
                raise ValueError("full graph evidence requires complete inventory and all graphs passed")
    normalized = dict(payload)
    normalized["schema_version"] = CUDA_BRIDGE_MANIFEST_SCHEMA
    normalized["backend"] = "cuda"
    normalized["runtime_sms"] = sorted((_manifest_target_value(item) for item in runtime_sms), key=str)
    normalized["custom_runtime_sms"] = sorted((_manifest_target_value(item) for item in custom_sms), key=str)
    normalized["graph_lowering_sms"] = sorted((_manifest_target_value(item) for item in graph_sms), key=str)
    normalized["native_runtime_sms"] = sorted((_manifest_target_value(item) for item in native_sms), key=str)
    if graph_evidence is not None:
        normalized["graph_lowering_evidence"] = dict(graph_evidence)
    return normalized


def load_bridge_manifest(bridge_path: object | None = None) -> Optional[dict[str, object]]:
    """Load a validated bridge sidecar, returning ``None`` when absent.

    Invalid manifests are intentionally ignored by the capability layer.  A
    malformed sidecar must quarantine the target instead of enabling a
    backend based on untrusted metadata.
    """

    path = bridge_manifest_path(bridge_path)
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        normalized = validate_bridge_manifest(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError):
        return None
    normalized["manifest_path"] = str(path)
    return normalized


def bridge_target_status(
    value: object,
    manifest: Optional[Mapping[str, object]] = None,
) -> str:
    """Return ``native``, ``runtime_candidate``, or ``unknown`` for one SM."""

    if manifest is None:
        return "unknown"
    target = normalize_cuda_target(value)
    native = _manifest_target_tokens(manifest.get("native_runtime_sms"), "native_runtime_sms")
    runtime = _manifest_target_tokens(manifest.get("runtime_sms"), "runtime_sms")
    graph = _manifest_target_tokens(manifest.get("graph_lowering_sms"), "graph_lowering_sms")
    if target in native:
        return "native"
    # Maxwell 5.0 requires explicit graph evidence; merely compiling the
    # generic runtime is insufficient because old TCMs may still contain
    # dynamic alloca.  Other SMs retain the historical runtime-candidate
    # meaning until their device run is available.
    if target in runtime and (target.compute_capability != 50 or target in graph):
        return "runtime_candidate"
    return "unknown"


def write_bridge_manifest(
    path: os.PathLike[str] | str,
    *,
    runtime_sms: Iterable[object],
    custom_runtime_sms: Iterable[object] = (),
    graph_lowering_sms: Iterable[object] = (),
    graph_lowering_evidence: Optional[Mapping[object, Mapping[str, object]]] = None,
    native_runtime_sms: Iterable[object] = (),
    toolchain: Optional[Mapping[str, object]] = None,
    target: Optional[Mapping[str, object]] = None,
    production: bool = False,
) -> Path:
    """Write an auditable CUDA bridge sidecar after a successful build."""

    raw_payload: dict[str, object] = {
        "schema_version": CUDA_BRIDGE_MANIFEST_SCHEMA,
        "backend": "cuda",
        "runtime_sms": list(runtime_sms),
        "custom_runtime_sms": list(custom_runtime_sms),
        "graph_lowering_sms": list(graph_lowering_sms),
        "native_runtime_sms": list(native_runtime_sms),
        "toolchain": dict(toolchain or {}),
        "target": dict(target or {}),
        "production": bool(production),
    }
    if graph_lowering_evidence is not None:
        raw_payload["graph_lowering_evidence"] = dict(graph_lowering_evidence)
    payload = validate_bridge_manifest(raw_payload)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def architecture_name(value: object) -> str:
    cc = normalize_compute_capability(value)
    if cc < 20:
        return "Tesla"
    if cc < 30:
        return "Fermi"
    if cc < 50:
        return "Kepler"
    if cc < 60:
        return "Maxwell"
    if cc < 70:
        return "Pascal"
    if cc == 70 or cc == 72:
        return "Volta"
    if cc == 75:
        return "Turing"
    if cc < 87:
        return "Ampere"
    if cc == 87:
        return "Orin/embedded Ampere"
    if cc == 89:
        return "Ada Lovelace"
    if cc == 90:
        return "Hopper"
    if cc in {100, 101, 103, 120, 121}:
        return "Blackwell"
    return "Unknown"


@dataclass(frozen=True)
class CudaArchitectureProfile:
    compute_capability: int
    architecture: str
    sm: str
    ptx: str
    current_taichi_codegen_candidate: bool
    current_taichi_native_optimized: bool
    supports_half2_atomic: bool
    supports_match_sync: bool
    requires_pre_volta_convergence_rules: bool
    notes: tuple[str, ...] = ()
    # Lossless target token.  Existing consumers can continue using the
    # numeric ``compute_capability`` field; newer build reports can distinguish
    # Blackwell variants such as sm_120a from the baseline sm_120.
    target: str = ""

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def profile_for(value: object) -> CudaArchitectureProfile:
    target = normalize_cuda_target(value)
    cc = target.compute_capability
    notes: list[str] = []
    candidate = cc in CURRENT_TAICHI_LLVM20_TARGETS
    # Static target acceptance is not native runtime qualification.  A
    # matching GPU, driver, kernel graph, and strict-backend run are required
    # before this flag may be asserted; this module has no such observation.
    native = False
    if cc in {50, 52, 53}:
        notes.append("Maxwell runtime is unverified; the prebuilt custom runtime artifact is sm_60.")
        if cc == 50:
            notes.append(
                "CC 5.0 full-graph lowering needs regenerated TCMs with static TLS; "
                "runtime bitcode alone is insufficient."
            )
        notes.append("Do not use match.sync/match_any; require convergent warp shuffles.")
    if cc > 86 and cc not in CURRENT_TAICHI_LLVM20_TARGETS:
        candidate = False
        native = False
        notes.append(
            "LLVM20 compiler acceptance alone is insufficient; this SM needs its "
            "own complete TCM lowering sweep and bridge qualification."
        )
    elif cc > 86:
        notes.append(
            "LLVM20 TCM lowering candidate; native runtime still requires a matching "
            "GPU/driver and strict-backend evidence."
        )
    if cc in {89, 90, 100, 101, 103, 120, 121}:
        notes.append("Requires a coherent newer LLVM/NVPTX + CUDA toolchain and hardware test.")
    return CudaArchitectureProfile(
        compute_capability=cc,
        architecture=architecture_name(cc),
        sm=target.sm,
        ptx=target.compute,
        current_taichi_codegen_candidate=candidate,
        current_taichi_native_optimized=native,
        supports_half2_atomic=cc >= 60,
        supports_match_sync=cc >= 70,
        requires_pre_volta_convergence_rules=cc < 70,
        notes=tuple(notes),
        target=target.sm,
    )


def unsupported_features(value: object, features: Iterable[str]) -> tuple[str, ...]:
    """Return feature names that cannot be emitted on a capability."""

    profile = profile_for(value)
    unsupported: list[str] = []
    for feature in features:
        name = str(feature).strip().lower()
        if name in {"half2_atomic", "half2_atomic_add"} and not profile.supports_half2_atomic:
            unsupported.append(name)
        elif name in {"match_sync", "match_any", "match_all"} and not profile.supports_match_sync:
            unsupported.append(name)
        elif name in {"native_blackwell", "sm_120", "compute_120"} and profile.compute_capability != 120:
            unsupported.append(name)
    return tuple(unsupported)


def _run_target_probe(
    executable: str,
    target: object,
    *,
    mode: str,
    timeout: float,
    compiler_bin: Optional[str] = None,
) -> dict[str, object]:
    """Compile a tiny device function for one target without a GPU context."""

    cuda_target = normalize_cuda_target(target)
    profile = profile_for(cuda_target)
    if mode == "clang":
        command = [
            executable,
            f"--cuda-gpu-arch={cuda_target.sm}",
            "--cuda-device-only",
            "-nocudainc",
            "-nocudalib",
            "-S",
            "-x",
            "cuda",
            "-o",
            "-",
            "-",
        ]
        source = 'extern "C" __attribute__((device)) int pixel_refine_probe(int x) { return x + 1; }\n'
    elif mode == "nvcc":
        # ``-x cu`` selects the language for stdin, but nvcc still requires
        # an explicit ``-`` input-file operand.  Without it, a compile-only
        # probe fed through ``subprocess.run(input=...)`` fails with
        # ``No input files specified`` for every otherwise supported SM and
        # incorrectly reports the toolkit as incompatible.
        command = [
            executable,
            "--ptx",
            f"--gpu-architecture={cuda_target.compute}",
            "-x",
            "cu",
            "-o",
            "-",
            "-",
        ]
        if compiler_bin:
            command[1:1] = [f"--compiler-bindir={compiler_bin}"]
        source = 'extern "C" __device__ int pixel_refine_probe(int x) { return x + 1; }\n'
    else:
        raise ValueError(f"unknown compiler probe mode: {mode}")
    try:
        result = subprocess.run(
            command,
            input=source,
            text=True,
            capture_output=True,
            timeout=float(timeout),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "target": cuda_target.sm,
            "compute": cuda_target.compute,
            "ok": False,
            "mode": mode,
            "error": f"{type(exc).__name__}: {exc}",
        }
    output = (result.stdout or "") + (result.stderr or "")
    return {
        "target": cuda_target.sm,
        "compute": cuda_target.compute,
        "ok": result.returncode == 0,
        "mode": mode,
        "returncode": result.returncode,
        "target_marker": next(
            (line.strip() for line in output.splitlines() if ".target" in line), None
        ),
        "diagnostic": output[-2000:],
    }


def probe_compiler_targets(
    executable: str,
    targets: Iterable[object],
    *,
    mode: str = "clang",
    timeout: float = 30.0,
    compiler_bin: Optional[str] = None,
) -> dict[str, object]:
    """Return a compile-only report for an LLVM clang or nvcc executable."""

    path = shutil.which(executable) or executable
    results = [
        _run_target_probe(path, normalize_cuda_target(target), mode=mode, timeout=timeout, compiler_bin=compiler_bin)
        for target in targets
    ]
    # Keep an aggregate next to the per-target diagnostics.  Consumers often
    # used to infer coverage from a non-empty ``results`` list, which was
    # especially misleading when nvcc rejected every target because MSVC was
    # unavailable (or when a newer SM was outside the installed toolkit).
    # This remains compile-only evidence; it never promotes a target to
    # runtime/native qualification.
    passed = [item for item in results if bool(item.get("ok"))]
    failed = [item for item in results if not bool(item.get("ok"))]
    summary = {
        "requested_targets": len(results),
        "passed_targets": len(passed),
        "failed_targets": len(failed),
        "supported_targets": [str(item.get("target")) for item in passed],
        "unsupported_targets": [str(item.get("target")) for item in failed],
        "all_passed": bool(results) and not failed,
        "qualification": "compile_only",
    }
    return {
        "kind": "cuda_compile_only_architecture_probe",
        "compiler": str(path),
        "mode": mode,
        "results": results,
        "summary": summary,
        "native_runtime_tested": False,
        "native_performance_tested": False,
    }


def query_nvidia_smi(executable: str = "nvidia-smi", timeout: float = 10.0) -> list[dict[str, object]]:
    """Query physical NVIDIA devices when a driver is installed.

    An empty list means that no physical NVIDIA device was queryable; it is
    never an emulation result.
    """

    command = [
        executable,
        "--query-gpu=index,name,driver_version,compute_cap,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=float(timeout), check=False)
    except (OSError, subprocess.TimeoutExpired):
        return []
    # A non-zero status means the driver/tool is unavailable or the query was
    # rejected.  Never turn partial stdout from such a call into a physical
    # device claim.
    try:
        returncode = int(getattr(result, "returncode", 1))
    except (TypeError, ValueError):
        return []
    if returncode != 0:
        return []
    records: list[dict[str, object]] = []
    # Use CSV parsing instead of ``split(',')`` because GPU names can contain
    # commas.  Invalid rows are skipped independently; one malformed device
    # must not hide valid rows or crash the settings probe.
    try:
        rows = csv.reader((result.stdout or "").splitlines(), skipinitialspace=True)
    except (TypeError, csv.Error):
        return []
    for fields in rows:
        fields = [str(part).strip() for part in fields]
        if len(fields) < 5:
            continue
        try:
            cc = normalize_compute_capability(fields[3])
            ordinal = int(fields[0])
        except (TypeError, ValueError):
            continue
        # ``nvidia-smi`` ordinals are zero-based and names are mandatory.  A
        # malformed row must never become a physical-device record merely
        # because its compute capability happens to parse correctly.
        if ordinal < 0 or not fields[1] or not fields[2]:
            continue
        memory_mb: int | None
        try:
            memory_mb = int(float(fields[4])) if fields[4] and fields[4].upper() not in {"N/A", "NA", "UNKNOWN"} else None
        except (TypeError, ValueError):
            memory_mb = None
        if memory_mb is not None and memory_mb < 0:
            continue
        records.append({
            "ordinal": ordinal,
            "name": fields[1],
            "driver_version": fields[2],
            "compute_capability": cc,
            # Keep the lossless canonical SM token alongside the legacy
            # numeric field.  This matters for future/variant targets where
            # an integer projection alone cannot distinguish ``sm_120`` from
            # ``sm_120a``.  The query currently returns the baseline numeric
            # capability, so this is diagnostic metadata only and never
            # promotes runtime qualification.
            "target": sm_name(cc),
            "architecture": architecture_name(cc),
            "memory_mb": memory_mb,
            "physical_device": True,
        })
    return records


def simulate_cuda_device(value: object, *, driver_version: str = "simulated", memory_mb: int | None = None) -> dict[str, object]:
    """Return deterministic architecture metadata for offline matrix tests.

    This is intentionally *not* an emulator: it does not create a CUDA
    context, execute kernels, or claim driver/performance support.  The
    returned record is marked ``physical_device=False`` and
    ``qualification='compile_only'`` so reports cannot accidentally promote
    simulated results to native qualification.
    """

    target = normalize_cuda_target(value)
    return {
        "ordinal": None,
        "name": f"Simulated {architecture_name(target.compute_capability)} ({target.sm})",
        "driver_version": str(driver_version),
        "compute_capability": target.compute_capability,
        "target": target.sm,
        "architecture": architecture_name(target.compute_capability),
        "memory_mb": memory_mb,
        "physical_device": False,
        "simulated": True,
        "qualification": "compile_only",
        "native_runtime_tested": False,
        "native_performance_tested": False,
    }


def _parse_targets(raw: str) -> list[CudaTarget]:
    """Parse numeric and variant target tokens without losing suffixes."""

    # Keep order stable for reproducible reports, but do not run a duplicate
    # lowering sweep when callers combine a family alias with its canonical
    # token (for example ``120,sm_120``).
    targets: list[CudaTarget] = []
    seen: set[CudaTarget] = set()
    for item in str(raw).split(","):
        if not item.strip():
            continue
        target = normalize_cuda_target(item)
        if target not in seen:
            targets.append(target)
            seen.add(target)
    return targets


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clang", help="clang executable for compile-only probe")
    parser.add_argument("--nvcc", help="nvcc executable for compile-only probe")
    parser.add_argument("--compiler-bin", help="MSVC compiler directory for nvcc")
    parser.add_argument("--targets", default="50,52,53,60,61,70,75,80,86,89,90,120")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--query-driver", action="store_true")
    parser.add_argument(
        "--write-bridge-manifest",
        type=Path,
        help="write a validated CUDA bridge sidecar instead of only printing the probe",
    )
    parser.add_argument(
        "--runtime-sms",
        default="",
        help="comma-separated runtime SMs for --write-bridge-manifest",
    )
    parser.add_argument(
        "--custom-runtime-sms",
        default="",
        help="comma-separated custom-runtime SMs for --write-bridge-manifest",
    )
    parser.add_argument(
        "--graph-lowering-sms",
        default="",
        help=(
            "comma-separated SMs whose generated TCM/IR graphs passed static "
            "lowering; required for CC 5.0 manifest routing"
        ),
    )
    parser.add_argument(
        "--native-runtime-sms",
        default="",
        help="comma-separated physically validated SMs for --write-bridge-manifest",
    )
    parser.add_argument("--llvm-major", type=int)
    parser.add_argument("--clang-version", default="")
    parser.add_argument("--cuda-toolkit", default="")
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args(argv)
    report: dict[str, object] = {"profiles": [profile_for(cc).as_dict() for cc in _parse_targets(args.targets)]}
    if args.clang:
        report["clang"] = probe_compiler_targets(args.clang, _parse_targets(args.targets), mode="clang")
    if args.nvcc:
        report["nvcc"] = probe_compiler_targets(
            args.nvcc,
            _parse_targets(args.targets),
            mode="nvcc",
            compiler_bin=args.compiler_bin,
        )
    if args.query_driver:
        report["devices"] = query_nvidia_smi()
    if args.write_bridge_manifest:
        runtime_sms = _parse_targets(args.runtime_sms) if args.runtime_sms else _parse_targets(args.targets)
        custom_sms = _parse_targets(args.custom_runtime_sms) if args.custom_runtime_sms else []
        graph_sms = _parse_targets(args.graph_lowering_sms) if args.graph_lowering_sms else []
        native_sms = _parse_targets(args.native_runtime_sms) if args.native_runtime_sms else []
        toolchain = {
            key: value
            for key, value in {
                "llvm_major": args.llvm_major,
                "clang_version": args.clang_version or None,
                "cuda_toolkit": args.cuda_toolkit or None,
            }.items()
            if value is not None
        }
        manifest_path = write_bridge_manifest(
            args.write_bridge_manifest,
            runtime_sms=runtime_sms,
            custom_runtime_sms=custom_sms,
            graph_lowering_sms=graph_sms,
            native_runtime_sms=native_sms,
            toolchain=toolchain,
            target={"arch": "x86_64", "os": "windows", "vendor": "nvidia"},
            production=args.production,
        )
        report["bridge_manifest"] = str(manifest_path)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    raise SystemExit(main())
