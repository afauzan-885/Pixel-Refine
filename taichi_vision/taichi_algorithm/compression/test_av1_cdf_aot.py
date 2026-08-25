"""Unit tests for the narrow, dependency-free AV1 CDF table subset."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from taichi_vision.taichi_algorithm.compression.av1_cdf_aot import (
    AOM_SOURCE_REF,
    AV1CDFUnsupportedContext,
    AV1CDFValidationError,
    CDF_PROB_TOP,
    CDF_TABLES,
    COEFF_BASE_CDF,
    COEFF_BR_CDF,
    DC_SIGN_CDF,
    EOB_EXTRA_CDF,
    EOB_FLAG_CDF,
    TXB_SKIP_CDF,
    av1_cdf_capability_report,
    get_av1_cdf,
    validate_cdf_table,
    validate_icdf,
)


class AV1CDFAOTTests(unittest.TestCase):
    def test_official_aom_1389210_values(self) -> None:
        # AOM's OD_ICDF(x) is CDF_PROB_TOP - x.  These are the exact
        # TX_4X4/Y/context-zero rows selected from the official source.
        self.assertEqual(TXB_SKIP_CDF, ((CDF_PROB_TOP - 128 * 252, 0, 0),))
        self.assertEqual(DC_SIGN_CDF, ((CDF_PROB_TOP - 128 * 125, 0, 0),))
        self.assertEqual(EOB_FLAG_CDF, ((CDF_PROB_TOP - 128 * 220, 0, 0),))
        self.assertEqual(EOB_EXTRA_CDF, ((CDF_PROB_TOP - 128 * 145, 0, 0),))
        self.assertEqual(COEFF_BR_CDF, ((CDF_PROB_TOP - 128 * 62, 0, 0),))
        self.assertEqual(COEFF_BASE_CDF, ((25216, 11525, 6213, 0, 0),))

    def test_tables_are_immutable_tuples(self) -> None:
        self.assertIsInstance(CDF_TABLES, MappingProxyType)
        for table in CDF_TABLES.values():
            self.assertIsInstance(table, tuple)
            for row in table:
                self.assertIsInstance(row, tuple)
        with self.assertRaises(TypeError):
            CDF_TABLES["txb_skip"] = ()  # type: ignore[index]
        with self.assertRaises(TypeError):
            TXB_SKIP_CDF[0][0] = 0  # type: ignore[index]

    def test_shape_and_monotonic_icdf_validation(self) -> None:
        expected_shapes = {
            "txb_skip": (1, 3),
            "dc_sign": (1, 3),
            "eob_flag": (1, 3),
            "eob_extra": (1, 3),
            "coeff_base": (1, 5),
            "coeff_br": (1, 3),
        }
        for name, table in CDF_TABLES.items():
            self.assertEqual(
                validate_cdf_table(table, expected_shapes[name], name=name), table
            )

        with self.assertRaises(AV1CDFValidationError):
            validate_icdf((100, 101, 0), expected_symbols=2)
        with self.assertRaises(AV1CDFValidationError):
            validate_icdf((100, 0), expected_symbols=2)
        with self.assertRaises(AV1CDFValidationError):
            validate_cdf_table(((100, 0, 0),), (2, 3), name="wrong_shape")

    def test_capability_report_is_explicit_and_fail_closed(self) -> None:
        report = av1_cdf_capability_report()
        self.assertEqual(report["aom_source_ref"], AOM_SOURCE_REF)
        self.assertEqual(report["tx_size"], "TX_4X4")
        self.assertEqual(report["bit_depth"], 8)
        self.assertEqual(report["plane_type"], "Y")
        self.assertTrue(report["fail_closed"])
        self.assertFalse(report["full_encoder"])
        self.assertEqual(report["runtime_dependencies"], ())

        self.assertIs(get_av1_cdf("coeff_base"), COEFF_BASE_CDF[0])
        with self.assertRaises(AV1CDFUnsupportedContext):
            get_av1_cdf("coeff_base", context=1)
        with self.assertRaises(AV1CDFUnsupportedContext):
            get_av1_cdf("coeff_base", tx_size="TX_8X8")
        with self.assertRaises(AV1CDFUnsupportedContext):
            get_av1_cdf("coeff_base", bit_depth=10)
        with self.assertRaises(AV1CDFUnsupportedContext):
            get_av1_cdf("coeff_base", plane_type="UV")
        with self.assertRaises(AV1CDFUnsupportedContext):
            get_av1_cdf("not_a_real_table")


if __name__ == "__main__":
    unittest.main()
