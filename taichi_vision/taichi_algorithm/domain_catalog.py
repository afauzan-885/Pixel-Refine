"""Auditable inventory for the panorama/HDR/focus/3D domain APIs.

The catalog is intentionally source-oriented: an entry is marked ``available``
only when its family module and callable are present.  It does not infer
native GPU support from a similarly named wrapper or from a compiled artifact.
This makes the remaining reference-only and pending stages visible to the
application instead of silently claiming that a broad algorithm checklist is
complete.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import ast
import importlib
from pathlib import Path
from typing import Any, Sequence


@dataclass(frozen=True)
class AlgorithmSpec:
    name: str
    family: str
    module: str
    callable: str
    backend: str
    status: str = "available"
    notes: str = ""


# These are the concrete stages used by the family workflows, not a second
# implementation list.  Existing AOT leaves are referenced directly; new
# orchestration/reference stages are labelled accordingly.
ALGORITHM_CATALOG: tuple[AlgorithmSpec, ...] = (
    AlgorithmSpec("phase_correlation", "alignment", "taichi_vision.taichi_algorithm.alignment.phase_correlation", "phase_correlation", "aot", notes="Requires the target-qualified phase-correlation artifact; audit_aot_matrix.py is authoritative per target"),
    AlgorithmSpec(
        "OFB_keypoints",
        "alignment",
        "taichi_vision.taichi_algorithm.feature_matching.ofb",
        "detect_ofb_keypoints",
        "taichi-jit",
        notes=(
            "The standalone detector wrapper executes the maintained CPU/GPU "
            "JIT kernels; the public aot_api.ofb matcher composes the "
            "target-qualified OFB graphs and fails closed when its artifact "
            "is unavailable"
        ),
    ),
    AlgorithmSpec(
        "AKAZE_descriptors",
        "alignment",
        "taichi_vision.taichi_algorithm.feature_matching.akaze",
        "compute_descriptors_kernel",
        "taichi-jit",
        notes=(
            "This catalog entry is the raw JIT descriptor kernel.  The public "
            "aot_api.akaze matcher reuses the target-qualified AKAZE graphs; "
            "a standalone descriptor call is not an AOT runtime claim"
        ),
    ),
    AlgorithmSpec("RANSAC_homography", "alignment", "taichi_vision.taichi_algorithm.alignment.quality", "choose_best_transform", "numpy-reference", notes="AOT RANSAC leaf remains available separately"),
    AlgorithmSpec("TPS_refinement", "alignment", "taichi_vision.taichi_algorithm.alignment.tps", "fit_tps_checked", "numpy-reference"),
    AlgorithmSpec("APAP_refinement", "alignment", "taichi_vision.taichi_algorithm.alignment.apap", "fit_apap", "numpy-reference"),
    AlgorithmSpec("planar_stitch", "panorama", "taichi_vision.taichi_algorithm.panorama.stitch", "stitch_panorama", "aot-or-numpy"),
    AlgorithmSpec("sparse_to_dense_warp", "panorama", "taichi_vision.taichi_algorithm.panorama.stitch", "sparse_to_dense_warp", "aot-or-numpy", notes="TPS/APAP maps are evaluated by the caller; AOT remap/remap_with_flow leaves handle dense sampling"),
    AlgorithmSpec("cylindrical_projection", "panorama", "taichi_vision.taichi_algorithm.panorama.projection", "cylindrical_projection", "aot-or-taichi-jit-or-numpy", notes="AOT composes host inverse-map construction with the qualified remap leaf"),
    AlgorithmSpec("spherical_projection", "panorama", "taichi_vision.taichi_algorithm.panorama.projection", "spherical_projection", "aot-or-taichi-jit-or-numpy", notes="AOT composes host inverse-map construction with the qualified remap leaf"),
    AlgorithmSpec("equirectangular_projection", "panorama", "taichi_vision.taichi_algorithm.panorama.projection", "equirectangular_projection", "aot-or-taichi-jit-or-numpy", notes="AOT composes host inverse-map construction with the qualified remap leaf"),
    AlgorithmSpec("exposure_compensation", "panorama", "taichi_vision.taichi_algorithm.panorama.exposure", "compensate_exposure", "taichi-jit-or-numpy", notes="JIT sufficient-statistics reduction and affine apply"),
    AlgorithmSpec("dynamic_programming_seam", "panorama", "taichi_vision.taichi_algorithm.panorama.seam", "dynamic_programming_seam", "taichi-jit-or-numpy", notes="JIT energy; deterministic DP control flow remains host"),
    AlgorithmSpec("graph_cut_seam_surrogate", "panorama", "taichi_vision.taichi_algorithm.panorama.seam", "graph_cut_surrogate", "taichi-jit-or-numpy", notes="bounded surrogate; not a max-flow claim"),
    AlgorithmSpec("graph_cut_maxflow_seam", "panorama", "taichi_vision.taichi_algorithm.panorama.seam", "graph_cut_maxflow", "aot-hybrid-or-taichi-jit-or-numpy", notes="exact bounded float64 host max-flow; target-qualified AOT/JIT unary maps compose with the same deterministic host solver; stale targets fail closed"),
    AlgorithmSpec("HDR_laplacian_fusion", "hdr", "taichi_vision.taichi_algorithm.aot_api.research_pipeline", "hdr_fuse_aot", "aot", notes="Target-qualified hdr TCM required; no cross-target CPU fallback"),
    AlgorithmSpec(
        "HDR_deghost_confidence",
        "hdr",
        "taichi_vision.taichi_algorithm.image_processing.hdr_stack",
        "deghost_confidence",
        "aot-hybrid-or-taichi-jit-or-numpy",
        notes=(
            "The residual leaf is target-qualified on CPU x86_64 Windows and "
            "Vulkan NVIDIA Windows; "
            "percentile/MAD thresholding and smoothing remain bounded host policy. "
            "Other targets fail closed until their HDR artifact is regenerated."
        ),
    ),
    AlgorithmSpec(
        "Debevec_response",
        "hdr",
        "taichi_vision.taichi_algorithm.image_processing.hdr_response",
        "estimate_response_curve",
        "aot-hybrid-or-taichi-jit-or-numpy",
        notes=(
            "Taichi JIT quantises/assembles bounded samples; bounded Debevec "
            "least-squares remains host NumPy and is reported as "
            "ResponseCalibration.solver_backend"
        ),
    ),
    AlgorithmSpec(
        "Robertson_response",
        "hdr",
        "taichi_vision.taichi_algorithm.image_processing.hdr_response",
        "estimate_response_curve_robertson",
        "aot-hybrid-or-taichi-jit-or-numpy",
        notes=(
            "Explicit bounded Robertson alternating update; target-qualified "
            "HDR AOT performs sample quantisation while float64 reductions and "
            "the alternating solver remain host-side."
        ),
    ),
    AlgorithmSpec("radiance_merge", "hdr", "taichi_vision.taichi_algorithm.image_processing.hdr_response", "merge_radiance", "aot-hybrid-or-taichi-jit-or-numpy", notes="AOT weighted/log merge leaves; calibration solver remains host-bounded"),
    AlgorithmSpec(
        "Reinhard_tone_map",
        "hdr",
        "taichi_vision.taichi_algorithm.image_processing.tone_mapping",
        "reinhard_tone_map",
        "taichi-jit-or-numpy",
        notes=(
            "The family-local callable is CPU/GPU JIT-only; AOT tone mapping "
            "is exposed separately through aot_api.research_pipeline and its "
            "qualified TCM leaves"
        ),
    ),
    AlgorithmSpec("focus_Tenengrad", "focus", "taichi_vision.taichi_algorithm.focus_stack.measures", "focus_measure", "aot", notes="Derivative leaves require a target-qualified gradients artifact"),
    AlgorithmSpec("focus_Laplacian", "focus", "taichi_vision.taichi_algorithm.focus_stack.measures", "focus_measure", "aot", notes="Derivative leaves require a target-qualified gradients artifact"),
    AlgorithmSpec("focus_Brenner", "focus", "taichi_vision.taichi_algorithm.focus_stack.measures", "focus_measure", "taichi-jit-or-numpy"),
    AlgorithmSpec("all_in_focus_fusion", "focus", "taichi_vision.taichi_algorithm.focus_stack.pipeline", "focus_stack", "aot-or-taichi-jit-or-numpy", notes="measure leaves can be AOT or explicit Taichi JIT; label/fusion host orchestration"),
    AlgorithmSpec(
        "five_point_essential",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.five_point_solver",
        "solve_five_point",
        "aot-hybrid-or-numpy",
        notes=(
            "AOT mode dispatches the qualified sfm_build_5pt_system_f32 leaf "
            "before the canonical host candidate solve; JIT mode remains the "
            "full NumPy/OpenCV reference"
        ),
    ),
    AlgorithmSpec(
        "cheirality_pose",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.cheirality_check",
        "check_cheirality_full",
        "numpy-reference",
        notes="The public pose contract is host-side; sfm_cheirality_*_aot leaves expose validation arrays only",
    ),
    AlgorithmSpec(
        "adaptive_triangulation",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.triangulation",
        "triangulate_adaptive",
        "numpy-reference",
        notes="The public adaptive solver is host-side; sfm_triangulate_adaptive_aot is a lower-level hybrid leaf",
    ),
    AlgorithmSpec("pairwise_SfM", "sfm", "taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline", "reconstruct_pair", "numpy-reference", notes="Complete pose selection is host-side; backend='aot' fails closed until a complete qualified solver graph exists"),
    AlgorithmSpec("sequence_pose_graph", "sfm", "taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline", "reconstruct_sequence", "numpy-reference", notes="Sequence orchestration composes the host pairwise solver; lower-level AOT geometry leaves are explicit"),
    AlgorithmSpec("plane_sweep_MVS", "sfm", "taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline", "run_plane_sweep_mvs", "aot-or-taichi-jit-or-numpy", notes="AOT reuses sfm_stereo cost/winner/refine leaves; host orchestration remains"),
    AlgorithmSpec("SGM_MVS", "sfm", "taichi_vision.taichi_algorithm.sfm.mvs_regularization", "run_sgm_mvs", "aot-hybrid-or-taichi-jit-or-numpy", notes="Target-qualified sfm_stereo artifacts execute each SGM path natively; direction aggregation remains host and stale targets fail closed"),
    AlgorithmSpec("PatchMatch_MVS", "sfm", "taichi_vision.taichi_algorithm.sfm.mvs_regularization", "run_patchmatch_mvs", "aot-hybrid-or-taichi-jit-or-numpy", notes="Target-qualified sfm_stereo artifacts execute deterministic propagation natively; host controls iteration sequencing and stale targets fail closed"),
    AlgorithmSpec("bundle_adjustment", "sfm", "taichi_vision.taichi_algorithm.aot_api.research_pipeline", "bundle_adjust_lm_aot", "aot", notes="Target-qualified sfm_bundle artifact required; host Schur solve/orchestration remains explicit"),
    AlgorithmSpec("point_cloud_filter_normals", "sfm", "taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline", "run_point_cloud_pipeline", "aot-or-numpy"),
    AlgorithmSpec(
        "point_to_plane_ICP",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.registration",
        "point_to_plane_icp",
        "aot-or-taichi-jit-or-numpy",
        notes="AOT accumulator is qualified on CPU Windows and Vulkan NVIDIA artifacts; other targets remain fail-closed",
    ),
    AlgorithmSpec(
        "TSDF_fusion",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.registration",
        "integrate_tsdf",
        "aot-or-taichi-jit-or-numpy",
        notes="AOT integration is qualified on CPU Windows and Vulkan NVIDIA artifacts; other targets remain fail-closed",
    ),
    AlgorithmSpec("PnP_quality_gate", "sfm", "taichi_vision.taichi_algorithm.sfm.registration", "solve_pnp_checked", "opencv-reference", notes="explicit reference backend; no fabricated fallback"),
    AlgorithmSpec("Poisson_surface", "sfm", "taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline", "run_point_cloud_pipeline", "aot-or-numpy"),
    AlgorithmSpec(
        "texture_UV_atlas",
        "sfm",
        "taichi_vision.taichi_algorithm.sfm.texture_mapping",
        "rasterize_texture_atlas",
        "aot-or-taichi-jit-or-numpy",
        notes="bounded UV rasteriser; AOT composes host barycentric maps with the target-qualified remap leaf",
    ),
)

# High-level stages that intentionally compose existing target-qualified TCM
# leaves instead of introducing a projection/MVS-specific compiler job.  Keep
# this registry declarative so tests can verify compiler/manifest drift without
# importing the AOT engine or claiming that host orchestration is native.
COMPOSED_AOT_LEAVES: dict[str, tuple[str, ...]] = {
    "cylindrical_projection": ("remap",),
    "spherical_projection": ("remap",),
    "equirectangular_projection": ("remap",),
    # Both direct-map and flow variants are graph names inside one remap TCM.
    "sparse_to_dense_warp": ("remap",),
    "plane_sweep_MVS": ("sfm_stereo",),
    "SGM_MVS": ("sfm_stereo",),
    "PatchMatch_MVS": ("sfm_stereo",),
    "graph_cut_maxflow_seam": ("panorama",),
    # Point-cloud filtering and Poisson meshing are high-level wrappers over
    # the existing research TCM families; the orchestration still performs
    # shape/finite/memory gates on the host and never silently falls back.
    "point_cloud_filter_normals": ("sfm_point_cloud",),
    "Poisson_surface": ("sfm_poisson",),
    "point_to_plane_ICP": ("sfm_registration",),
    "TSDF_fusion": ("sfm_registration",),
    "texture_UV_atlas": ("remap",),
}

# Explicit gaps that must not be mistaken for the reference implementations
# above.  They require new target-qualified graphs (and parity evidence) before
# their backend can be advertised as target-qualified native AOT.  Several
# now have explicit CPU-JIT implementations; the AOT artifact distinction is
# kept separate so the catalog never upgrades a JIT parity result into an AOT
# support claim.
PENDING_NATIVE_CAPABILITIES: tuple[str, ...] = (
    "aot_projection_coordinate_map",
    "aot_graph_cut_dynamic_solver",
    "aot_Debevec_Robertson_response_solve",
    # CPU Windows/Vulkan NVIDIA artifacts are qualified; remaining target
    # profiles are intentionally fail-closed until their own artifacts exist.
    "aot_point_to_plane_ICP",
    "aot_TSDF_volume_integration",
    # The UV workflow has a qualified composed remap path; only a standalone
    # all-native atlas graph remains pending.
    "aot_texture_UV_mapping",
)


def audit_catalog(specs: Sequence[AlgorithmSpec] = ALGORITHM_CATALOG) -> dict[str, Any]:
    """Resolve catalog entries and return a serialisable capability report."""

    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    backend_counts: dict[str, int] = {}
    for item in specs:
        available = False
        error = ""
        try:
            module = importlib.import_module(item.module)
            available = callable(getattr(module, item.callable))
            if not available:
                error = "callable is missing"
        except Exception as exc:  # diagnostics must not hide unrelated imports
            error = f"{type(exc).__name__}: {exc}"
        status = item.status if available else "missing"
        counts[status] = counts.get(status, 0) + 1
        if available:
            backend_counts[item.backend] = backend_counts.get(item.backend, 0) + 1
        entry = asdict(item)
        entry.update({"available": bool(available), "resolved_status": status})
        if error:
            entry["error"] = error
        entries.append(entry)
    legacy_count = None
    legacy_unique_count = None
    try:
        init_path = Path(__file__).with_name("__init__.py")
        tree = ast.parse(init_path.read_text(encoding="utf-8-sig"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
            ):
                names = ast.literal_eval(node.value)
                legacy_count = len(names)
                legacy_unique_count = len(set(names))
                break
    except Exception:
        # The inventory remains useful when a source checkout is packaged
        # without the legacy facade's source file.
        pass
    return {
        "total": len(entries),
        "counts": counts,
        "backend_counts": backend_counts,
        "legacy_public_export_count": legacy_count,
        "legacy_unique_export_count": legacy_unique_count,
        "pending_native_capabilities": list(PENDING_NATIVE_CAPABILITIES),
        "entries": entries,
    }


__all__ = [
    "AlgorithmSpec",
    "ALGORITHM_CATALOG",
    "COMPOSED_AOT_LEAVES",
    "PENDING_NATIVE_CAPABILITIES",
    "audit_catalog",
]
