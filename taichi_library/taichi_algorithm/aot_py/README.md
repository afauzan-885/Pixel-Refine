# AOT build and validation tools

This directory contains only cross-family tooling:

- `compile_aot_backend_suite.py` — target-qualified batch compiler;
- `compile_research_tcm.py` — shared HDR, tone-mapping, Camera2, and SfM compiler;
- `compile_common_tcm.py` and `compile_cast_tcm.py` — shared utility graphs;
- `tests/` — comprehensive, parity, and stress validation;
- `tools/` — diagnostic/build helpers.

Family-specific compilers live beside their kernels. Examples:

- `feature_matching/compile_akaze_tcm.py`
- `optical_flow/compile_lucas_kanade_tcm.py`
- `demosaicing/compile_hamilton_tcm.py`
- `image_processing/compile_analysis_suite_tcm.py`

Use the batch compiler for production builds so it resolves family-local
modules and validates target-qualified artifacts.
