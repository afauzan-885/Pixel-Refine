"""RAW warp resolution and GPU blend dispatch helpers.

Per-support-frame helpers used by the shared RAW provider loop: resolving
exactly one support->reference warp for weight analysis, and blending one
support frame into the GPU-resident accumulator.
"""

__all__ = ["_prepare_raw_aligned_analysis", "_gpu_blend_frame"]

def _prepare_raw_aligned_analysis(
    support_analysis,
    alignment_preview,
    transform,
    *,
    align_shape,
    warp_analysis,
):
    """Resolve exactly one support->reference warp for RAW weight analysis.

    Resident aligners return both an already-warped primary image and the
    transform used to create it.  RAW Native needs the transform again for the
    CFA carrier, but must not apply it a second time to that aligned RGB proxy.

    The aligner preview can be reused only when it is a distinct buffer on the
    canonical analysis grid.  A smaller RAW proxy may otherwise have been
    expanded to the full carrier grid by an aligner whose primary-image
    contract targets ``full_shape``.  In that case, discard the preview and
    warp the original proxy once on its own grid.

    Returns ``(analysis_for_weight, preview_to_destroy)``.  Ownership of a
    reusable preview transfers to ``analysis_for_weight``.
    """

    target_shape = (int(align_shape[0]), int(align_shape[1]))
    if transform is None:
        return support_analysis, alignment_preview

    preview_shape = getattr(alignment_preview, "shape", ())
    preview_matches = (
        alignment_preview is not None
        and alignment_preview is not support_analysis
        and len(preview_shape) >= 2
        and tuple(int(value) for value in preview_shape[:2]) == target_shape
    )
    if preview_matches:
        return alignment_preview, None

    aligned = warp_analysis(support_analysis, transform, target_shape)
    return aligned, alignment_preview


def _gpu_blend_frame(sum_img_gpu, weight_sum_gpu, supp_aligned_gpu, weight_work_gpu):
    """Blend one support frame into the GPU-resident accumulator.

    Uses the shared Taichi accumulator. Scalar WeightNet maps stay 2D and
    dispatch to scalar-to-RGB accumulation; SpatialFusion and legacy RGB maps
    retain their existing scalar/vec3 dispatch.
    """
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
        accumulate_spatial_merging_taichi,
    )

    accumulate_spatial_merging_taichi(
        current_image_full=supp_aligned_gpu.view_as_vector(False),
        weight_map_work=(
            weight_work_gpu.view_as_vector(False)
            if len(weight_work_gpu.shape) > 2
            else weight_work_gpu
        ),
        final_image_sum=sum_img_gpu.view_as_vector(False),
        weight_map_sum_full=weight_sum_gpu.view_as_vector(False),
    )
