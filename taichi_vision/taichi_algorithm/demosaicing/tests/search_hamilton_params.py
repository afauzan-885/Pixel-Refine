"""Coordinate-descent search for the Hamilton tuning constants.

The search runs against the float64 NumPy model (``hamilton_reference.py``)
rather than the AOT graph, because a graph evaluation costs a TCM compile and a
device round trip.  The model is validated against the compiled graph by
``compare_hamilton_model.py``; a candidate that wins here is only ever adopted
after it has been re-measured through the real graph.

Guarding against overfitting is structural, not statistical:

* the **train** scenes drive the descent;
* the **validation** scenes must also improve, and no acceptance metric may
  worsen by more than ``--tolerance`` on them;
* the tuning set is never used to select the final constant.

The objective is a weighted sum of four error terms that all share the same
scale, so no single artifact family can dominate by having larger units.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent


def _load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - repository invariant
        raise ImportError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load_by_path("pixel_refine_harness_search", _HERE / "demosaic_quality_harness.py")
model_module = _load_by_path("pixel_refine_hamilton_reference_search", _HERE / "hamilton_reference.py")

HamiltonParams = model_module.HamiltonParams
hamilton_model = model_module.hamilton_model

TRAIN_SCENES = ("contrast_edges", "color_edges", "repeating_detail", "micro_foliage")
VALIDATION_SCENES = ("star_chart", "micro_foliage_alt", "neutral_chart")

# Terms that make up the objective, with their weights.  Every term is an error,
# so every scene metric below is lower-is-better.  ``halo_rate`` is included
# because an earlier search pass reduced halo *magnitude* while slightly
# increasing the number of marginally-over-threshold pixels, and a target that
# only weighs magnitude silently accepted that.
OBJECTIVE_TERMS = (
    ("mae", 1.0),
    ("chroma_error_mean", 1.0),
    ("zipper_score", 0.5),
    ("fringing_score", 0.5),
    ("halo_rate", 0.5),
    ("halo_p99", 0.5),
)

# Metrics that must not regress on validation, beyond the shared tolerance.
GUARD_METRICS = tuple(metric for metric, _ in OBJECTIVE_TERMS)

# Per-parameter candidate values.  Defaults reproduce the compiled constants.
SEARCH_SPACE = (
    ("direction_primary", (2.0, 2.5, 3.0, 3.5, 4.5)),
    ("direction_secondary", (1.0, 1.5, 2.0, 2.5, 3.0)),
    ("green_weight_floor", (0.002, 0.01, 0.03, 0.1)),
    ("texture_offset", (2.0, 3.0, 4.0, 6.0)),
    ("texture_scale", (0.15, 0.25, 0.4)),
    ("chroma_weight_floor", (0.001, 0.005, 0.015, 0.05)),
    ("opponent_offset", (0.005, 0.015, 0.03, 0.06)),
    ("opponent_scale", (0.08, 0.155, 0.25)),
    ("opponent_texture_offset", (0.08, 0.16, 0.24)),
    ("opponent_texture_scale", (0.2, 0.39, 0.6)),
    ("highlight_knee", (0.45, 0.55, 0.65)),
    ("highlight_scale", (0.3, 0.43, 0.6)),
    ("neutrality_offset", (0.3, 0.4, 0.5)),
    ("neutrality_scale", (0.3, 0.45, 0.6)),
)

QUICK_PARAMETERS = (
    "direction_primary",
    "direction_secondary",
    "chroma_weight_floor",
    "opponent_offset",
    "opponent_scale",
    "texture_offset",
)


def build_suite(size: int, sensor) -> dict:
    """Render every scene once; the mosaics and references are reused."""

    suite = {}
    for group, names in (("train", TRAIN_SCENES), ("validation", VALIDATION_SCENES)):
        suite[group] = {}
        for name in names:
            factory = harness.SCENE_LIBRARY.get(name) or harness.HELD_OUT_SCENES[name]
            scene = factory(size)
            frame = harness.render_frame(scene, sensor)
            suite[group][name] = {
                "bayer": frame.bayer,
                "reference": harness.output_transfer(frame.optical),
                "achromatic": name in harness.ACHROMATIC_SCENES,
            }
    return suite


def evaluate(params: HamiltonParams, suite: dict, group: str) -> dict:
    metrics = {}
    for name, entry in suite[group].items():
        output = hamilton_model(entry["bayer"], (1.0, 1.0, 1.0, 1.0), 0.0, 1.0, (0, 1, 3, 2), params)
        metrics[name] = harness.metric_bundle(
            entry["reference"], output, achromatic=entry["achromatic"]
        )
    return metrics


def objective(metrics: dict) -> float:
    return float(
        np.mean(
            [
                sum(weight * scene[metric] for metric, weight in OBJECTIVE_TERMS)
                for scene in metrics.values()
            ]
        )
    )


def guard_regressions(base: dict, candidate: dict, tolerance: float) -> list[dict]:
    """Return validation metrics that worsened beyond the relative tolerance."""

    regressions = []
    for scene, base_metrics in base.items():
        if scene not in candidate:
            continue
        for metric in GUARD_METRICS:
            before = base_metrics.get(metric)
            after = candidate[scene].get(metric)
            if before is None or after is None or before == 0.0:
                continue
            relative = (after - before) / abs(before)
            if relative > tolerance:
                regressions.append(
                    {
                        "scene": scene,
                        "metric": metric,
                        "baseline": float(before),
                        "candidate": float(after),
                        "relative": float(relative),
                    }
                )
    return regressions


def search(suite: dict, base_params: HamiltonParams, passes: int, tolerance: float, parameters):
    base_train = evaluate(base_params, suite, "train")
    base_validation = evaluate(base_params, suite, "validation")
    best_params = base_params
    best_score = objective(base_train)
    best_train, best_validation = base_train, base_validation
    history = []

    print(f"start objective={best_score:.6f}")
    for pass_index in range(passes):
        for name, values in SEARCH_SPACE:
            if name not in parameters:
                continue
            for value in values:
                if getattr(best_params, name) == value:
                    continue
                candidate = HamiltonParams(**{**best_params.__dict__, name: value})
                train = evaluate(candidate, suite, "train")
                score = objective(train)
                if score >= best_score:
                    continue
                validation = evaluate(candidate, suite, "validation")
                regressions = guard_regressions(base_validation, validation, tolerance)
                if regressions:
                    continue
                print(
                    f"  pass{pass_index} {name}={value} objective {best_score:.6f} -> "
                    f"{score:.6f} (validation clean)"
                )
                history.append(
                    {
                        "pass": pass_index,
                        "parameter": name,
                        "value": value,
                        "objective": score,
                    }
                )
                best_params = candidate
                best_score = score
                best_train, best_validation = train, validation
    return best_params, best_score, best_train, best_validation, history


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=192)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--clean-sensor", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    sensor = (
        harness.SensorModel(psf_sigma=0.0, ca_strength=0.0, full_well=0.0, read_noise_e=-1.0)
        if args.clean_sensor
        else harness.SensorModel()
    )
    parameters = QUICK_PARAMETERS if args.quick else tuple(name for name, _ in SEARCH_SPACE)

    started = time.perf_counter()
    suite = build_suite(args.size, sensor)
    print(f"suite built in {time.perf_counter() - started:.1f}s size={args.size}")

    best_params, best_score, train, validation, history = search(
        suite, HamiltonParams(), args.passes, args.tolerance, parameters
    )

    base_params = HamiltonParams()
    base_train = evaluate(base_params, suite, "train")
    base_validation = evaluate(base_params, suite, "validation")

    report = {
        "size": args.size,
        "passes": args.passes,
        "tolerance": args.tolerance,
        "parameters_searched": list(parameters),
        "objective_baseline": objective(base_train),
        "objective_best": best_score,
        "objective_validation_baseline": objective(base_validation),
        "objective_validation_best": objective(validation),
        "params_baseline": base_params.__dict__,
        "params_best": best_params.__dict__,
        "history": history,
        "train_baseline": base_train,
        "train_best": train,
        "validation_baseline": base_validation,
        "validation_best": validation,
    }
    print(
        f"\nobjective train {report['objective_baseline']:.6f} -> {best_score:.6f} "
        f"({(1 - best_score / report['objective_baseline']) * 100:.1f}% better)"
    )
    print(
        f"objective validation {report['objective_validation_baseline']:.6f} -> "
        f"{report['objective_validation_best']:.6f}"
    )
    print(f"winning parameters: {best_params}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
