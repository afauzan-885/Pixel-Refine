"""Optional linear camera-RGB highlight recovery for Taichi AOT."""

import os
import sys

import taichi as ti

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module


@ti.kernel
def _highlight_recover_rgb(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, strength: ti.f32,
    h: ti.i32, w: ti.i32,
):
    """Preserve valid luminance while recovering clipped channel chroma."""
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        wb_scale = ti.max(wb_r, ti.max(wb_g, wb_b))
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
                ti.max(
                    ng / ti.max(wb_g, 1e-4),
                    nb / ti.max(wb_b, 1e-4),
                ),
            )
            if ng > 1e-5:
                distance = ti.cast(ti.abs(dy - 5) + ti.abs(dx - 5), ti.f32)
                confidence = ti.math.clamp(
                    (1.0 - neighbour_peak) / 0.12, 0.0, 1.0
                )
                confidence = confidence * confidence * (3.0 - 2.0 * confidence)
                weight = confidence / (1.0 + distance)
                rg_sum += ti.math.clamp(nr / ng, 0.45, 1.80) * weight
                bg_sum += ti.math.clamp(nb / ng, 0.45, 1.80) * weight
                weight_sum += weight
        rg = ti.select(weight_sum > 1e-5, rg_sum / weight_sum, 1.0)
        bg = ti.select(weight_sum > 1e-5, bg_sum / weight_sum, 1.0)
        fade = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        fade = (
            fade
            * fade
            * (3.0 - 2.0 * fade)
            * ti.math.clamp(strength, 0.0, 1.0)
        )
        # Only a fully clipped sensor highlight should approach neutral white.
        # One- and two-channel clipping retain the propagated boundary colour.
        raw_floor = ti.min(raw_r, ti.min(raw_g, raw_b))
        fully_clipped = ti.math.clamp((raw_floor - 0.94) / 0.06, 0.0, 1.0)
        fully_clipped = fully_clipped * fully_clipped * (3.0 - 2.0 * fully_clipped)
        neutral_mix = fade * fully_clipped * 0.35
        rg = rg * (1.0 - neutral_mix) + neutral_mix
        bg = bg * (1.0 - neutral_mix) + neutral_mix
        rel_r = ti.math.clamp((1.0 - raw_r) / 0.12, 0.0, 1.0)
        rel_g = ti.math.clamp((1.0 - raw_g) / 0.12, 0.0, 1.0)
        rel_b = ti.math.clamp((1.0 - raw_b) / 0.12, 0.0, 1.0)
        rel_r = rel_r * rel_r * (3.0 - 2.0 * rel_r)
        rel_g = rel_g * rel_g * (3.0 - 2.0 * rel_g)
        rel_b = rel_b * rel_b * (3.0 - 2.0 * rel_b)
        # Estimate a common green-space intensity from only reliable channels.
        # This preserves valid channels instead of averaging their RGB values.
        green_sum = (
            (r / ti.max(rg, 1e-4)) * rel_r
            + g * rel_g
            + (b / ti.max(bg, 1e-4)) * rel_b
        )
        reliable_weight = rel_r + rel_g + rel_b
        green_intensity = ti.select(
            reliable_weight > 1e-4,
            green_sum / reliable_weight,
            ti.min(g, ti.min(r / ti.max(rg, 1e-4), b / ti.max(bg, 1e-4))),
        )
        recovered_r = r * rel_r + green_intensity * rg * (1.0 - rel_r)
        recovered_g = g * rel_g + green_intensity * (1.0 - rel_g)
        recovered_b = b * rel_b + green_intensity * bg * (1.0 - rel_b)
        blend = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        blend = (
            blend
            * blend
            * (3.0 - 2.0 * blend)
            * ti.math.clamp(strength, 0.0, 1.0)
        )
        dst[y, x, 0] = ti.math.clamp(
            (r * (1.0 - blend) + recovered_r * blend) / ti.max(wb_scale, 1e-4), 0.0, 1.0
        )
        dst[y, x, 1] = ti.math.clamp(
            (g * (1.0 - blend) + recovered_g * blend) / ti.max(wb_scale, 1e-4), 0.0, 1.0
        )
        dst[y, x, 2] = ti.math.clamp(
            (b * (1.0 - blend) + recovered_b * blend) / ti.max(wb_scale, 1e-4), 0.0, 1.0
        )


def compile_highlight_recovery_tcm(
    arch=ti.vulkan, save_path="highlight_recovery_vulkan.tcm"
):
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)
    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    wb_r = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_r", ti.f32)
    wb_g = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_g", ti.f32)
    wb_b = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_b", ti.f32)
    strength = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "strength", ti.f32)
    h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        _highlight_recover_rgb,
        src, dst, wb_r, wb_g, wb_b, strength, h, w,
    )
    module.add_graph("highlight_recover_rgb", graph.compile())
    archive_module(module, save_path)
    ti.reset()


if __name__ == "__main__":
    target_id = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip() or "vulkan_x86_64_windows"
    output = os.path.abspath(
        os.path.join(
            file_dir,
            f"../aot_tcm/{target_id}/highlight_recovery_{target_id}.tcm",
        )
    )
    os.makedirs(os.path.dirname(output), exist_ok=True)
    compile_highlight_recovery_tcm(ti.vulkan, output)
