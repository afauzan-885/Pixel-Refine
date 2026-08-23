"""Regression tests for the native AV1 Q15 range/CDF primitive."""
from __future__ import annotations

import random
import unittest

from .av1_entropy_aot import (
    AV1EntropyMalformedError,
    AV1RangeDecoder,
    AV1RangeEncoder,
    CDF_PROB_TOP,
    decode_symbols,
    encode_symbols,
    update_icdf,
    validate_icdf,
)


class AV1EntropyAOTTests(unittest.TestCase):
    def test_random_symbols_round_trip_for_multiple_alphabets(self) -> None:
        randomizer = random.Random(0xA71CE)
        for icdf in (
            (16384, 0),
            (24576, 8192, 0),
            (28672, 24576, 16384, 8192, 0),
            (32000, 30000, 27000, 22000, 16000, 9000, 0),
        ):
            for count in (0, 1, 2, 7, 32, 257):
                symbols = [randomizer.randrange(len(icdf)) for _ in range(count)]
                payload = encode_symbols(symbols, icdf)
                self.assertEqual(tuple(symbols), decode_symbols(payload, count, icdf))

    def test_literals_round_trip_across_flush_boundaries(self) -> None:
        randomizer = random.Random(0x51A1)
        values = [randomizer.randrange(1 << 32) for _ in range(257)]
        encoder = AV1RangeEncoder()
        for value in values:
            encoder.encode_literal(value, 32)
        payload = encoder.finish()
        decoder = AV1RangeDecoder(payload)
        self.assertEqual(values, [decoder.decode_literal(32) for _ in values])
        self.assertGreater(len(payload), 256)

    def test_boolean_path_matches_binary_cdf_path(self) -> None:
        values = (0, 1, 1, 0, 0, 1, 0, 1)
        bool_encoder = AV1RangeEncoder()
        for value in values:
            bool_encoder.encode_bool(value, CDF_PROB_TOP // 2)
        cdf_payload = encode_symbols(values, (CDF_PROB_TOP // 2, 0))
        self.assertEqual(bool_encoder.finish(), cdf_payload)
        decoder = AV1RangeDecoder(cdf_payload)
        self.assertEqual(values, tuple(decoder.decode_bool(CDF_PROB_TOP // 2) for _ in values))

    def test_cdf_adaptation_is_explicit_and_bounded(self) -> None:
        table = (24576, 8192, 0)
        updated, count = update_icdf(table, 1, count=31)
        self.assertEqual(count, 32)
        self.assertEqual(updated, (24832, 7936, 0))
        self.assertEqual(len(updated), len(table))
        self.assertEqual(updated[-1], 0)
        validate_icdf(updated)

    def test_rejects_malformed_tables_and_empty_streams(self) -> None:
        with self.assertRaises(AV1EntropyMalformedError):
            validate_icdf((0, 1))
        with self.assertRaises(AV1EntropyMalformedError):
            validate_icdf((100, 50, 1))
        with self.assertRaises(AV1EntropyMalformedError):
            AV1RangeDecoder(b"")


if __name__ == "__main__":
    unittest.main()
