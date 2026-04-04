import os
import ctypes
import numpy as np

class SimilaritySpatialInterface:
    """
    Membungkus pemanggilan fungsi C++ yang telah dioptimalkan.
    Sekarang HANYA menghasilkan weight_map.
    """

    def __init__(self, lib_path):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            self.clib = ctypes.CDLL(lib_path)
            if not hasattr(self.clib, "generate_weight_map_jit"):
                raise AttributeError(
                    "Function 'generate_weight_map_jit' not found in DLL. Check C++ extern \"C\" block."
                )
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
            raise AttributeError(
                f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}"
            )

    def _define_argtypes(self):
        self.clib.generate_weight_map_jit.argtypes = [
            np.ctypeslib.ndpointer(
                dtype=np.float32, ndim=2, flags=("C_CONTIGUOUS", "WRITEABLE")
            ),  # weight_map_sum (2D)
            np.ctypeslib.ndpointer(
                dtype=np.float32, flags="C_CONTIGUOUS"
            ),  # current_image (flattened 1D/3D OK)
            np.ctypeslib.ndpointer(
                dtype=np.float32, flags="C_CONTIGUOUS"
            ),  # reference_image_processed
            np.ctypeslib.ndpointer(
                dtype=np.float32, flags="C_CONTIGUOUS"
            ),  # base_window
            ctypes.c_void_p,  # stability_map_ptr
            np.ctypeslib.ndpointer(
                dtype=np.int32, ndim=1, flags="C_CONTIGUOUS"
            ),  # row_starts
            np.ctypeslib.ndpointer(
                dtype=np.int32, ndim=1, flags="C_CONTIGUOUS"
            ),  # col_starts
            ctypes.c_int,
            ctypes.c_int,  # num_row_starts, num_col_starts
            ctypes.c_int,
            ctypes.c_int,  # tile_h, tile_w
            ctypes.c_int,
            ctypes.c_int,  # h_img, w_img
            ctypes.c_int,  # channels
            ctypes.c_float,  # motion_sensitivity
            ctypes.c_float,  # noise_offset_factor
            ctypes.c_float,  # precomputed_ref_noise_sigma
        ]
        self.clib.generate_weight_map_jit.restype = None

    def call_generate_weight_map_jit(
        self,
        weight_map_sum,
        current_image,
        reference_image_processed,
        base_window,
        stability_map,
        row_starts,
        col_starts,
        tile_h,
        tile_w,
        h,
        w,
        channels,
        motion_sensitivity,
        noise_offset_factor,
        precomputed_ref_noise_sigma,
    ):
        stability_map_ptr = None
        if stability_map is not None:
            if not stability_map.flags["C_CONTIGUOUS"]:
                stability_map = np.ascontiguousarray(stability_map)
            stability_map_ptr = stability_map.ctypes.data_as(ctypes.c_void_p)

        self.clib.generate_weight_map_jit(
            weight_map_sum,
            current_image,
            reference_image_processed,
            base_window,
            stability_map_ptr,
            row_starts,
            col_starts,
            len(row_starts),
            len(col_starts),
            tile_h,
            tile_w,
            h,
            w,
            channels,
            motion_sensitivity,
            noise_offset_factor,
            precomputed_ref_noise_sigma,
        )
