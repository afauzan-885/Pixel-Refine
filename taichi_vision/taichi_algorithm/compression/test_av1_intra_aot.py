"""Standalone regression tests for the bounded AV1 intra profile."""
from __future__ import annotations

import unittest

from .av1_intra_aot import (
    AV1IntraError,
    AV1IntraUnsupportedError,
    av1_intra_capability_report,
    encode_av1_intra_constant,
    expected_i420_frame,
    supported_constant_colors,
    validate_av1_intra_payload,
)


class AV1IntraAOTTests(unittest.TestCase):
    def test_every_palette_entry_is_exact_and_structurally_valid(self) -> None:
        colors = supported_constant_colors()
        self.assertEqual(len(colors), 27)
        for color in colors:
            payload = encode_av1_intra_constant(*color)
            result = validate_av1_intra_payload(payload, *color)
            self.assertTrue(result.valid)
            self.assertEqual(result.obu_types, (2, 1, 6))
            self.assertEqual(result.frame_tile_count, 1)
            self.assertEqual(
                expected_i420_frame(*color),
                bytes((color[0],)) * 256
                + bytes((color[1],)) * 64
                + bytes((color[2],)) * 64,
            )

    def test_rejects_unsupported_input(self) -> None:
        for kwargs in (
            {"width": 15},
            {"height": 32},
            {"bit_depth": 10},
            {"chroma": "444"},
        ):
            with self.assertRaises(AV1IntraUnsupportedError):
                encode_av1_intra_constant(**kwargs)
        with self.assertRaises(AV1IntraUnsupportedError):
            encode_av1_intra_constant(1, 128, 128)

    def test_rejects_truncation_and_wrong_palette_key(self) -> None:
        payload = encode_av1_intra_constant(128, 128, 128)
        for end in range(len(payload)):
            with self.assertRaises(AV1IntraError):
                validate_av1_intra_payload(payload[:end], 128, 128, 128)
        with self.assertRaises(AV1IntraUnsupportedError):
            validate_av1_intra_payload(payload, 0, 128, 128)

    def test_capability_is_explicitly_not_general(self) -> None:
        report = av1_intra_capability_report()
        self.assertEqual(report["profile"], "bounded-intra-constant-16x16-i420")
        self.assertEqual(report["palette_size"], 27)
        self.assertFalse(report["general_encoder"])
        self.assertTrue(report["external_decoder_validation_required"])


if __name__ == "__main__":
    unittest.main()
