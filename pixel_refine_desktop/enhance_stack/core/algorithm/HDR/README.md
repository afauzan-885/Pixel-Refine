# HDR Fusion

This package adds two selectable batch algorithms:

- **Weighted HDR**: per-pixel exposure, detail, saturation, and Taichi noise
  weighted fusion.
- **SPDE-MR HDR Fusion**: the same AOT weights plus Taichi AOT-scored 8×8
  patches at stride 4, local `E×C×S` quality, a structure correlation
  threshold of 0.8, and single-frame priority for regions rejected as moving.

`running_hdr_fusion()` reads the marked reference image from the batch database.
It scans histogram summaries one image at a time; if the selected reference is
clearly worse exposed than another frame, it uses the highest-scoring frame as
the reference. The image data itself is then decoded again and streamed with
`PipelineRuntime(prefetch_depth=0)`. Each support is aligned against the
reference with Taichi Vision AOT MTB before it contributes to the accumulators.
The support count has no configured cap; live image buffers and fusion state
remain bounded by image size, while the database path and histogram summaries
scale with the number of frames.

Weighted HDR's streaming policy lives in `weighted_average/core.py`; its Taichi
weight and accumulation graphs are packaged by
`weighted_average/compile_weighted_average.py`. The runtime resolves the exact
active target artifact from `pixel_refine_desktop/ui/data/aot_assets/` and
raises an error if it is missing. The high-level `hdr_fuse_aot()` materializes
the entire stack, so the desktop runner applies the same lower-level weight and
accumulation leaves one frame at a time. Intermediate accumulators still cross
the host boundary between frames; this is not a fully resident GPU pipeline.

The user-selected LDR output is a 16-bit TIFF in `[0, 1]`. A second float32
linear TIFF is written only when all frames have positive EXIF shutter time,
ISO, and aperture metadata, camera values are compatible, and the exposure
ordering passes a histogram-consistency check. This is a **relative radiance
estimate** based on an sRGB transfer-curve assumption and EXIF effective
exposure; ordinary JPEG tone curves and camera processing prevent it from
claiming calibrated physical radiance. When metadata is missing or inconsistent,
the pipeline emits only LDR exposure fusion and reports why.

SPDE-MR's fusion policy lives in `SPDE/core.py`; `spde_mr.py` is its small
pipeline-facing orchestrator. It uses the report's 8×8/stride-4 and 0.8
defaults, and its local priority is `E×C×S` (exposure suitability × patch
contrast × structure correlation).
For accepted static patches it modulates the AOT pixel weights; patches below
the correlation threshold are excluded from weighted accumulation and the
highest local-priority single-frame sample is used where motion was detected.
The policy calls the two Taichi graphs exposed by `SPDE/runtime.py`. Their
canonical Taichi kernels remain in
`taichi_vision/taichi_algorithm/spatial_fusion/spde_mr_hdr.py`; the family
compiler in `SPDE/compile_spde_mr.py` packages them into
`pixel_refine_desktop/ui/data/aot_assets/` for the active target. Both compiler
scripts compile one backend at a time, for example:

```powershell
.\venv\Scripts\python.exe pixel_refine_desktop\enhance_stack\core\algorithm\HDR\weighted_average\compile_weighted_average.py --backend cpu
.\venv\Scripts\python.exe pixel_refine_desktop\enhance_stack\core\algorithm\HDR\SPDE\compile_spde_mr.py --backend cpu
```

The generated filenames include backend, OS, and architecture. Add `--overwrite`
only when intentionally rebuilding the same target artifact.

The report leaves its sensor-noise coefficients and final detail term
`F = B + alpha×D` unspecified. The implementation therefore uses Taichi's
estimated raw noise sigma for the existing AOT weight and does not claim a
calibrated sensor model or the report's unspecified detail reconstruction.

RAW inputs use Taichi AOT demosaicing only. A demosaic failure is explicit; the
desktop HDR path does not invoke RawPy or another CPU fallback. MTB handles
integer translation; rotation, scale, parallax, and rolling-shutter motion are
outside this initial alignment contract.

For RAW RGB input, the desktop loader requests Hamilton output with+`return_gpu=True`, matching MF-Denoising's resident RAW loader, reads back the+single frame needed by the streaming HDR stage, and releases its GPU buffer.+This keeps full-resolution RAW on the normal resident demosaic graph and avoids+the distinct non-resident block adapter. The RGB HDR AOT kernels use flat scalar+buffers because the engine marks H×W×3 uploads as vector fields; their registered+graph ABI is therefore 1D RGB plus the 2D weight map.
