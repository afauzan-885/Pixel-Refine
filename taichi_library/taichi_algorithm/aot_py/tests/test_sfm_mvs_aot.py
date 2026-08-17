"""Target-qualified SGM/PatchMatch leaf contracts."""

from __future__ import annotations

import unittest

import numpy as np


class SfMMVSAOTTests(unittest.TestCase):
    def test_cpu_stereo_regularizer_leaves(self) -> None:
        from ...aot_api.research import (
            sfm_patchmatch_iteration_aot,
            sfm_sgm_path_aot,
        )

        cost = np.random.default_rng(19).random((4, 6, 7), dtype=np.float32)
        try:
            path = sfm_sgm_path_aot(cost, dy=1, dx=0)
            labels = sfm_patchmatch_iteration_aot(
                cost,
                np.argmin(cost, axis=0).astype(np.int32),
                iteration=0,
                random_seed=7,
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(path.shape, cost.shape)
        self.assertTrue(np.isfinite(path).all())
        self.assertEqual(labels.shape, cost.shape[1:])
        self.assertTrue(np.all((labels >= 0) & (labels < cost.shape[0])))


if __name__ == "__main__":
    unittest.main()
