"""Measure demosaic quality, latency, and memory on synthetic and real captures.

This is the CLI half of the quality harness: ``demosaic_quality_harness`` owns
the metrics, the scene library, and the sensor model, while this module owns
device execution, metadata extraction, and reporting.

Method notes that matter for interpreting a report:

* Full-frame execution is timed (``return_gpu=True``), because full-frame is the
  correctness oracle.  The compute-block path has its own parity probe
  (``aot_py/tests/stress_demosaic_block_parity.py``), and block parity must be
  re-checked separately whenever a kernel changes.
* The scoring reference for a synthetic scene is the **optical** image returned
  by ``render_frame`` -- after the lens PSF and chromatic aberration, before
  mosaicing -- never the sharp scene.  Scoring against the sharp scene would
  reward ringing.
* The "beat RawPy AHD" comparison is only computed for synthetic ground-truth
  scenes, where both reconstructions can be compared against the same reference
  in the same transfer domain.  On real captures only ground-truth-free metrics
  are reported, and they are meaningful as a comparison against a stored
  baseline of the same frame, not as absolute numbers.
* Sensor metadata is extracted exactly as ``aot_api.demosaic`` does it for a
  path or rawpy object (see ``_extract_from_raw`` there), including the G2
  fallback to G1, the green-average gain normalisation, the single-channel black
  level, and ``raw_colors`` for the Bayer phase.  ``--verify-extraction`` proves
  the mirror agrees by running the public dispatcher on the same file and
  requiring an identical result.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_HERE = Path(__file__).resolve().parent


def _load_by_path(name: str, path: Path):
    """Import a module by file path so pure libraries need no package import."""

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - repository invariant
        raise ImportError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load_by_path(
    "pixel_refine_demosaic_quality_harness", _HERE / "demosaic_quality_harness.py"
)
adversarial = _load_by_path(
    "pixel_refine_demosaic_adversarial", _HERE / "benchmark_demosaic_adversarial.py"
)

METHODS = ("hamilton", "arm", "dcb", "mlri_admm", "bilinear")

# Metrics that a gate should check per method and scene.  Keeping this list
# explicit prevents a new metric from silently entering or leaving the gate.
GATE_METRICS = (
    "mae",
    "psnr_db",
    "p99_abs",
    "false_pixel_rate",
    "edge_mae",
    "chroma_error_mean",
    "chroma_error_p99",
    "edge_chroma_error",
    "false_chroma_mean",
    "false_chroma_p99",
    "edge_false_chroma",
    "halo_energy",
    "halo_p99",
    "halo_rate",
    "zipper_score",
    "fringing_score",
)

# Margin excluded from a cropped real-capture evaluation.  It is wider than
# Hamilton's three-pixel stencil so a clamped crop border cannot contaminate a
# metric, and even so the CFA phase is preserved.
CROP_MARGIN = 8

GT_FREE_METRICS = (
    "sample_site_fidelity_mean",
    "sample_site_fidelity_max",
    "sample_site_fidelity_p99",
    "cfa_halo_energy",
    "cfa_halo_p99",
    "cfa_halo_rate",
    "chroma_hp_energy",
    "chroma_hp_p99",
    "cfa_checkerboard_chroma",
    "cfa_checkerboard_chroma_p99",
)


def configure_backend(backend: str) -> None:
    """Select the backend before the first Taichi import."""

    os.environ["PIXEL_REFINE_AOT_ARCH"] = backend
    os.environ["AOT_ARCH"] = backend


def _import_api():
    from taichi_vision import taichi_aot

    return taichi_aot


def scalar_tuple(wb, cmatrix, black, white, cfa):
    """Build the positional argument tuple the demosaic graphs expect."""

    wb_r, wb_g1, wb_b, wb_g2 = (float(value) for value in wb)
    return (
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        np.ascontiguousarray(cmatrix, dtype=np.float32),
        float(black),
        float(white),
        int(cfa[0]),
        int(cfa[1]),
        int(cfa[2]),
        int(cfa[3]),
    )


def memory_snapshot(status_provider=None) -> dict:
    """Report host resident memory and, when available, engine telemetry.

    ``status_provider`` is a zero-argument callable returning the engine memory
    dictionary; the facade exposes ``get_memory_status`` but not necessarily the
    engine object itself, so the caller supplies the accessor.
    """

    import psutil

    snapshot = {"rss_bytes": int(psutil.Process().memory_info().rss)}
    if status_provider is None:
        return snapshot
    try:
        status = status_provider()
    except Exception as exc:  # pragma: no cover - backend dependent
        snapshot["engine_status_error"] = repr(exc)
        return snapshot
    for key in (
        "resident_bytes",
        "resident_limit",
        "lifecycle_bytes",
        "resident_over_limit",
    ):
        if isinstance(status, dict) and key in status:
            snapshot[key] = status[key]
    return snapshot


def status_provider_for(api):
    """Build the engine-memory accessor from the public facade."""

    getter = getattr(api, "get_memory_status", None)
    if getter is None:
        return None

    def provider():
        return getter(force=True)

    return provider


# ---------------------------------------------------------------------------
# Real capture metadata (mirrors aot_api.demosaic._extract_from_raw)
# ---------------------------------------------------------------------------
def extract_sensor_metadata(raw) -> dict:
    """Extract exactly what the public dispatcher extracts from a rawpy object."""

    raw_image = np.asarray(raw.raw_image)
    if raw_image.dtype in (np.dtype(np.uint8), np.dtype(np.uint16)):
        bayer = np.array(raw_image, copy=True)
    else:
        bayer = raw_image.astype(np.float32)

    black_levels = tuple(float(value) for value in raw.black_level_per_channel)
    white_level = float(raw.white_level)

    wb = np.array(raw.camera_whitebalance, dtype=np.float32)
    if wb.size == 4:
        if wb[3] <= 0.01:
            wb[3] = wb[1]
        wb = wb / ((wb[1] + wb[3]) / 2.0)
    else:
        wb = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

    cfa = (
        int(raw.raw_colors[0, 0]),
        int(raw.raw_colors[0, 1]),
        int(raw.raw_colors[1, 0]),
        int(raw.raw_colors[1, 1]),
    )
    cmatrix = raw.color_matrix[:, :3].astype(np.float32)
    return {
        "bayer": bayer,
        "black_level": black_levels[0],
        "black_levels": black_levels,
        "white_level": white_level,
        "gains": tuple(float(value) for value in wb),
        "cfa": cfa,
        "cmatrix": cmatrix,
        "shape": tuple(int(v) for v in bayer.shape),
        "dtype": str(bayer.dtype),
        "black_levels_uniform": len(set(black_levels)) == 1,
    }


def center_crop(bayer: np.ndarray, size: int) -> tuple[np.ndarray, tuple[int, int]]:
    """Crop a centred window on an even offset so the CFA phase is preserved."""

    if size <= 0:
        return bayer, (0, 0)
    height, width = bayer.shape[:2]
    if size >= min(height, width):
        return bayer, (0, 0)
    size -= size % 2
    top = ((height - size) // 2) & ~1
    left = ((width - size) // 2) & ~1
    return bayer[top : top + size, left : left + size], (top, left)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def evaluate_synthetic(api, method: str, size: int, model, scenes: dict, runs: int,
                       compare_ahd: bool) -> dict:
    if model.cfa != "RGGB" and compare_ahd:
        raise RuntimeError(
            "the synthetic DNG writer encodes RGGB; use cfa=RGGB or --no-ahd"
        )

    report = {}
    directory = tempfile.mkdtemp(prefix="pixel-refine-quality-")
    for name, factory in scenes.items():
        scene = factory(size)
        frame = harness.render_frame(scene, model)
        reference = harness.output_transfer(frame.optical, method)
        scalars = scalar_tuple((1.0, 1.0, 1.0, 1.0), np.eye(3), 0.0, 1.0, (0, 1, 3, 2))

        output, timing = harness.run_full_frame(api, method, frame.bayer, scalars, runs=runs)
        entry = {
            "metrics": harness.metric_bundle(
                reference, output, achromatic=name in harness.ACHROMATIC_SCENES
            ),
            "ground_truth_free": harness.ground_truth_free_bundle(
                frame.bayer, output, (0, 1, 3, 2), (1.0, 1.0, 1.0, 1.0)
            ),
            "timing": timing,
        }

        if compare_ahd:
            dng_path = Path(directory) / f"{name}.dng"
            adversarial.write_synthetic_dng(dng_path, frame.bayer)
            started = time.perf_counter()
            ahd_rgb = adversarial.rawpy_ahd(dng_path)
            elapsed = (time.perf_counter() - started) * 1000.0
            entry["rawpy_ahd"] = {
                "metrics": harness.metric_bundle(
                    reference,
                    harness.output_transfer(ahd_rgb, method),
                    achromatic=name in harness.ACHROMATIC_SCENES,
                ),
                "end_to_end_ms": elapsed,
            }
        report[name] = entry
    return report


def evaluate_real(api, method: str, paths, crop: int, runs: int, verify_extraction: bool) -> dict:
    import rawpy

    report = {}
    for path in paths:
        with rawpy.imread(str(path)) as raw:
            meta = extract_sensor_metadata(raw)
        bayer, offset = center_crop(meta["bayer"], crop)
        scalars = scalar_tuple(
            meta["gains"], meta["cmatrix"], meta["black_level"], meta["white_level"], meta["cfa"]
        )

        output, timing = harness.run_full_frame(api, method, bayer, scalars, runs=runs)

        # A cropped window has clamped borders that the full frame does not, so
        # both the metrics and the extraction check are evaluated inside a
        # margin wider than Hamilton's three-pixel stencil.  The margin is even,
        # which keeps the CFA phase intact.
        height, width = bayer.shape[:2]
        margin = CROP_MARGIN if offset != (0, 0) else 0
        inner = (slice(margin, height - margin), slice(margin, width - margin))

        entry = {
            "shape": tuple(int(v) for v in bayer.shape),
            "raw_shape": meta["shape"],
            "dtype": meta["dtype"],
            "cfa": list(meta["cfa"]),
            "gains": list(meta["gains"]),
            "black_level": meta["black_level"],
            "black_levels_uniform": meta["black_levels_uniform"],
            "white_level": meta["white_level"],
            "crop_offset": list(offset),
            "metric_margin": margin,
            "ground_truth_free": harness.ground_truth_free_bundle(
                bayer[inner],
                output[inner],
                meta["cfa"],
                meta["gains"],
                black_level=meta["black_level"],
                white_level=meta["white_level"],
            ),
            "timing": timing,
        }

        if verify_extraction:
            with rawpy.imread(str(path)) as raw:
                # ``return_gpu=True`` keeps the reference full-frame, which is the
                # same path the measured run took; cropping below makes the two
                # arrays comparable element for element.
                reference_output = api.demosaic(raw, method=method, return_gpu=True)
            reference_array = (
                reference_output.to_numpy()
                if hasattr(reference_output, "to_numpy")
                else np.asarray(reference_output)
            )
            if hasattr(reference_output, "release"):
                reference_output.release()
            reference_array = np.asarray(reference_array, dtype=np.float32)
            top, left = offset
            reference_array = reference_array[top : top + height, left : left + width]
            if reference_array.shape != output.shape:
                raise RuntimeError(
                    "extraction verification produced a different shape for "
                    f"{path.name}: reference={reference_array.shape} measured={output.shape}"
                )
            entry["extraction_verified"] = bool(
                np.allclose(reference_array[inner], output[inner], atol=1e-4)
            )
            entry["extraction_max_abs_diff"] = float(
                np.max(np.abs(reference_array[inner] - output[inner]))
            )
            if not entry["extraction_verified"]:
                raise RuntimeError(
                    "the mirrored metadata extraction disagrees with aot_api.demosaic "
                    f"for {path.name} (max_abs_diff={entry['extraction_max_abs_diff']}); "
                    "the ground-truth-free metrics would be invalid"
                )
        report[path.name] = entry
    return report


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------
def gate_report(baseline: dict, candidate: dict, scope: str) -> dict:
    """Compare two reports and list regressions and wins for the given scope."""

    base_section = baseline.get(scope, {})
    cand_section = candidate.get(scope, {})
    regressions = []
    improvements = []

    for scene, base_entry in base_section.items():
        cand_entry = cand_section.get(scene)
        if not cand_entry:
            regressions.append({"scene": scene, "metric": "<scene missing>"})
            continue
        base_metrics = dict(base_entry.get("metrics", {}))
        base_metrics.update(base_entry.get("ground_truth_free", {}))
        cand_metrics = dict(cand_entry.get("metrics", {}))
        cand_metrics.update(cand_entry.get("ground_truth_free", {}))

        for item in harness.compare_scene_metrics(base_metrics, cand_metrics):
            item["scene"] = scene
            regressions.append(item)
        for metric in GATE_METRICS + GT_FREE_METRICS:
            if metric not in base_metrics or metric not in cand_metrics:
                continue
            direction = harness.direction_of(metric)
            delta = cand_metrics[metric] - base_metrics[metric]
            better = delta < 0 if direction == "lower" else delta > 0
            if better and abs(delta) > 1e-9:
                improvements.append(
                    {"scene": scene, "metric": metric, "delta": float(delta)}
                )

    return {
        "scope": scope,
        "regressions": regressions,
        "improvement_count": len(improvements),
        "improvements": improvements[:60],
    }


def beats_ahd(section: dict) -> dict:
    """Report, per scene, whether the method beat RawPy AHD on the key metrics."""

    verdict = {}
    for scene, entry in section.items():
        ahd = entry.get("rawpy_ahd")
        if not ahd:
            continue
        ours, theirs = entry["metrics"], ahd["metrics"]
        verdict[scene] = {
            metric: bool(
                ours[metric] < theirs[metric]
                if harness.direction_of(metric) == "lower"
                else ours[metric] > theirs[metric]
            )
            for metric in (
                "mae",
                "chroma_error_mean",
                "psnr_db",
                "false_pixel_rate",
                "edge_mae",
                "zipper_score",
                "fringing_score",
            )
            if metric in ours and metric in theirs
        }
    return verdict


def summarize(section: dict) -> dict:
    """Aggregate the headline metrics across scenes."""

    names = list(section)
    if not names:
        return {}
    summary = {}
    for method_metrics in ("metrics", "ground_truth_free"):
        # Real captures have no ground-truth group and synthetic scenes have no
        # ground-truth-free group only if the caller skipped it, so a group is
        # aggregated only when every scene actually carries it.
        if not all(method_metrics in section[name] for name in names):
            continue
        available = [
            metric
            for metric in (GATE_METRICS if method_metrics == "metrics" else GT_FREE_METRICS)
            if all(metric in section[name][method_metrics] for name in names)
        ]
        for metric in available:
            summary[f"{method_metrics}.{metric}_mean"] = float(
                np.mean([section[name][method_metrics][metric] for name in names])
            )
    if all("timing" in section[name] for name in names):
        summary["end_to_end_median_ms"] = float(
            np.median([section[name]["timing"]["end_to_end_median_ms"] for name in names])
        )
        summary["dispatch_median_ms"] = float(
            np.median([section[name]["timing"]["dispatch_median_ms"] for name in names])
        )
    for name in names:
        ahd = section[name].get("rawpy_ahd")
        if ahd:
            summary.setdefault("ahd_end_to_end_median_ms", [])
            summary["ahd_end_to_end_median_ms"].append(ahd["end_to_end_ms"])
    if isinstance(summary.get("ahd_end_to_end_median_ms"), list):
        summary["ahd_end_to_end_median_ms"] = float(
            np.median(summary["ahd_end_to_end_median_ms"])
        )
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="cpu")
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["hamilton"],
        help="demosaic methods to score; several may be given",
    )
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--scenes", default="")
    parser.add_argument("--include-held-out", action="store_true")
    parser.add_argument("--no-ahd", action="store_true", help="skip the RawPy AHD comparison")
    parser.add_argument("--clean", action="store_true", help="disable PSF, CA, and noise")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--real-glob", default="test_algorithm/*.dng")
    parser.add_argument("--crop", type=int, default=1024)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-verify-extraction", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--compare", type=Path, help="baseline report to gate against")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    methods = []
    for item in args.methods:
        for piece in item.split(","):
            if piece.strip():
                methods.append(piece.strip())
    unknown = sorted(set(methods) - set(METHODS))
    if unknown:
        parser.error(f"unsupported methods: {', '.join(unknown)}")

    if args.scenes:
        requested = [item.strip() for item in args.scenes.split(",") if item.strip()]
    else:
        requested = list(harness.SCENE_LIBRARY)
    unknown_scenes = sorted(set(requested) - set(harness.SCENE_LIBRARY))
    if unknown_scenes:
        parser.error(f"unsupported scenes: {', '.join(unknown_scenes)}")
    scenes = {name: harness.SCENE_LIBRARY[name] for name in requested}
    if args.include_held_out:
        scenes.update(harness.HELD_OUT_SCENES)

    model = (
        harness.SensorModel(psf_sigma=0.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        if args.clean
        else harness.SensorModel()
    )

    configure_backend(args.backend)
    api = _import_api()
    status_provider = status_provider_for(api)

    report = {
        "schema_version": 1,
        "backend": args.backend,
        "input_mode": "resident",
        "sensor_model": {
            "psf_sigma": model.psf_sigma,
            "ca_strength": model.ca_strength,
            "full_well": model.full_well,
            "read_noise_e": model.read_noise_e,
            "noise_seed": model.noise_seed,
            "cfa": model.cfa,
        },
        "metric_directions": harness.METRIC_DIRECTIONS,
        "methods": {},
    }

    for method in methods:
        before = memory_snapshot(status_provider)
        entry = {"synthetic": {}, "real": {}, "memory_before": before}
        if not args.real:
            entry["synthetic"] = evaluate_synthetic(
                api, method, args.size, model, scenes, max(1, args.runs), not args.no_ahd
            )
        else:
            paths = sorted(Path(ROOT).glob(args.real_glob))
            if args.limit:
                paths = paths[: args.limit]
            if not paths:
                parser.error(f"no captures matched {args.real_glob}")
            entry["real"] = evaluate_real(
                api,
                method,
                paths,
                args.crop,
                max(1, args.runs),
                not args.no_verify_extraction,
            )
        entry["memory_after"] = memory_snapshot(status_provider)
        if entry["synthetic"]:
            entry["synthetic_summary"] = summarize(entry["synthetic"])
            entry["beats_ahd"] = beats_ahd(entry["synthetic"])
        if entry["real"]:
            entry["real_summary"] = summarize(entry["real"])
        report["methods"][method] = entry

    payload = (
        {
            "backend": report["backend"],
            "sensor_model": report["sensor_model"],
            "methods": {
                method: {
                    key: value
                    for key, value in entry.items()
                    if key in {"synthetic_summary", "real_summary", "beats_ahd", "memory_after"}
                }
                for method, entry in report["methods"].items()
            },
        }
        if args.summary_only
        else report
    )

    if args.compare:
        with open(args.compare, "r", encoding="utf-8") as handle:
            baseline = json.load(handle)
        gates = {}
        for method, entry in report["methods"].items():
            base_entry = baseline.get("methods", {}).get(method, {})
            gates[method] = {
                scope: gate_report(base_entry, entry, scope)
                for scope in ("synthetic", "real")
                if entry.get(scope)
            }
        payload["gate"] = gates

    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
