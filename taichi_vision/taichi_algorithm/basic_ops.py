# Basic Image Operations & Computational Photography Implementations
from __future__ import annotations
import os
import builtins
import numpy as np
import taichi as ti

def _resolve_output(source, dst=None):
    """True when the result should stay resident (device-owned)."""
    from taichi.aot_engine import is_resident

    if dst is not None and is_resident(dst):
        return True
    if isinstance(source, dict):
        return any(is_resident(value) for value in source.values())
    if isinstance(source, (list, tuple)):
        return any(is_resident(value) for value in source)
    return is_resident(source)



def demosaic(
    raw_input,
    wb_r=1.0,
    wb_g1=1.0,
    wb_b=1.0,
    wb_g2=1.0,
    cmatrix=None,
    black_level=0.0,
    white_level=1.0,
    c00=0,
    c01=1,
    c10=1,
    c11=2,
    method="hamilton",
    
    dst=None,
    output_bgr_u16=False,
    preserve_headroom=False,
    half_res=False,
    **kwargs,
):
    """Universal demosaicing dispatcher supporting RAW Bayer arrays, files, and GPU buffers."""
    _resident_output = _resolve_output(raw_input, dst=dst)
    import builtins
    import cv2
    _max = builtins.max
    _min = builtins.min

    flip = 0
    bayer = raw_input

    # 1. Handle file path or rawpy object input
    is_rawpy_obj = hasattr(raw_input, "raw_image")
    is_filepath = isinstance(raw_input, (str, bytes, os.PathLike)) and os.path.exists(str(raw_input))

    if is_rawpy_obj or is_filepath:
        try:
            import rawpy
            if is_rawpy_obj:
                raw = raw_input
                close_raw = False
            else:
                raw = rawpy.imread(str(raw_input))
                close_raw = True

            try:
                flip = getattr(raw.sizes, "flip", 0)
                algo = rawpy.DemosaicAlgorithm.PPG if str(method).lower() in ("hamilton", "ha") else (
                    rawpy.DemosaicAlgorithm.BILINEAR if str(method).lower() == "bilinear" else rawpy.DemosaicAlgorithm.AHD
                )
                rgb = raw.postprocess(
                    demosaic_algorithm=algo,
                    half_size=bool(half_res),
                    output_bps=16,
                    no_auto_bright=True,
                    use_camera_wb=True,
                )
                rgb_f32 = (rgb.astype(np.float32) / 65535.0)

                if hasattr(ti, "engine"):
                    try:
                        ti.engine.active_cmatrix = raw.color_matrix[:, :3].astype(np.float32)
                        wb = raw.camera_whitebalance
                        ti.engine.active_wb_r = float(wb[0])
                        ti.engine.active_wb_g1 = float(wb[1])
                        ti.engine.active_wb_b = float(wb[2])
                        ti.engine.active_wb_g2 = float(wb[3] if len(wb) > 3 else wb[1])
                        ti.engine.active_black_level = float(raw.black_level_per_channel[0])
                        ti.engine.active_white_level = float(raw.white_level)
                    except Exception:
                        pass
            finally:
                if close_raw:
                    raw.close()

            if output_bgr_u16:
                bgr = cv2.cvtColor(rgb_f32, cv2.COLOR_RGB2BGR)
                res = np.clip(bgr * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
            else:
                res = rgb_f32

            if dst is not None:
                if hasattr(dst, "from_numpy"):
                    dst.from_numpy(res)
                    return dst
                np.copyto(dst, res)
                return dst

            if _resident_output and hasattr(ti, "engine"):
                return ti.engine.upload(res)
            return res
        except Exception:
            if is_filepath and hasattr(ti, "read_dng"):
                try:
                    dng_info = ti.read_dng(str(raw_input))
                    bayer = dng_info.get("data", dng_info.get("raw_data"))
                    black_level = float(dng_info.get("black_level", black_level))
                    white_level = float(dng_info.get("white_level", white_level))
                    pat = dng_info.get("cfa_pattern", [0, 1, 1, 2])
                    if len(pat) == 4:
                        c00, c01, c10, c11 = pat[0], pat[1], pat[2], pat[3]
                except Exception:
                    pass

    # 2. Handle 2D Bayer array (NumPy or TaichiGPUBuffer)
    if hasattr(bayer, "to_numpy"):
        bayer_arr = bayer.to_numpy()
    else:
        bayer_arr = np.asarray(bayer)

    if bayer_arr.ndim == 3 and bayer_arr.shape[-1] == 1:
        bayer_arr = bayer_arr[..., 0]

    H, W = bayer_arr.shape[:2]
    bl = float(black_level or 0.0)
    wl = float(white_level or 1.0)
    denom = _max(1e-6, float(wl - bl))

    if bayer_arr.dtype == np.uint16:
        bayer_f32 = np.clip((bayer_arr.astype(np.float32) - bl) / denom, 0.0, 1.0)
    elif bayer_arr.dtype == np.uint8:
        bayer_f32 = np.clip((bayer_arr.astype(np.float32) * 257.0 - bl) / denom, 0.0, 1.0)
    else:
        if wl > 1.5:
            bayer_f32 = np.clip((bayer_arr - bl) / denom, 0.0, 1.0)
        else:
            bayer_f32 = np.clip(bayer_arr, 0.0, 1.0)

    pattern_tuple = (int(c00 or 0), int(c01 or 1), int(c10 or 1), int(c11 or 2))

    if half_res:
        h2, w2 = H // 2, W // 2
        ch00 = bayer_f32[0:h2*2:2, 0:w2*2:2]
        ch01 = bayer_f32[0:h2*2:2, 1:w2*2:2]
        ch10 = bayer_f32[1:h2*2:2, 0:w2*2:2]
        ch11 = bayer_f32[1:h2*2:2, 1:w2*2:2]

        channels = {pattern_tuple[0]: ch00, pattern_tuple[1]: ch01, pattern_tuple[2]: ch10, pattern_tuple[3]: ch11}
        r = channels.get(0, ch00)
        g_candidates = [ch for p, ch in zip(pattern_tuple, [ch00, ch01, ch10, ch11]) if p in (1, 3)]
        if len(g_candidates) >= 2:
            g = 0.5 * (g_candidates[0] + g_candidates[1])
        elif len(g_candidates) == 1:
            g = g_candidates[0]
        else:
            g = ch01
        b = channels.get(2, ch11)

        r = r * float(wb_r or 1.0)
        g = g * float(wb_g1 or 1.0)
        b = b * float(wb_b or 1.0)
        rgb = np.stack([r, g, b], axis=-1)
    else:
        bayer_u16 = np.clip(bayer_f32 * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
        is_ea = str(method).lower() in ("hamilton", "ha")

        if pattern_tuple in ((0, 1, 1, 2), (0, 1, 3, 2)):
            code = cv2.COLOR_BAYER_RG2RGB_EA if is_ea else cv2.COLOR_BAYER_RG2RGB
        elif pattern_tuple in ((1, 0, 2, 1), (3, 0, 2, 1)):
            code = cv2.COLOR_BAYER_GR2RGB_EA if is_ea else cv2.COLOR_BAYER_GR2RGB
        elif pattern_tuple in ((1, 2, 0, 1), (3, 2, 0, 1)):
            code = cv2.COLOR_BAYER_GB2RGB_EA if is_ea else cv2.COLOR_BAYER_GB2RGB
        else:
            code = cv2.COLOR_BAYER_BG2RGB_EA if is_ea else cv2.COLOR_BAYER_BG2RGB

        rgb_u16 = cv2.demosaicing(bayer_u16, code)
        rgb = rgb_u16.astype(np.float32) / 65535.0

        rgb[..., 0] *= float(wb_r or 1.0)
        rgb[..., 1] *= float(wb_g1 or 1.0)
        rgb[..., 2] *= float(wb_b or 1.0)

    if cmatrix is not None:
        try:
            cm = np.asarray(cmatrix, dtype=np.float32)
            if cm.shape == (3, 3):
                rgb = np.clip(rgb @ cm.T, 0.0, 1.0)
        except Exception:
            pass

    if output_bgr_u16:
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        res = np.clip(bgr * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
    else:
        res = np.ascontiguousarray(rgb, dtype=np.float32)

    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst

    if _resident_output and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_resize(src, dsize=None, fx=0, fy=0, interpolation=None, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    if isinstance(dsize, (int, float)):
        dsize = (int(dsize), int(dsize))
    elif dsize is None or len(dsize) == 0:
        dsize = (int(arr.shape[1] * fx), int(arr.shape[0] * fy))
    res = cv2.resize(arr, (int(dsize[0]), int(dsize[1])))
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    if _resident_output and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_box_filter(src, kernel_size=(3, 3), dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    ksize = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
    if hasattr(ti, "box_blur") and ti.box_blur is not None and arr.ndim == 2:
        import builtins
        radius = builtins.max(1, ksize[0] // 2)
        res = ti.box_blur(arr, radius)
    else:
        res = cv2.boxFilter(arr, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    if _resident_output and hasattr(ti, "upload"):
        return ti.upload(res)
    return res


def _compat_gaussian_blur(src, ksize=(5, 5), sigmaX=1.0, sigmaY=0, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    ks = ksize if isinstance(ksize, tuple) else (ksize, ksize)
    res = cv2.GaussianBlur(arr, ks, sigmaX, sigmaY=sigmaY)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    if _resident_output and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_remap(src, coordinates=None, map_x=None, map_y=None, output_size=None, coordinate_mode=None, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    is_gpu_src = hasattr(src, "to_numpy")

    if coordinates is not None:
        coords = coordinates.to_numpy() if hasattr(coordinates, "to_numpy") else np.asarray(coordinates)
        if coordinate_mode in ("displacement_xy", "displacement", "flow") or (coordinate_mode is None and coords.shape[-1] == 2):
            h, w = arr.shape[:2]
            if coords.shape[:2] != (h, w):
                coords = cv2.resize(coords, (w, h), interpolation=cv2.INTER_LINEAR)
            grid_y, grid_x = np.mgrid[0:h, 0:w].astype(np.float32)
            mx = grid_x + coords[..., 0]
            my = grid_y + coords[..., 1]
        else:
            if coords.shape[:2] != arr.shape[:2]:
                coords = cv2.resize(coords, (arr.shape[1], arr.shape[0]), interpolation=cv2.INTER_LINEAR)
            mx = coords[..., 0]
            my = coords[..., 1]
    else:
        mx = map_x.to_numpy() if hasattr(map_x, "to_numpy") else np.asarray(map_x)
        my = map_y.to_numpy() if hasattr(map_y, "to_numpy") else np.asarray(map_y)

    res = cv2.remap(arr, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst

    want_gpu = is_gpu_src if _resident_output is None else bool(_resident_output)
    if want_gpu and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_remap_with_flow(src, flow, full_h=None, full_w=None, dst=None, **kwargs):
    dsize = None
    if full_h is not None and full_w is not None:
        dsize = (full_w, full_h)
    return _compat_remap(src, coordinates=flow, coordinate_mode="displacement_xy", output_size=dsize, dst=dst, **kwargs)


def _compat_warp_affine(src, M, dsize=None, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    is_gpu = hasattr(src, "to_numpy")
    h, w = arr.shape[:2]
    out_sz = dsize if dsize is not None else (w, h)
    res = cv2.warpAffine(arr, np.asarray(M, dtype=np.float32), (int(out_sz[0]), int(out_sz[1])))
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    want_gpu = is_gpu if _resident_output is None else bool(_resident_output)
    if want_gpu and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_warp_perspective(src, M, dsize=None, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    arr = src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src)
    is_gpu = hasattr(src, "to_numpy")
    h, w = arr.shape[:2]
    out_sz = dsize if dsize is not None else (w, h)
    res = cv2.warpPerspective(arr, np.asarray(M, dtype=np.float32), (int(out_sz[0]), int(out_sz[1])))
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    want_gpu = is_gpu if _resident_output is None else bool(_resident_output)
    if want_gpu and hasattr(ti, "engine"):
        return ti.engine.upload(res)
    return res


def _compat_farneback_flow(prev, curr, flow=None, pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0, dst=None, **kwargs):
    _resident_output = _resolve_output(flow, dst=dst)
    import cv2
    p = prev.to_numpy() if hasattr(prev, "to_numpy") else np.asarray(prev)
    c = curr.to_numpy() if hasattr(curr, "to_numpy") else np.asarray(curr)
    if p.ndim == 3:
        p = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY if p.shape[-1] == 3 else cv2.COLOR_BGRA2GRAY)
    if c.ndim == 3:
        c = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY if c.shape[-1] == 3 else cv2.COLOR_BGRA2GRAY)
    if p.dtype != np.uint8:
        p = np.clip(p * 255.0, 0, 255).astype(np.uint8)
    if c.dtype != np.uint8:
        c = np.clip(c * 255.0, 0, 255).astype(np.uint8)

    res = cv2.calcOpticalFlowFarneback(p, c, None, pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    if _resident_output and hasattr(ti, "engine"):
        return ti.engine.upload(res, is_vector=True)
    return res


def _compat_phase_correlation(src1, src2, window=None, **kwargs):
    _resident_output = _resolve_output(src1)
    import cv2
    a = src1.to_numpy() if hasattr(src1, "to_numpy") else np.asarray(src1)
    b = src2.to_numpy() if hasattr(src2, "to_numpy") else np.asarray(src2)
    if a.ndim == 3:
        a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    if b.ndim == 3:
        b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    shift, response = cv2.phaseCorrelate(a, b)
    return shift, response


def _compat_upload(arr, is_vector=False, host_accessible=True, **kwargs):
    if hasattr(ti, "engine") and hasattr(ti.engine, "upload"):
        return ti.engine.upload(arr, is_vector=is_vector, host_accessible=host_accessible, **kwargs)
    return arr


def _compat_copy(src, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src))
            return dst
        np.copyto(dst, src.to_numpy() if hasattr(src, "to_numpy") else np.asarray(src))
        return dst
    if hasattr(src, "to_numpy"):
        arr = src.to_numpy()
        want_gpu = True if _resident_output is None else bool(_resident_output)
        if want_gpu and hasattr(ti, "engine"):
            return ti.engine.upload(arr)
        return arr.copy()
    arr = np.asarray(src)
    if _resident_output and hasattr(ti, "engine"):
        return ti.engine.upload(arr)
    return arr.copy()


def _compat_rgb2gray(src, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    is_gpu = hasattr(src, "to_numpy")
    arr = src.to_numpy() if is_gpu else np.asarray(src)
    if arr.ndim == 2:
        res = arr
    else:
        res = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    should_stay_resident = _resident_output if _resident_output is not None else is_gpu
    if should_stay_resident and hasattr(ti, "upload"):
        return ti.upload(res)
    return res


def accumulate_weighted_frame(
    current_image_full,
    weight_map_work,
    final_image_sum,
    weight_map_sum_full,
    **kwargs
):
    import cv2
    cur = current_image_full.to_numpy() if hasattr(current_image_full, "to_numpy") else np.asarray(current_image_full)
    w_work = weight_map_work.to_numpy() if hasattr(weight_map_work, "to_numpy") else np.asarray(weight_map_work)
    h_full, w_full = cur.shape[:2]
    h_work, w_work_w = w_work.shape[:2]
    
    if (h_work, w_work_w) != (h_full, w_full):
        w_upsampled = cv2.resize(w_work, (w_full, h_full), interpolation=cv2.INTER_LINEAR)
    else:
        w_upsampled = w_work

    if w_upsampled.ndim == 2 and cur.ndim == 3:
        w_broad = w_upsampled[..., None]
    else:
        w_broad = w_upsampled

    val_img = cur * w_broad
    val_w = w_broad if (getattr(weight_map_sum_full, "shape", None) and len(weight_map_sum_full.shape) == cur.ndim) else w_upsampled

    def _update_buffer(buf, arr):
        if hasattr(buf, "_rust_buf") and buf._rust_buf is not None:
            buf._rust_buf.write_from_buffer(np.ascontiguousarray(arr, dtype=buf.dtype))
        if hasattr(buf, "_host_array") and buf._host_array is not None:
            np.copyto(buf._host_array, arr)
        elif not hasattr(buf, "to_numpy"):
            buf += arr

    if hasattr(final_image_sum, "to_numpy"):
        fs = final_image_sum.to_numpy()
        fs += val_img
        _update_buffer(final_image_sum, fs)
    else:
        final_image_sum += val_img

    if hasattr(weight_map_sum_full, "to_numpy"):
        ws = weight_map_sum_full.to_numpy()
        ws += val_w
        _update_buffer(weight_map_sum_full, ws)
    else:
        weight_map_sum_full += val_w


def _compat_bgr2gray(src, dst=None, **kwargs):
    _resident_output = _resolve_output(src, dst=dst)
    import cv2
    is_gpu = hasattr(src, "to_numpy")
    arr = src.to_numpy() if is_gpu else np.asarray(src)
    if arr.ndim == 2:
        res = arr
    else:
        res = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    if dst is not None:
        if hasattr(dst, "from_numpy"):
            dst.from_numpy(res)
            return dst
        np.copyto(dst, res)
        return dst
    should_stay_resident = _resident_output if _resident_output is not None else is_gpu
    if should_stay_resident and hasattr(ti, "upload"):
        return ti.upload(res)
    return res


def cvtColor(src, code, dst=None, session=None, **kwargs):
    """OpenCV-compatible color conversion for numpy and GPU buffer objects."""
    import cv2
    from taichi_vision.taichi_algorithm import common
    return common.cvtColor(src, code, dst=dst, session=session, **kwargs)


