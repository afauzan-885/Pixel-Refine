"""Legacy demosaic highlight kernels kept for compatibility.

These kernels are not part of the current graph assembly, but older notebooks
and experiments imported them directly.  Keeping them in a separate module
allows the active compiler to stay small without silently deleting that
experimental surface.
"""

import taichi as ti


@ti.kernel
def recover_highlights_local(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        raw_r = r / ti.max(wb_r, 1e-4)
        raw_g = g / ti.max(wb_g, 1e-4)
        raw_b = b / ti.max(wb_b, 1e-4)
        raw_peak = ti.max(raw_r, ti.max(raw_g, raw_b))
        rg_sum = 0.0
        bg_sum = 0.0
        weight_sum = 0.0
        for dy, dx in ti.ndrange(11, 11):
            ny = ti.math.clamp(y + dy - 5, 0, h - 1)
            nx = ti.math.clamp(x + dx - 5, 0, w - 1)
            nr = src[ny, nx, 0]
            ng = src[ny, nx, 1]
            nb = src[ny, nx, 2]
            neighbour_peak = ti.max(
                nr / ti.max(wb_r, 1e-4),
                ti.max(ng / ti.max(wb_g, 1e-4), nb / ti.max(wb_b, 1e-4)),
            )
            if ng > 1e-5:
                distance = ti.cast(ti.abs(dy - 5) + ti.abs(dx - 5), ti.f32)
                valid = ti.math.clamp((1.0 - neighbour_peak) / 0.12, 0.0, 1.0)
                valid = valid * valid * (3.0 - 2.0 * valid)
                weight = valid / (1.0 + distance)
                rg_sum += ti.math.clamp(nr / ng, 0.05, 8.0) * weight
                bg_sum += ti.math.clamp(nb / ng, 0.05, 8.0) * weight
                weight_sum += weight
        rg = ti.select(weight_sum > 0.0, rg_sum / ti.max(weight_sum, 1e-5), 1.0)
        bg = ti.select(weight_sum > 0.0, bg_sum / ti.max(weight_sum, 1e-5), 1.0)
        neutral = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        neutral = neutral * neutral * (3.0 - 2.0 * neutral) * 0.70
        rg = ti.math.clamp(rg, 0.70, 1.30) * (1.0 - neutral) + neutral
        bg = ti.math.clamp(bg, 0.70, 1.30) * (1.0 - neutral) + neutral
        rel_r = ti.math.clamp((1.0 - raw_r) / 0.12, 0.0, 1.0)
        rel_g = ti.math.clamp((1.0 - raw_g) / 0.12, 0.0, 1.0)
        rel_b = ti.math.clamp((1.0 - raw_b) / 0.12, 0.0, 1.0)
        rel_r = rel_r * rel_r * (3.0 - 2.0 * rel_r)
        rel_g = rel_g * rel_g * (3.0 - 2.0 * rel_g)
        rel_b = rel_b * rel_b * (3.0 - 2.0 * rel_b)
        reliable_sum = r * rel_r + g * rel_g + b * rel_b
        reliable_weight = rel_r + rel_g + rel_b
        intensity = ti.select(
            reliable_weight > 1e-4,
            reliable_sum / ti.max(reliable_weight, 1e-4),
            ti.min(r, ti.min(g, b)),
        )
        recovered_r = r * rel_r + intensity * rg * (1.0 - rel_r)
        recovered_g = g * rel_g + intensity * (1.0 - rel_g)
        recovered_b = b * rel_b + intensity * bg * (1.0 - rel_b)
        blend = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        dst[y, x, 0] = r * (1.0 - blend) + recovered_r * blend
        dst[y, x, 1] = g * (1.0 - blend) + recovered_g * blend
        dst[y, x, 2] = b * (1.0 - blend) + recovered_b * blend


@ti.kernel
def chroma_inpaint_seed(
    src: ti.types.ndarray(), ratios: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        peak = ti.max(r / ti.max(wb_r, 1e-4), ti.max(g / ti.max(wb_g, 1e-4), b / ti.max(wb_b, 1e-4)))
        confidence = ti.math.clamp((0.98 - peak) / 0.16, 0.0, 1.0)
        confidence = confidence * confidence * (3.0 - 2.0 * confidence)
        ratios[y, x, 0] = ti.math.clamp(r / ti.max(g, 1e-4), 0.65, 1.45)
        ratios[y, x, 1] = ti.math.clamp(b / ti.max(g, 1e-4), 0.65, 1.45)
        ratios[y, x, 2] = confidence


@ti.kernel
def chroma_inpaint_diffuse(
    guide: ti.types.ndarray(), src: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        own_confidence = src[y, x, 2]
        if own_confidence >= 0.995:
            for channel in ti.static(range(3)):
                dst[y, x, channel] = src[y, x, channel]
        else:
            luma = guide[y, x, 0] * 0.25 + guide[y, x, 1] * 0.5 + guide[y, x, 2] * 0.25
            rg_sum = 0.0
            bg_sum = 0.0
            confidence_sum = 0.0
            weight_sum = 0.0
            for dy, dx in ti.static(ti.ndrange(3, 3)):
                if dy != 1 or dx != 1:
                    ny = ti.math.clamp(y + dy - 1, 0, h - 1)
                    nx = ti.math.clamp(x + dx - 1, 0, w - 1)
                    neighbour_luma = guide[ny, nx, 0] * 0.25 + guide[ny, nx, 1] * 0.5 + guide[ny, nx, 2] * 0.25
                    edge_weight = 1.0 / (1.0 + 24.0 * ti.abs(neighbour_luma - luma))
                    support = 0.08 + src[ny, nx, 2]
                    weight = edge_weight * support
                    rg_sum += src[ny, nx, 0] * weight
                    bg_sum += src[ny, nx, 1] * weight
                    confidence_sum += src[ny, nx, 2] * edge_weight
                    weight_sum += weight
            neighbour_rg = ti.select(weight_sum > 1e-5, rg_sum / weight_sum, 1.0)
            neighbour_bg = ti.select(weight_sum > 1e-5, bg_sum / weight_sum, 1.0)
            mix = ti.math.clamp(0.38 + (1.0 - own_confidence) * 0.44, 0.0, 0.82)
            dst[y, x, 0] = src[y, x, 0] * (1.0 - mix) + neighbour_rg * mix
            dst[y, x, 1] = src[y, x, 1] * (1.0 - mix) + neighbour_bg * mix
            propagated = ti.select(weight_sum > 1e-5, confidence_sum / ti.max(weight_sum, 1e-5), 0.0)
            dst[y, x, 2] = ti.math.clamp(own_confidence * 0.90 + propagated * 0.22, 0.0, 1.0)


@ti.kernel
def recover_highlights_inpainted(
    src: ti.types.ndarray(), ratios: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        raw_r = r / ti.max(wb_r, 1e-4)
        raw_g = g / ti.max(wb_g, 1e-4)
        raw_b = b / ti.max(wb_b, 1e-4)
        peak = ti.max(raw_r, ti.max(raw_g, raw_b))
        rel_r = ti.math.clamp((1.0 - raw_r) / 0.16, 0.0, 1.0)
        rel_g = ti.math.clamp((1.0 - raw_g) / 0.16, 0.0, 1.0)
        rel_b = ti.math.clamp((1.0 - raw_b) / 0.16, 0.0, 1.0)
        rel_r = rel_r * rel_r * (3.0 - 2.0 * rel_r)
        rel_g = rel_g * rel_g * (3.0 - 2.0 * rel_g)
        rel_b = rel_b * rel_b * (3.0 - 2.0 * rel_b)
        reliable_sum = r * rel_r + g * rel_g + b * rel_b
        reliable_weight = rel_r + rel_g + rel_b
        intensity = ti.select(reliable_weight > 1e-4, reliable_sum / reliable_weight, ti.min(r, ti.min(g, b)))
        fade = ti.math.clamp((peak - 0.80) / 0.20, 0.0, 1.0)
        fade = fade * fade * (3.0 - 2.0 * fade) * 0.35
        rg = ti.math.clamp(ratios[y, x, 0], 0.70, 1.30)
        bg = ti.math.clamp(ratios[y, x, 1], 0.70, 1.30)
        rg = rg * (1.0 - fade) + fade
        bg = bg * (1.0 - fade) + fade
        recovered_r = r * rel_r + intensity * rg * (1.0 - rel_r)
        recovered_g = g * rel_g + intensity * (1.0 - rel_g)
        recovered_b = b * rel_b + intensity * bg * (1.0 - rel_b)
        blend = ti.math.clamp((peak - 0.78) / 0.22, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        dst[y, x, 0] = ti.math.clamp(r * (1.0 - blend) + recovered_r * blend, 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(g * (1.0 - blend) + recovered_g * blend, 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(b * (1.0 - blend) + recovered_b * blend, 0.0, 1.0)
