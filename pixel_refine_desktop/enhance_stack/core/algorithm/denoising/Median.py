"""Median-stack denoising adapter and public UI facade."""

import gc

import numpy as np

from ._common_helpers import restore_output_dtype


class MedianDenoisingAlgorithm:
    NAME = "Median"
    KIND = "denoising"
    DESCRIPTION = "Median stack of all input frames."

    @staticmethod
    def _to_float32(image):
        image = np.asarray(image)
        if np.issubdtype(image.dtype, np.integer):
            scale = 65535.0 if image.dtype.itemsize > 1 else 255.0
            return np.ascontiguousarray(image.astype(np.float32) / scale)
        if np.issubdtype(image.dtype, np.floating):
            values = np.asarray(image, dtype=np.float32)
            max_value = float(np.max(values)) if values.size else 1.0
            if max_value > 1.5:
                scale = 65535.0 if max_value > 255.0 else 255.0
                values = values / np.float32(scale)
            return np.ascontiguousarray(values, dtype=np.float32)
        return np.ascontiguousarray(image.astype(np.float32), dtype=np.float32)

    def run(self, ctx, frames=None, batch_plan=None):
        del batch_plan
        image_paths = list(getattr(ctx, "image_paths", None) or [])
        is_raw = bool(getattr(ctx, "is_linear_mode", False))

        if image_paths:
            from .fusionet_engine.weightnet_inference import load_rgb_linear_image

            source = image_paths
            load_path_source = True
        else:
            source = list(frames or [])
            load_path_source = False

        if not source:
            print("[Median] No input frames available.")
            return None

        from taichi_vision import taichi_aot

        stack = None
        try:
            for index, item in enumerate(source):
                if load_path_source:
                    frame = load_rgb_linear_image(item, is_raw=is_raw)
                else:
                    frame = self._to_float32(item)

                if stack is None:
                    stack_shape = (len(source), *frame.shape)
                    stack = np.empty(stack_shape, dtype=np.float32)
                elif frame.shape != stack.shape[1:]:
                    frame = taichi_aot.resize(
                        frame,
                        (stack.shape[2], stack.shape[1]),
                        interpolation=taichi_aot.INTER_LINEAR,
                    )
                    frame = np.ascontiguousarray(frame, dtype=np.float32)

                stack[index] = frame
                del frame
                if getattr(ctx, "update_progress", None):
                    ctx.update_progress(
                        25 + int((index + 1) * 65 / max(1, len(source))),
                        f"Median stacking {index + 1}/{len(source)}...",
                    )

            # In-place selection avoids the extra full-frame copy made by
            # np.median for a 12 MP burst. For an even burst, average the two
            # central order statistics to preserve NumPy median semantics.
            count = stack.shape[0]
            high = count // 2
            low = high if count % 2 else high - 1
            stack.partition((low, high), axis=0)
            result = np.empty_like(stack[0], dtype=np.float32)
            if low == high:
                np.copyto(result, stack[high])
            else:
                np.add(stack[low], stack[high], out=result)
                result *= np.float32(0.5)

            ref_dtype = getattr(ctx, "ref_dtype", None)
            if ref_dtype is None:
                ref_dtype = np.uint16 if is_raw else np.uint8
            if np.issubdtype(np.dtype(ref_dtype), np.integer):
                result = restore_output_dtype(result, ref_dtype)
            return result
        finally:
            if stack is not None:
                del stack
            gc.collect()


def running_median(parent=None, single_process=None, batch_id=None, progress_callback=None, stop_callback=None):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import running_mf_denoiser
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode="median",
        output_suffix="median"
    )

