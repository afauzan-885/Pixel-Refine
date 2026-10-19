import os
import subprocess
import sys
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.patch_process.multi_patch import (
    CandidateOffset,
    candidate_flow_from_indices,
    cohere_candidate_selection,
    gather_rank_candidate,
    normalize_weighted_accumulator,
    patch_distance_map,
    search_candidate_offsets,
    select_topk_candidates,
    validity_mask,
)


def _offset(dx, dy):
    return CandidateOffset(
        name=f"offset_{dx}_{dy}",
        dx_full=dx,
        dy_full=dy,
        dx_proxy=dx,
        dy_proxy=dy,
        dx_align=dx,
        dy_align=dy,
    )


def test_search_offsets_are_unique_2d_and_stay_inside_radius():
    offsets = search_candidate_offsets(
        (64, 80),
        (32, 40),
        align_shape=(16, 20),
        search_radius=5,
        patch_stride=2,
    )

    assert len(offsets) == 24
    proxy_points = {(item.dx_proxy, item.dy_proxy) for item in offsets}
    assert len(proxy_points) == len(offsets)
    assert (0, 0) not in proxy_points
    assert all(abs(dx) <= 4 and abs(dy) <= 4 for dx, dy in proxy_points)
    assert len({item.name for item in offsets}) == len(offsets)


def test_raw_search_offsets_preserve_cfa_phase_after_scale_mapping():
    offsets = search_candidate_offsets(
        (64, 64),
        (32, 32),
        align_shape=(16, 16),
        search_radius=5,
        patch_stride=2,
        preserve_cfa_phase=True,
    )

    assert len(offsets) == 24
    assert all(item.dx_full % 2 == 0 and item.dy_full % 2 == 0 for item in offsets)
    assert all(item.dx_proxy == round(item.dx_full * 0.5) for item in offsets)
    assert all(item.dy_proxy == round(item.dy_full * 0.5) for item in offsets)


def test_patch_distance_uses_full_patch_footprint_and_masks_shift_borders():
    reference = np.zeros((11, 13), dtype=np.float32)
    candidate = reference.copy()
    geometric_valid = validity_mask((11, 13), dx=1, dy=0)

    distance, valid = patch_distance_map(
        reference,
        candidate,
        patch_size=5,
        valid_mask=geometric_valid,
    )

    assert valid[2:-2, 2:-3].all()
    assert not valid[:2].any()
    assert not valid[-2:].any()
    assert not valid[:, :2].any()
    assert not valid[:, -3:].any()
    assert np.all(distance[valid] == 0.0)
    assert np.isinf(distance[~valid]).all()


def test_topk_selects_lowest_patch_distance_with_stable_ties():
    height, width = 15, 17
    _, xx = np.mgrid[:height, :width]
    candidate = np.broadcast_to(xx.astype(np.float32), (1, height, width)).copy()
    reference = candidate.copy()
    offsets = (_offset(2, 0), _offset(1, 0), _offset(-1, 0))

    selection = select_topk_candidates(
        reference,
        candidate,
        offsets,
        max_neighbors=3,
        patch_size=5,
    )

    assert selection.indices.shape == (3, height, width)
    assert selection.search_candidate_count == 3
    np.testing.assert_array_equal(selection.indices[:, 7, 8], (1, 2, 0))
    assert selection.valid[:, 7, 8].all()
    assert not selection.valid[:, 0, :].any()
    assert not selection.valid[:, :, -1].any()


def test_topk_ties_are_stable_and_k_is_bounded_by_pool_size():
    reference = np.ones((1, 13, 13), dtype=np.float32)
    offsets = (_offset(-1, 0), _offset(1, 0), _offset(0, -1))
    selection = select_topk_candidates(
        reference,
        reference,
        offsets,
        max_neighbors=8,
        patch_size=5,
    )

    np.testing.assert_array_equal(selection.indices[:, 6, 6], (0, 1, 2))
    assert selection.indices.shape[0] == len(offsets)


def test_coherent_rank_map_reduces_pixelwise_offset_switching_on_flat_raw_proxy():
    rng = np.random.default_rng(20261017)
    height = width = 128
    reference = (
        np.full((1, height, width), 0.5, dtype=np.float32)
        + rng.normal(0, 0.01, (1, height, width))
    ).astype(np.float32)
    support = (
        np.full((1, height, width), 0.5, dtype=np.float32)
        + rng.normal(0, 0.01, (1, height, width))
    ).astype(np.float32)
    offsets = search_candidate_offsets(
        (height * 2, width * 2),
        (height, width),
        search_radius=5,
        patch_stride=2,
        preserve_cfa_phase=True,
    )
    selection = select_topk_candidates(
        reference, support, offsets, max_neighbors=4, patch_size=5
    )
    coherent = cohere_candidate_selection(
        selection, offsets, cell_size=10, patch_size=5
    )

    def horizontal_switch_fraction(rank_map, valid):
        pair_valid = valid[:, 1:] & valid[:, :-1]
        return float(
            np.mean((rank_map[:, 1:] != rank_map[:, :-1])[pair_valid])
        )

    for rank in range(selection.indices.shape[0]):
        original_fraction = horizontal_switch_fraction(
            selection.indices[rank, 2:-2, 2:-2],
            selection.valid[rank, 2:-2, 2:-2],
        )
        coherent_fraction = horizontal_switch_fraction(
            coherent.indices[rank, 2:-2, 2:-2],
            coherent.valid[rank, 2:-2, 2:-2],
        )
        assert coherent_fraction < original_fraction * 0.25
        assert np.all(coherent.indices[rank] >= -1)

    for y0 in range(0, height, 10):
        for x0 in range(0, width, 10):
            y1, x1 = min(height, y0 + 10), min(width, x0 + 10)
            cell_values = coherent.indices[:, y0:y1, x0:x1]
            cell_valid = coherent.valid[:, y0:y1, x0:x1]
            for rank in range(cell_values.shape[0]):
                assert np.all(cell_values[rank][~cell_valid[rank]] == -1)
                assert np.unique(cell_values[rank][cell_valid[rank]]).size <= 1
            if np.all(coherent.valid[:, y0 + 2, x0 + 2]):
                assert len(np.unique(coherent.indices[:, y0 + 2, x0 + 2])) == 4


def test_weightnet_confidence_is_not_scaled_by_patch_distance(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine import (
        weightnet_inference,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import (
        resident_pipeline,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.patch_process.multi_patch import (
        CandidateTelemetry,
    )

    height = width = 11
    reference = np.zeros((1, height, width), dtype=np.float32)
    candidate = reference.copy()
    offsets = (_offset(1, 0),)
    expected_confidence = np.full((1, height, width), 0.73, dtype=np.float32)

    def fixed_weightnet(*_args, **_kwargs):
        return expected_confidence.copy(), 0.6

    monkeypatch.setattr(
        weightnet_inference,
        "infer_single_support_weight_map",
        fixed_weightnet,
    )
    selection = select_topk_candidates(
        reference, candidate, offsets, max_neighbors=1, patch_size=5
    )
    maps = list(
        resident_pipeline._iter_multi_patch_rank_maps(
            object(),
            reference,
            candidate,
            offsets,
            max_neighbors=1,
            tile_size=256,
            overlap=0.2,
            ghost_penalty=1.0,
            ghost_cutoff=0.0,
            chroma_sensitivity=1.0,
            stop_event=None,
            telemetry=CandidateTelemetry(),
            selection=selection,
        )
    )

    assert len(maps) == 1
    _rank_indices, valid, confidence, _alpha = maps[0]
    np.testing.assert_array_equal(confidence[:, valid], expected_confidence[:, valid])
    assert np.all(confidence[:, ~valid] == 0.0)


def test_rank_gather_uses_the_selected_offset_at_each_location():
    source = np.stack(np.mgrid[:7, :8], axis=0).astype(np.float32)
    offsets = (_offset(1, 0), _offset(0, -1))
    rank_indices = np.full((7, 8), -1, dtype=np.int32)
    rank_indices[2:5, 2:5] = 0
    rank_indices[3:6, 4:7] = 1

    gathered, valid = gather_rank_candidate(source, offsets, rank_indices)

    assert valid.sum() == 16
    np.testing.assert_array_equal(gathered[:, 3, 3], source[:, 3, 4])
    np.testing.assert_array_equal(gathered[:, 4, 5], source[:, 3, 5])
    assert not gathered[:, 0, 0].any()


def test_raw_candidate_flow_composes_offsets_with_identity_homography():
    indices = np.zeros((16, 16), dtype=np.int32)
    offsets = (_offset(4, -2),)
    flow = candidate_flow_from_indices(
        indices,
        offsets,
        full_shape=(64, 64),
        flow_shape=(16, 16),
        base_transform=np.eye(3, dtype=np.float32),
    )

    assert flow.shape == (16, 16, 2)
    assert flow.dtype == np.float32
    np.testing.assert_allclose(flow[8, 8], (1.0, -0.5))


def test_raw_candidate_flow_composes_nonidentity_homography_and_dense_flow():
    indices = np.zeros((16, 16), dtype=np.int32)
    offsets = (_offset(4, -2),)
    homography = np.asarray(
        ((1.0, 0.0, 2.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        dtype=np.float32,
    )
    homography_flow = candidate_flow_from_indices(
        indices,
        offsets,
        full_shape=(64, 64),
        flow_shape=(16, 16),
        base_transform=homography,
    )
    np.testing.assert_allclose(homography_flow[8, 8], (0.5, -0.5))

    base_flow = np.empty((16, 16, 2), dtype=np.float32)
    base_flow[...] = (0.25, -0.125)
    dense_flow = candidate_flow_from_indices(
        indices,
        offsets,
        full_shape=(64, 64),
        flow_shape=(16, 16),
        base_transform=base_flow,
    )
    np.testing.assert_allclose(dense_flow[8, 8], (1.25, -0.625))


def test_candidate_flow_with_invalid_rank_has_zero_offset():
    indices = np.full((8, 8), -1, dtype=np.int32)
    flow = candidate_flow_from_indices(
        indices,
        (_offset(4, 2),),
        full_shape=(32, 32),
        flow_shape=(8, 8),
    )
    assert not flow.any()


def test_zero_weight_accumulator_falls_back_to_reference():
    reference = np.arange(24, dtype=np.float32).reshape(2, 4, 3)
    numerator = np.ones_like(reference, dtype=np.float32)
    denominator = np.zeros((2, 4), dtype=np.float32)

    output = normalize_weighted_accumulator(numerator, denominator, reference)

    np.testing.assert_array_equal(output, reference)


def test_candidate_offsets_stop_on_cancellation():
    offsets = search_candidate_offsets((80, 80), (40, 40), search_radius=5)

    class StopAfterTwo:
        def __init__(self):
            self.calls = 0

        def is_set(self):
            self.calls += 1
            return self.calls > 2

    selection = select_topk_candidates(
        np.zeros((1, 40, 40), dtype=np.float32),
        np.zeros((1, 40, 40), dtype=np.float32),
        offsets,
        max_neighbors=2,
        stop_event=StopAfterTwo(),
    )
    assert 0 < selection.search_candidate_count < len(offsets)

def test_raw_cfa_normalization_matches_carrier_samples_for_every_phase():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline.provider import (
        _normalize_phase_planes_into,
    )

    samples = (np.arange(64, dtype=np.uint16).reshape(8, 8) + 5).astype(np.uint16)
    black, white = 5, 69
    expected = np.clip(
        (samples.astype(np.float32) - np.float32(black))
        / np.float32(white - black),
        0.0,
        1.0,
    )
    demosaic_proxy = np.full((8, 8, 3), 0.99, dtype=np.float32)

    for phase_origin in ((0, 0), (0, 1), (1, 0), (1, 1)):
        frame = SimpleNamespace(
            samples=samples,
            black_level=(black,),
            white_level=(white,),
            phase_origin=phase_origin,
        )
        planes = tuple(np.empty((4, 4), dtype=np.float32) for _ in range(4))
        normalized_planes = _normalize_phase_planes_into(frame, planes)
        reconstructed = np.empty((8, 8), dtype=np.float32)
        phase_y, phase_x = phase_origin
        for index, plane in enumerate(normalized_planes):
            plane_y, plane_x = divmod(index, 2)
            row = (plane_y - phase_y) & 1
            col = (plane_x - phase_x) & 1
            np.testing.assert_allclose(plane, expected[row::2, col::2])
            reconstructed[row::2, col::2] = plane

        np.testing.assert_allclose(reconstructed, expected)
        assert not np.allclose(reconstructed, demosaic_proxy[..., 0])


def test_standard_default_and_explicit_mode_keep_resident_route(monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import fusionnet_parameter_settings
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
        FusionNetDenoisingAlgorithm,
    )

    monkeypatch.setattr(
        fusionnet_parameter_settings,
        "load_fusionnet_config_for_batch",
        lambda _batch_id: {},
    )
    algorithm = FusionNetDenoisingAlgorithm()
    routed_modes = []

    def resident_route(_ctx, _inputs, config, _batch_plan):
        routed_modes.append(config["denoising_mode"])
        return "standard-result"

    monkeypatch.setattr(algorithm, "_run_resident_paths", resident_route)
    for params in ({}, {"fusionnet_denoising_mode": "standard"}):
        context = SimpleNamespace(
            image_paths=["burst-reference.png"],
            frames=None,
            aligned_frames=None,
            params=params,
            batch_id=None,
            alignment_selection_name="No Alignment",
            source_descriptor=SimpleNamespace(kind="rgb"),
            is_raw_pipeline=False,
        )
        assert algorithm.run(context, frames=None) == "standard-result"

    assert routed_modes == ["standard", "standard"]


def test_standard_and_deep_analysis_default_to_taichi_aot_weightnet(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
        _resolve_weightnet_runtime,
    )

    monkeypatch.delenv("PIXEL_REFINE_WEIGHTNET_RUNTIME", raising=False)
    assert _resolve_weightnet_runtime() == "taichi_aot"

    monkeypatch.setenv("PIXEL_REFINE_WEIGHTNET_RUNTIME", "dml")
    assert _resolve_weightnet_runtime() == "dml"


def test_deep_analysis_headless_rgb_and_raw_cfa_smoke(tmp_path):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline.result import (
        RawPipelineResult,
    )
    from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

    height, width = 64, 64
    yy, xx = np.mgrid[:height, :width]
    rgb_reference = np.stack((xx, yy, (xx + yy) % width), axis=-1).astype(np.uint8) * 4
    rgb_paths = []
    rgb_images = [rgb_reference]
    rgb_images.extend(
        np.clip(rgb_reference.astype(np.int16) + 2 * index, 0, 255).astype(np.uint8)
        for index in range(1, 4)
    )
    for index, image in enumerate(rgb_images):
        path = tmp_path / f"rgb-{index}.png"
        assert cv2.imwrite(str(path), image[..., ::-1])
        rgb_paths.append(str(path))

    color_matrix = tuple(
        (int(value), 1000)
        for value in (672, -174, -102, -362, 1188, 194, -16, 143, 598)
    )
    raw_paths = []
    rng = np.random.default_rng(20261017)
    raw_samples = []
    for _index in range(4):
        shot = rng.poisson(160.0, size=(height, width)).astype(np.float32)
        read = rng.normal(0.0, 4.0, size=(height, width)).astype(np.float32)
        raw_samples.append(
            np.clip(np.rint(shot + read), 0, 1023).astype(np.uint16)
        )
    for index, samples in enumerate(raw_samples):
        frame = RawMosaicFrame.from_samples(
            samples,
            bits_per_sample=10,
            cfa_pattern=(0, 1, 1, 2),
            metadata={"dng_tags": {50721: color_matrix}},
        )
        result = RawPipelineResult(
            normalized_mosaic=samples.astype(np.float32) / np.float32(1023.0),
            preview_rgb=np.zeros((height, width, 3), dtype=np.float32),
            reference_frame=frame,
            source_paths=(),
        )
        path = tmp_path / f"raw-{index}.dng"
        result.save_dng(path)
        raw_paths.append(str(path))
    ground_truth_path = tmp_path / "raw-known-flat-field.npz"
    np.savez_compressed(ground_truth_path, frames=np.stack(raw_samples))

    script = r"""
import importlib
import sys
import threading
from types import SimpleNamespace

import numpy as np

from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

fusionnet_module = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet"
)
FusionNetDenoisingAlgorithm = fusionnet_module.FusionNetDenoisingAlgorithm

class FakeWeightNetSession:
    runtime = "cpu"
    run_count = 0
    def get_inputs(self):
        return [SimpleNamespace(shape=[1, 1, 32, 32])]
    def get_outputs(self):
        return [SimpleNamespace(shape=[1, 1, 32, 32]), SimpleNamespace(shape=[1, 1])]
    def get_providers(self):
        return []
    def run(self, _outputs, _inputs):
        self.run_count += 1
        return [
            np.full((1, 1, 32, 32), 0.8, dtype=np.float32),
            np.asarray([[0.7]], dtype=np.float32),
        ]

session = FakeWeightNetSession()
fusionnet_module.load_weightnet_onnx = lambda *_args, **_kwargs: session
inference_module = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference"
)
base_inference = inference_module.infer_single_support_weight_map
weightnet_map_calls = [0]

def count_weightnet_map(*args, **kwargs):
    weightnet_map_calls[0] += 1
    return base_inference(*args, **kwargs)

inference_module.infer_single_support_weight_map = count_weightnet_map

def context(paths, source_kind, denoising_mode="deep_analysis"):
    return SimpleNamespace(
        image_paths=paths,
        frames=None,
        aligned_frames=None,
        params={
                "fusionnet_denoising_mode": denoising_mode,
                "fusionnet_max_neighbor_candidates": 4,
            "fusionnet_work_pixel_fraction": 0.25,
            "alignment_plan": "No Alignment",
        },
        batch_id=None,
        alignment_selection_name="No Alignment",
        source_descriptor=SimpleNamespace(kind=source_kind),
        is_raw_pipeline=(source_kind == "raw"),
        stop_requested=None,
        update_progress=None,
    )

rgb_paths = sys.argv[1:5]
raw_paths = sys.argv[5:9]
ground_truth_path = sys.argv[9]
raw_ground_truth = np.load(ground_truth_path)["frames"]
algorithm = FusionNetDenoisingAlgorithm()
rgb_output = algorithm.run(context(rgb_paths, "rgb"), frames=None)
assert rgb_output.shape == (64, 64, 3) and rgb_output.dtype == np.uint16
assert np.isfinite(rgb_output).all()
expected_neighbor_count = 4
expected_map_calls = expected_neighbor_count + 3 * (1 + expected_neighbor_count)
assert weightnet_map_calls[0] == expected_map_calls, weightnet_map_calls[0]

raw_provider_module = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline.provider"
)
raw_provider_class = raw_provider_module.RawPipelineProvider
original_raw_accumulate = raw_provider_class.accumulate
raw_carrier_samples = []
raw_transform_shapes = []

def capture_raw_accumulate(provider, frame, transform=None, weight_map=None):
    assert isinstance(frame.carrier, RawMosaicFrame), type(frame.carrier)
    raw_carrier_samples.append(np.array(frame.carrier.samples, copy=True))
    if transform is not None:
        raw_transform_shapes.append(getattr(transform, "shape", type(transform).__name__))
    return original_raw_accumulate(provider, frame, transform=transform, weight_map=weight_map)

raw_provider_class.accumulate = capture_raw_accumulate
session.run_count = 0
weightnet_map_calls[0] = 0
raw_context = context(raw_paths, "raw")
try:
    raw_preview = algorithm.run(raw_context, frames=None)
finally:
    raw_provider_class.accumulate = original_raw_accumulate
raw_result = raw_context.raw_pipeline_result
assert raw_preview.shape == (64, 64, 3) and np.isfinite(raw_preview).all()
assert raw_result.normalized_mosaic.shape == (64, 64)
assert raw_result.normalized_mosaic.dtype == np.float32
assert np.isfinite(raw_result.normalized_mosaic).all()
assert tuple(raw_result.reference_frame.cfa_pattern) == (0, 1, 1, 2)
assert tuple(raw_result.reference_frame.phase_origin) == (0, 0)
expected_samples = [
    samples.astype(np.float32) / np.float32(1023.0)
    for samples in raw_ground_truth
]
assert len(raw_carrier_samples) == expected_map_calls, len(raw_carrier_samples)
assert weightnet_map_calls[0] == expected_map_calls, weightnet_map_calls[0]
for carrier_samples in raw_carrier_samples:
    normalized = carrier_samples.astype(np.float32) / np.float32(65535.0)
    assert min(float(np.max(np.abs(normalized - expected))) for expected in expected_samples) <= 1.0 / 65535.0
assert len(raw_transform_shapes) == expected_neighbor_count * (1 + 3), raw_transform_shapes

standard_context = context(raw_paths, "raw", denoising_mode="standard")
standard_preview = algorithm.run(standard_context, frames=None)
standard_result = standard_context.raw_pipeline_result
assert standard_preview.shape == (64, 64, 3) and np.isfinite(standard_preview).all()
assert standard_result.normalized_mosaic.shape == (64, 64)
assert standard_result.normalized_mosaic.dtype == np.float32
assert np.isfinite(standard_result.normalized_mosaic).all()

# The synthetic DNG burst represents a flat 160-DN Poisson signal with 4-DN
# Gaussian read noise. Both modes must reduce error against the known clean CFA.
known_flat = np.float32(160.0 / 1023.0)
reference_mosaic = expected_samples[0]
deep_mosaic = raw_result.normalized_mosaic
standard_mosaic = standard_result.normalized_mosaic
reference_mse = float(np.mean((reference_mosaic - known_flat) ** 2))
deep_mse = float(np.mean((deep_mosaic - known_flat) ** 2))
standard_mse = float(np.mean((standard_mosaic - known_flat) ** 2))
def flat_field_lag1_autocorrelation(mosaic):
    correlations = []
    noise = np.asarray(mosaic, dtype=np.float32) - known_flat
    for phase_y in range(2):
        for phase_x in range(2):
            plane = noise[phase_y::2, phase_x::2]
            for dy, dx in ((0, 1), (1, 0)):
                first = plane[: plane.shape[0] - dy, : plane.shape[1] - dx]
                second = plane[dy:, dx:]
                correlations.append(
                    float(
                        np.mean(first * second)
                        / (np.std(first) * np.std(second) + 1.0e-12)
                    )
                )
    return correlations

print(
    "synthetic RAW MSE",
    {"reference": reference_mse, "standard": standard_mse, "deep": deep_mse},
    flush=True,
)
standard_correlation = flat_field_lag1_autocorrelation(standard_mosaic)
deep_correlation = flat_field_lag1_autocorrelation(deep_mosaic)
print(
    "synthetic RAW CFA lag-1 autocorrelation",
    {"standard": standard_correlation, "deep": deep_correlation},
    flush=True,
)
assert deep_mse < reference_mse, (deep_mse, reference_mse)
assert standard_mse < reference_mse, (standard_mse, reference_mse)
assert deep_mse < standard_mse, (deep_mse, standard_mse)
assert max(abs(value) for value in deep_correlation) <= (
    max(abs(value) for value in standard_correlation) + 0.03
), (deep_correlation, standard_correlation)
plane_means = [
    float(np.mean(deep_mosaic[y::2, x::2]))
    for y in range(2)
    for x in range(2)
]
assert max(plane_means) - min(plane_means) < 0.02, plane_means
deep_dng_path = str(
    __import__("pathlib").Path(ground_truth_path).with_name("deep-known-flat.dng")
)
raw_result.save_dng(deep_dng_path)
import rawpy
with rawpy.imread(raw_paths[0]) as input_raw:
    input_cfa_pattern = input_raw.raw_pattern.copy()
with rawpy.imread(deep_dng_path) as saved_raw:
    assert saved_raw.raw_image_visible.shape == (64, 64), saved_raw.raw_image_visible.shape
    np.testing.assert_array_equal(saved_raw.raw_pattern, input_cfa_pattern)

# Inject a candidate inference error after the resident runtime has allocated
# buffers. The runtime's cleanup boundary must return its owned set to zero.
resident_module = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.resident_pipeline"
)
base_runtime = resident_module.PipelineRuntime
observed_sessions = []
original_ensure_session = base_runtime.ensure_session

def tracking_ensure_session(runtime, engine=None):
    session = original_ensure_session(runtime, engine)
    observed_sessions.append(session)
    return session

base_runtime.ensure_session = tracking_ensure_session

# Cancel from the first WeightNet inference. Candidate iteration must stop and
# the actual resident session must release every owned buffer before return.
cancel_event = threading.Event()

class CancelAfterFirstWeightNetSession(FakeWeightNetSession):
    def run(self, _outputs, _inputs):
        result = super().run(_outputs, _inputs)
        cancel_event.set()
        return result

fusionnet_module.load_weightnet_onnx = lambda *_args, **_kwargs: CancelAfterFirstWeightNetSession()
cancel_context = context(rgb_paths, "rgb")
cancel_context.stop_requested = cancel_event
try:
    algorithm.run(cancel_context, frames=None)
except RuntimeError as error:
    assert "cancel" in str(error).lower(), str(error)
assert cancel_event.is_set(), "candidate inference did not trigger cancellation"
assert observed_sessions, "resident buffer session was not observed after cancellation"
assert observed_sessions[-1].owned_count == 0, observed_sessions[-1].owned_count

raw_cancel_event = threading.Event()

class CancelAfterFirstRawWeightNetSession(FakeWeightNetSession):
    def run(self, _outputs, _inputs):
        result = super().run(_outputs, _inputs)
        raw_cancel_event.set()
        return result

fusionnet_module.load_weightnet_onnx = lambda *_args, **_kwargs: CancelAfterFirstRawWeightNetSession()
raw_cancel_context = context(raw_paths, "raw")
raw_cancel_context.stop_requested = raw_cancel_event
try:
    algorithm.run(raw_cancel_context, frames=None)
except RuntimeError as error:
    assert "cancel" in str(error).lower(), str(error)
assert raw_cancel_event.is_set(), "RAW candidate inference did not trigger cancellation"
assert observed_sessions[-1].owned_count == 0, observed_sessions[-1].owned_count

inference_module = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference"
)
original_inference = base_inference

def fail_candidate_inference(*_args, **_kwargs):
    raise RuntimeError("injected multi-patch candidate failure")

inference_module.infer_single_support_weight_map = fail_candidate_inference
fusionnet_module.load_weightnet_onnx = lambda *_args, **_kwargs: FakeWeightNetSession()
try:
    algorithm.run(context(raw_paths, "raw"), frames=None)
except RuntimeError as error:
    assert "injected multi-patch candidate failure" in str(error)
else:
    raise AssertionError("injected RAW candidate inference failure was swallowed")
finally:
    inference_module.infer_single_support_weight_map = original_inference
    base_runtime.ensure_session = original_ensure_session
assert observed_sessions, "resident buffer session was not observed"
assert observed_sessions[-1].owned_count == 0, observed_sessions[-1].owned_count
"""
    environment = os.environ.copy()
    environment["PIXEL_REFINE_AOT_ARCH"] = "cpu"
    # The subprocess is a short-lived headless smoke run.  Disable the AOT
    # idle watchdog so its daemon thread cannot race interpreter shutdown and
    # call os._exit(1) after the assertions have completed.
    environment["AUTO_DESTROY"] = "0"
    environment["QT_QPA_PLATFORM"] = "offscreen"
    completed = subprocess.run(
            [sys.executable, "-c", script, *rgb_paths, *raw_paths, str(ground_truth_path)],
        cwd=os.getcwd(),
        env=environment,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    for line in completed.stdout.splitlines():
        if line.startswith(("synthetic RAW MSE", "synthetic RAW CFA lag-1")):
            print(line)
