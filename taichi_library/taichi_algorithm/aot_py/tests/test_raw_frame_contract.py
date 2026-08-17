"""Contract tests for pre-demosaic RAW/DNG handling."""

from __future__ import annotations

import unittest
import importlib.util
import pathlib
import struct
import sys
import types

import numpy as np



def _load_pure_compression_modules():
    """Load container/RAW modules without initializing the AOT engine."""
    root = pathlib.Path(__file__).resolve().parents[2] / "compression"
    base = "_pixel_refine_raw_contract"
    package = types.ModuleType(base)
    package.__path__ = [str(root.resolve())]
    sys.modules[base] = package
    subpackage = types.ModuleType(f"{base}.compression")
    subpackage.__path__ = [str(root.resolve())]
    sys.modules[f"{base}.compression"] = subpackage
    loaded = {}
    for name in ("bitstream", "png_aot", "raw_frame", "dng_aot", "raw_pipeline"):
        qualified = f"{base}.compression.{name}"
        spec = importlib.util.spec_from_file_location(qualified, root / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified] = module
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded["dng_aot"], loaded["raw_frame"], loaded["raw_pipeline"]


_DNG, _RAW, _PIPELINE = _load_pure_compression_modules()
encode_dng_aot = _DNG.encode_dng_aot
read_dng_aot = _DNG.read_dng_aot
DNGCapabilityError = _DNG.DNGCapabilityError
dng_capability_report = _DNG.dng_capability_report
RawMosaicFrame = _RAW.RawMosaicFrame
fuse_raw_frames_blockwise = _PIPELINE.fuse_raw_frames_blockwise
fuse_dng_frames_blockwise = _PIPELINE.fuse_dng_frames_blockwise
raw_alignment_guide_dng = _PIPELINE.raw_alignment_guide_dng
raw_optical_flow_dng = _PIPELINE.raw_optical_flow_dng
raw_flow_tile_parity_report = _PIPELINE.raw_flow_tile_parity_report
_prepare_flow_inputs = _PIPELINE._prepare_flow_inputs
phase_safe_integer_warp = _PIPELINE.phase_safe_integer_warp
RawFlowTileContract = _PIPELINE.RawFlowTileContract


class RawFrameContractTests(unittest.TestCase):
    def test_headroom_is_preserved_and_cfa_planes_are_phase_aware(self):
        samples = np.array(
            [
                [90, 110, 130, 150],
                [210, 230, 250, 270],
                [290, 310, 330, 350],
                [410, 430, 450, 470],
            ],
            dtype=np.uint16,
        )
        frame = RawMosaicFrame.from_samples(
            samples,
            bits_per_sample=12,
            cfa_pattern=(1, 0, 0, 1),
            black_level=(100, 100, 100, 100),
            white_level=(300, 300, 300, 300),
            source_id="synthetic",
            source_version="v1",
        )
        normalized = frame.normalized_headroom()
        self.assertEqual(normalized.dtype, np.float32)
        self.assertEqual(float(normalized[0, 0]), 0.0)
        self.assertGreater(float(normalized[3, 3]), 1.0)
        self.assertEqual(frame.plane(0).shape, (2, 2))
        self.assertEqual(frame.plane(3).shape, (2, 2))
        self.assertEqual(frame.cache_key(), RawMosaicFrame.from_samples(
            samples.copy(),
            bits_per_sample=12,
            cfa_pattern=(1, 0, 0, 1),
            black_level=(100, 100, 100, 100),
            white_level=(300, 300, 300, 300),
            source_id="synthetic",
            source_version="v1",
        ).cache_key())

    def test_dng_round_trip_keeps_native_codes_before_demosaic(self):
        source = (np.arange(35, dtype=np.uint16).reshape(5, 7) * 37) & 0x3FFF
        encoded = encode_dng_aot(
            source,
            metadata={
                "cfa_pattern": (1, 0, 0, 1),
                "black_level": 64,
                "white_level": 16383,
                "camera_model": "Synthetic RAW",
            },
            compression="packbits",
            bits_per_sample=14,
        )
        parsed = read_dng_aot(encoded)
        frame = parsed.to_raw_frame(source_id="synthetic-dng")
        np.testing.assert_array_equal(frame.samples, source)
        self.assertEqual(frame.bits_per_sample, 14)
        self.assertEqual(frame.cfa_pattern, (1, 0, 0, 1))
        self.assertEqual(frame.source_id, "synthetic-dng")

    def test_packed_10_12_14_bit_rows_are_exact(self):
        rng = np.random.default_rng(20260810)
        for bits, width in ((10, 11), (12, 13), (14, 15)):
            source = rng.integers(
                0,
                1 << bits,
                size=(5, width),
                dtype=np.uint16,
            )
            encoded = encode_dng_aot(
                source,
                metadata={"cfa_pattern": (1, 0, 0, 1)},
                compression="none",
                bits_per_sample=bits,
            )
            parsed = read_dng_aot(encoded)
            np.testing.assert_array_equal(parsed.samples(), source)
            np.testing.assert_array_equal(parsed.sample_region(1, 5, 2, width), source[1:5, 2:])

    def test_all_supported_8_to_16_bit_depths_are_lossless(self):
        rng = np.random.default_rng(20260811)
        for bits in range(8, 17):
            # Deliberately use a non-group-aligned width for packed formats;
            # 8/16-bit paths exercise the native byte transport directly.
            width = 17 + (bits % 3)
            dtype = np.uint8 if bits == 8 else np.uint16
            source = rng.integers(0, 1 << bits, size=(3, width), dtype=dtype)
            encoded = encode_dng_aot(
                source,
                metadata={"cfa_pattern": (1, 0, 0, 1)},
                compression="none",
                bits_per_sample=bits,
            )
            parsed = read_dng_aot(encoded)
            np.testing.assert_array_equal(parsed.samples(), source)
            np.testing.assert_array_equal(parsed.sample_region(0, 2, 3, width), source[0:2, 3:])

    def test_capability_report_accepts_supported_lossless_jpeg_and_rejects_tiles(self):
        supported = dng_capability_report(
            {256: 64, 257: 32, 258: 14, 259: 1, 273: (128,), 279: (256,)}
        )
        self.assertTrue(supported.supported)
        lossless_jpeg = dng_capability_report(
            {256: 64, 257: 32, 258: 16, 259: 7, 273: (128,), 279: (256,)}
        )
        self.assertTrue(lossless_jpeg.supported)
        self.assertEqual(lossless_jpeg.profile, "lossless_jpeg_strip_profile")
        malformed_lossless_jpeg = dng_capability_report(
            {
                256: 64,
                257: 32,
                258: 16,
                259: 7,
                273: (128,),
                279: (256,),
                517: 8,
            }
        )
        self.assertFalse(malformed_lossless_jpeg.supported)
        self.assertTrue(any("1..7" in reason for reason in malformed_lossless_jpeg.reasons))
        tiled = dng_capability_report(
            {256: 64, 257: 32, 258: 16, 259: 1, 322: 16, 323: 16, 324: (128,), 325: (256,)}
        )
        self.assertFalse(tiled.supported)
        self.assertEqual(tiled.profile, "tiled_unsupported")
        self.assertTrue(any("tiled" in reason for reason in tiled.reasons))
        subifd = dng_capability_report(
            {256: 64, 257: 32, 258: 16, 259: 1, 273: (128,), 279: (256,), 330: (512,)}
        )
        self.assertFalse(subifd.supported)
        self.assertEqual(subifd.profile, "subifd_unsupported")
        self.assertTrue(any("SubIFDs" in reason for reason in subifd.reasons))

        lossless_source = np.arange(64, dtype=np.uint16).reshape(8, 8)
        lossless_encoded = encode_dng_aot(
            lossless_source,
            compression="lossless_jpeg",
            bits_per_sample=16,
            metadata={"jpeg_predictor": 1},
        )
        lossless_parsed = read_dng_aot(lossless_encoded)
        np.testing.assert_array_equal(lossless_parsed.samples(), lossless_source)

        encoded = bytearray(
            encode_dng_aot(
                np.arange(64, dtype=np.uint16).reshape(8, 8),
                compression="none",
                bits_per_sample=16,
            )
        )
        ifd_offset = struct.unpack_from("<I", encoded, 4)[0]
        entry_count = struct.unpack_from("<H", encoded, ifd_offset)[0]
        for index in range(entry_count):
            entry = ifd_offset + 2 + index * 12
            if struct.unpack_from("<H", encoded, entry)[0] == 259:
                struct.pack_into("<H", encoded, entry + 8, 7)
                break
        else:  # pragma: no cover - encoder always emits Compression
            self.fail("synthetic DNG did not contain Compression")
        with self.assertRaises((DNGCapabilityError, ValueError)):
            read_dng_aot(bytes(encoded))

        tiled_encoded = bytearray(
            encode_dng_aot(
                np.arange(64, dtype=np.uint16).reshape(8, 8),
                compression="none",
                bits_per_sample=16,
            )
        )
        tiled_ifd_offset = struct.unpack_from("<I", tiled_encoded, 4)[0]
        tiled_entry_count = struct.unpack_from("<H", tiled_encoded, tiled_ifd_offset)[0]
        for index in range(tiled_entry_count):
            entry = tiled_ifd_offset + 2 + index * 12
            # Replace the optional PlanarConfiguration tag with TileWidth;
            # capability inspection must reject the tile marker before decode.
            if struct.unpack_from("<H", tiled_encoded, entry)[0] == 284:
                struct.pack_into("<H", tiled_encoded, entry, 322)
                break
        with self.assertRaises(DNGCapabilityError) as context:
            read_dng_aot(bytes(tiled_encoded))
        self.assertIsNotNone(context.exception.report)
        self.assertEqual(context.exception.report.profile, "tiled_unsupported")

    def test_dng_region_iterator_and_direct_fusion_preserve_cfa_phase(self):
        first = (np.arange(63, dtype=np.uint16).reshape(7, 9) * 19) & 0x3FFF
        second = np.minimum(first + 240, 0x3FFF).astype(np.uint16)
        encoded_a = encode_dng_aot(
            first,
            metadata={"cfa_pattern": (1, 0, 0, 1), "black_level": 64, "white_level": 16383},
            compression="none",
            bits_per_sample=14,
        )
        encoded_b = encode_dng_aot(
            second,
            metadata={"cfa_pattern": (1, 0, 0, 1), "black_level": 64, "white_level": 16383},
            compression="none",
            bits_per_sample=14,
        )
        dng_a = read_dng_aot(encoded_a)
        dng_b = read_dng_aot(encoded_b)
        full_frame = dng_a.to_raw_frame()
        odd_tile = RawMosaicFrame.from_dng_region(dng_a, 1, 6, 3, 8)
        np.testing.assert_allclose(
            odd_tile.normalized_headroom(),
            full_frame.normalized_headroom()[1:6, 3:8],
            rtol=0,
            atol=0,
        )
        streamed_guide = raw_alignment_guide_dng(
            dng_a, block_size=(3, 4), apply_white_balance=False
        )
        np.testing.assert_allclose(
            streamed_guide,
            full_frame.green_guide(apply_white_balance=False),
            rtol=0,
            atol=0,
        )
        flow = raw_optical_flow_dng(
            dng_a,
            dng_a,
            block_size=(3, 4),
            flow_runner=lambda previous, current, **_kwargs: previous - current,
        )
        self.assertEqual(flow.shape, streamed_guide.shape)
        np.testing.assert_allclose(flow, 0.0, rtol=0, atol=0)
        regions = list(dng_a.iter_regions((3, 4)))
        self.assertEqual(len(regions), 9)
        for y0, y1, x0, x1, tile in regions:
            np.testing.assert_array_equal(tile, first[y0:y1, x0:x1])
        fused, report = fuse_dng_frames_blockwise(
            (dng_a, dng_b), block_size=(3, 4)
        )
        expected = (
            np.maximum(first.astype(np.float32) - 64.0, 0.0)
            + np.maximum(second.astype(np.float32) - 64.0, 0.0)
        ) / (2.0 * (16383.0 - 64.0))
        np.testing.assert_allclose(fused, expected, rtol=0, atol=1e-6)
        self.assertEqual(report.block_count, 9)

    def test_dng_flow_force_mode_requires_explicit_tile_contract(self):
        source = np.arange(81, dtype=np.uint16).reshape(9, 9)
        encoded = encode_dng_aot(
            source,
            metadata={"cfa_pattern": (1, 0, 0, 1)},
            compression="none",
            bits_per_sample=12,
        )
        parsed = read_dng_aot(encoded)
        with self.assertRaises(ValueError):
            raw_optical_flow_dng(
                parsed,
                parsed,
                block_size=(4, 5),
                flow_runner=lambda previous, current, **_kwargs: np.zeros(
                    (*previous.shape, 2), dtype=np.float32
                ),
                flow_mode="force",
            )

    def test_dng_flow_explicit_tile_contract_matches_full_guide_runner(self):
        source = (np.arange(143, dtype=np.uint16).reshape(11, 13) * 17) & 0x0FFF
        changed = np.minimum(source + 13, 0x0FFF).astype(np.uint16)
        encoded_a = encode_dng_aot(
            source,
            metadata={"cfa_pattern": (1, 0, 0, 1)},
            compression="none",
            bits_per_sample=12,
        )
        encoded_b = encode_dng_aot(
            changed,
            metadata={"cfa_pattern": (1, 0, 0, 1)},
            compression="none",
            bits_per_sample=12,
        )
        first = read_dng_aot(encoded_a)
        second = read_dng_aot(encoded_b)

        def local_runner(previous, current, **_kwargs):
            # A deterministic guide-local vector field; no global reduction,
            # pyramid, or cross-tile state is hidden in this test runner.
            return np.stack((current - previous, current + previous), axis=-1)

        full = raw_optical_flow_dng(
            first,
            second,
            block_size=(4, 5),
            flow_runner=local_runner,
            flow_mode="full_frame",
        )
        tiled = raw_optical_flow_dng(
            first,
            second,
            block_size=(4, 5),
            flow_runner=local_runner,
            flow_contract=RawFlowTileContract(halo=1),
            flow_mode="force",
        )
        self.assertEqual(tiled.dtype, np.dtype(np.float32))
        np.testing.assert_array_equal(tiled, full)

    def test_dng_flow_parity_harness_records_determinism_and_known_translation(self):
        """The same runner is compared full-frame and through explicit tiles."""
        source = np.zeros((13, 17), dtype=np.uint16)
        source[3:7, 5:9] = 1000
        shifted = np.roll(np.roll(source, 1, axis=0), 2, axis=1)
        encoded_a = encode_dng_aot(
            source,
            metadata={"cfa_pattern": (1, 0, 0, 1)},
            compression="none",
            bits_per_sample=12,
        )
        encoded_b = encode_dng_aot(
            shifted,
            metadata={"cfa_pattern": (1, 0, 0, 1)},
            compression="none",
            bits_per_sample=12,
        )
        first = read_dng_aot(encoded_a)
        second = read_dng_aot(encoded_b)

        def known_translation_runner(previous, current, **_kwargs):
            # This deterministic synthetic runner represents a known moving
            # pair; the harness remains candidate-only and makes no native
            # qualification claim.
            return np.broadcast_to(
                np.asarray((2.0, 1.0), dtype=np.float32),
                (*previous.shape, 2),
            ).copy()

        report = raw_flow_tile_parity_report(
            first,
            second,
            flow_runner=known_translation_runner,
            block_size=(6, 8),
            flow_contract=RawFlowTileContract(halo=2),
            expected_translation=(2.0, 1.0),
        )
        self.assertTrue(report["passed"])
        self.assertTrue(report["block_selected"])
        self.assertTrue(report["deterministic_merge"])
        self.assertEqual(report["parity_max_abs_error"], 0.0)
        self.assertEqual(report["repeat_max_abs_error"], 0.0)
        self.assertEqual(report["median_translation"], [2.0, 1.0])
        self.assertEqual(report["evidence_status"], "candidate_only")
        self.assertFalse(report["native_runtime"])

    def test_dng_flow_tile_contract_rejects_phase_unsafe_metadata(self):
        with self.assertRaises(ValueError):
            RawFlowTileContract(halo=2, phase_preserving=False)
        with self.assertRaises(ValueError):
            RawFlowTileContract(halo=2, domain="raw_mosaic")

    def test_default_native_flow_abi_scales_normalized_guides_only(self):
        previous = np.asarray([[0.0, 0.25], [0.5, 1.0]], dtype=np.float32)
        current = previous + np.float32(0.1)
        scaled_previous, scaled_current = _prepare_flow_inputs(
            previous,
            current,
            flow_input_scale=None,
            default_runner=True,
        )
        np.testing.assert_array_equal(scaled_previous, previous * np.float32(255.0))
        np.testing.assert_array_equal(scaled_current, current * np.float32(255.0))
        custom_previous, custom_current = _prepare_flow_inputs(
            previous,
            current,
            flow_input_scale=None,
            default_runner=False,
        )
        np.testing.assert_array_equal(custom_previous, previous)
        np.testing.assert_array_equal(custom_current, current)
        explicit_previous, explicit_current = _prepare_flow_inputs(
            previous,
            current,
            flow_input_scale=1.0,
            default_runner=True,
        )
        np.testing.assert_array_equal(explicit_previous, previous)
        np.testing.assert_array_equal(explicit_current, current)

    def test_invalid_native_dtype_is_rejected(self):
        with self.assertRaises(TypeError):
            RawMosaicFrame.from_samples(np.zeros((2, 2), dtype=np.float32))

    def test_region_normalization_and_block_fusion_match_oracle(self):
        first = np.full((9, 11), 600, dtype=np.uint16)
        second = np.full((9, 11), 1000, dtype=np.uint16)
        frame_a = RawMosaicFrame.from_samples(
            first,
            bits_per_sample=12,
            black_level=100,
            white_level=1100,
            cfa_pattern=(1, 0, 0, 1),
        )
        frame_b = RawMosaicFrame.from_samples(
            second,
            bits_per_sample=12,
            black_level=100,
            white_level=1100,
            cfa_pattern=(1, 0, 0, 1),
        )
        full = frame_a.normalized_headroom()
        region = frame_a.normalized_headroom_region(1, 8, 3, 10)
        np.testing.assert_allclose(region, full[1:8, 3:10], rtol=0, atol=0)
        fused, report = fuse_raw_frames_blockwise((frame_a, frame_b), block_size=(4, 5))
        np.testing.assert_allclose(fused, 0.7, rtol=0, atol=1e-6)
        self.assertEqual(report.block_count, 9)
        self.assertEqual(report.headroom_pixels, 0)

    def test_phase_safe_warp_rejects_odd_or_subpixel_motion(self):
        samples = np.arange(64, dtype=np.uint16).reshape(8, 8)
        frame = RawMosaicFrame.from_samples(samples, bits_per_sample=12, white_level=4095)
        even_flow = np.zeros((8, 8, 2), dtype=np.float32)
        even_flow[..., 0] = 2.0
        shifted = phase_safe_integer_warp(frame, even_flow)
        np.testing.assert_array_equal(shifted[:, :-2], samples[:, 2:])
        odd_flow = even_flow.copy()
        odd_flow[0, 0, 0] = 1.0
        with self.assertRaises(ValueError):
            phase_safe_integer_warp(frame, odd_flow)
        fractional = even_flow.copy()
        fractional[0, 0, 1] = 2.25
        with self.assertRaises(ValueError):
            phase_safe_integer_warp(frame, fractional)

    def test_green_guide_respects_nonzero_cfa_phase(self):
        samples = np.arange(64, dtype=np.uint16).reshape(8, 8)
        frame = RawMosaicFrame.from_samples(
            samples,
            bits_per_sample=12,
            cfa_pattern=(1, 0, 0, 1),
            phase_origin=(1, 1),
            white_level=63,
        )
        normalized = frame.normalized_headroom()
        expected = (
            normalized[1::2, 1::2][:4, :4]
            + normalized[0::2, 0::2][:4, :4]
        ) * np.float32(0.5)
        np.testing.assert_allclose(frame.green_guide(), expected, rtol=0, atol=0)


if __name__ == "__main__":
    unittest.main()
