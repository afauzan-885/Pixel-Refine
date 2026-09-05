"""Opt-in integration test for the complete optical-SR production route.

The test is intentionally gated because it initializes the selected graphics
backend and runs the CPU WeightNet ONNX model.  Enable it with
``PIXEL_REFINE_RUN_AOT_INTEGRATION=1`` when qualifying a local installation.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.tests.test_optical_sr_refinement import (
    _independent_camera_burst,
    _synthetic_scene,
)


@unittest.skipUnless(
    os.environ.get("PIXEL_REFINE_RUN_AOT_INTEGRATION") == "1",
    "set PIXEL_REFINE_RUN_AOT_INTEGRATION=1 to run backend integration tests",
)
class ProductionOpticalSRIntegrationTest(unittest.TestCase):
    def test_active_lk_splat_weightnet_rejects_ghost(self):
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
            SplatSRAlgorithm,
        )

        model_path = Path(
            "database/Learning_Model/weightNet/CPU/weightnet_256_cpu_fp32.onnx"
        )
        decoupled = model_path.parent / "decoupled"
        if not model_path.is_file() and not (
            (decoupled / "encoder_256_cpu.onnx").is_file()
            and (decoupled / "attention_256_cpu.onnx").is_file()
        ):
            self.skipTest("CPU WeightNet ONNX model pair is unavailable")

        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.weightnet_confidence import (
            WeightNetConfidenceProvider,
        )

        rng = np.random.default_rng(91)
        scene = _synthetic_scene("natural_texture", height=256, width=256)
        frames, _ = _independent_camera_burst(scene)
        frames = np.clip(
            frames + rng.normal(0.0, 0.003, frames.shape).astype(np.float32),
            0.0,
            1.0,
        )
        # A moving/invalid patch exists only in one support frame.
        frames[2, 36:62, 50:82] = 1.0
        images = [
            np.repeat(
                np.clip(frame * 255.0, 0.0, 255.0).astype(np.uint8)[..., None],
                3,
                axis=2,
            )
            for frame in frames
        ]

        provider = WeightNetConfidenceProvider(
            model_path=model_path,
            runtime="cpu",
            tile_size=256,
            work_scale=0.5,
        )
        algorithm = SplatSRAlgorithm(":memory:")
        route = dict(
            scale=2,
            alignment_method="lucas_kanade",
            exposure_normalization=True,
            refinement_iterations=2,
            refinement_step=0.1,
            refinement_regularization=0.1,
        )
        plain = algorithm.run_splatting_sr(images, **route)
        weighted = algorithm.run_splatting_sr(
            images, weightnet_provider=provider, **route
        )
        plain_mse = float(
            np.mean((plain[..., 0].astype(np.float32) / 255.0 - scene) ** 2)
        )
        weighted_mse = float(
            np.mean((weighted[..., 0].astype(np.float32) / 255.0 - scene) ** 2)
        )

        self.assertEqual(weighted.shape, (256, 256, 3))
        self.assertTrue(np.isfinite(weighted).all())
        self.assertLess(weighted_mse, plain_mse)
        print(
            "[OPTICAL-SR] active_weightnet_ghost "
            f"plain_mse={plain_mse:.9g} weightnet_mse={weighted_mse:.9g} "
            f"providers={provider.providers}"
        )

    def test_dml_weightnet_matches_cpu_confidence(self):
        import onnxruntime as ort

        if "DmlExecutionProvider" not in ort.get_available_providers():
            self.skipTest("DmlExecutionProvider is unavailable")

        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.weightnet_confidence import (
            WeightNetConfidenceProvider,
        )

        cpu_model = Path(
            "database/Learning_Model/weightNet/CPU/weightnet_256_cpu_fp32.onnx"
        )
        gpu_model = Path(
            "database/Learning_Model/weightNet/GPU/weightnet_256_gpu_fp32.onnx"
        )
        rng = np.random.default_rng(2026)
        reference = rng.uniform(0.08, 0.92, (256, 256, 3)).astype(np.float32)
        support = reference.copy()
        support[72:128, 96:160] = 1.0
        cpu = WeightNetConfidenceProvider(
            model_path=cpu_model,
            runtime="cpu",
            tile_size=256,
            work_scale=1.0,
        )
        dml = WeightNetConfidenceProvider(
            model_path=gpu_model,
            runtime="dml",
            tile_size=256,
            work_scale=1.0,
        )
        cpu_map = cpu(reference, support)
        dml_map = dml(reference, support)
        max_abs = float(np.max(np.abs(cpu_map - dml_map)))
        self.assertIn("DmlExecutionProvider", dml.providers)
        self.assertTrue(np.isfinite(dml_map).all())
        self.assertLess(max_abs, 1.0e-4)
        self.assertEqual(
            float(np.mean(dml_map[72:128, 96:160])),
            0.0,
        )
        print(
            "[OPTICAL-SR] weightnet_cpu_dml_parity "
            f"max_abs={max_abs:.9g} cpu={cpu.providers} dml={dml.providers}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
