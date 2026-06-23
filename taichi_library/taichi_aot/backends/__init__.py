import ctypes
import os
import sys

# -------------------------------------------------------------------------
# Dynamic Argument Structure for C++ Engine
# -------------------------------------------------------------------------
class DynamicArg(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("arg_type", ctypes.c_int),  # 0: ndarray, 1: scalar
        ("dtype", ctypes.c_int),  # 0: f32, 1: i32, 2: u8, 3: u16
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_int * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_int * 8),
        ("is_vector", ctypes.c_int),
        ("vector_dim", ctypes.c_int),
        ("val_u64", ctypes.c_uint64),
    ]


class BaseAOTBackend:
    """Base interface for AOT backends. Handles ctypes binding and common routines."""
    
    def __init__(self, dll_name: str):
        self.dll_name = dll_name
        self._lib = None
        self._load_dll()
        self._setup_prototypes()
        self.allocated_pointers = set()
        
    def _load_dll(self):
        # Suppress loader debug warnings on Windows
        os.environ["VK_LOADER_DEBUG"] = "error"
        if os.name == "nt":
            try:
                ctypes.CDLL("msvcrt.dll")._putenv(b"VK_LOADER_DEBUG=error")
            except Exception:
                pass

        script_dir = os.path.dirname(os.path.abspath(__file__))
        aot_dll_dir = os.path.abspath(
            os.path.join(script_dir, "../../taichi_algorithm/aot_py/aot_dll")
        )
        engine_dll_path = os.path.join(aot_dll_dir, self.dll_name)

        if os.name == "nt" and os.path.exists(aot_dll_dir):
            try:
                os.add_dll_directory(aot_dll_dir)
            except Exception:
                pass

            # Try to add Taichi bin directory for dependency resolution
            try:
                import importlib.util
                spec = importlib.util.find_spec("taichi")
                if spec is not None and spec.origin is not None:
                    ti_root = os.path.dirname(spec.origin)
                    ti_bin = os.path.join(ti_root, "_lib", "c_api", "bin")
                    if os.path.exists(ti_bin):
                        os.add_dll_directory(ti_bin)
                    
                    ti_runtime = os.path.join(ti_root, "_lib", "runtime")
                    if os.path.exists(ti_runtime):
                        os.environ["TI_LIB_DIR"] = ti_runtime
            except Exception:
                pass

        try:
            self._lib = ctypes.CDLL(engine_dll_path)
            print(f"[AOTEngine] Loaded modular backend: {self.dll_name}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load modular backend DLL {self.dll_name} at {engine_dll_path}\nError: {e}"
            )

    def _setup_prototypes(self):
        lib = self._lib
        
        lib.init_aot_engine.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.init_aot_engine.restype = ctypes.c_void_p

        try:
            lib.scan_vulkan_devices.argtypes = []
            lib.scan_vulkan_devices.restype = ctypes.c_char_p
        except AttributeError:
            pass

        lib.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lib.load_aot_module.restype = ctypes.c_void_p

        lib.destroy_aot_module.argtypes = [ctypes.c_void_p]
        lib.destroy_aot_module.restype = None

        lib.allocate_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_int]
        lib.allocate_gpu_buffer.restype = ctypes.c_void_p

        lib.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.free_gpu_buffer.restype = None

        lib.write_to_gpu_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        lib.write_to_gpu_buffer.restype = None

        lib.read_from_gpu_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        lib.read_from_gpu_buffer.restype = None

        lib.map_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.map_gpu_buffer.restype = ctypes.c_void_p

        lib.unmap_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.unmap_gpu_buffer.restype = None

        lib.copy_gpu_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        lib.copy_gpu_buffer.restype = None

        lib.run_aot_graph.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(DynamicArg),
            ctypes.c_int,
        ]
        lib.run_aot_graph.restype = None

        lib.sync_runtime.argtypes = [ctypes.c_void_p]
        lib.sync_runtime.restype = None

        lib.clear_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lib.clear_pipeline.restype = None

        lib.add_to_pipeline.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(DynamicArg),
            ctypes.c_int,
        ]
        lib.add_to_pipeline.restype = None

        lib.run_pipeline.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(DynamicArg),
            ctypes.c_int,
        ]
        lib.run_pipeline.restype = None

        lib.ti_imread_to_gpu.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.ti_imread_to_gpu.restype = ctypes.c_void_p

        lib.ti_imwrite_from_gpu.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        lib.ti_imwrite_from_gpu.restype = ctypes.c_bool

        lib.ti_cast_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        lib.ti_cast_buffer.restype = ctypes.c_bool

    # --- Delegate API calls to C-API ---
    def init_engine(self, arch_id: int, device_id: int) -> int:
        return self._lib.init_aot_engine(arch_id, device_id)

    def scan_devices(self) -> str:
        if hasattr(self._lib, "scan_vulkan_devices"):
            return self._lib.scan_vulkan_devices().decode("utf-8")
        return ""

    def load_module(self, runtime, tcm_path: bytes) -> int:
        return self._lib.load_aot_module(runtime, tcm_path)

    def destroy_module(self, module_ptr):
        self._lib.destroy_aot_module(module_ptr)

    def allocate_buffer(self, runtime, size: int, host_accessible: int) -> int:
        ptr = self._lib.allocate_gpu_buffer(runtime, size, host_accessible)
        ptr_val = ptr.value if hasattr(ptr, "value") else ptr
        if ptr_val:
            self.allocated_pointers.add(ptr_val)
        return ptr_val

    def free_buffer(self, runtime, memory):
        ptr_val = memory.value if hasattr(memory, "value") else memory
        if ptr_val is None or ptr_val == 0:
            return
        if ptr_val not in self.allocated_pointers:
            print(f"[AOTEngine WARNING] Ignored attempt to free invalid or already freed buffer memory handle: {ptr_val}")
            return
        self._lib.free_gpu_buffer(runtime, memory)
        self.allocated_pointers.discard(ptr_val)

    def write_buffer(self, runtime, memory, data, size: int):
        ptr_val = memory.value if hasattr(memory, "value") else memory
        if ptr_val is None or ptr_val not in self.allocated_pointers:
            return
        self._lib.write_to_gpu_buffer(runtime, memory, data, size)

    def read_buffer(self, runtime, memory, data, size: int):
        ptr_val = memory.value if hasattr(memory, "value") else memory
        if ptr_val is None or ptr_val not in self.allocated_pointers:
            return
        self._lib.read_from_gpu_buffer(runtime, memory, data, size)

    def map_buffer(self, runtime, memory) -> int:
        ptr_val = memory.value if hasattr(memory, "value") else memory
        if ptr_val is None or ptr_val not in self.allocated_pointers:
            return 0
        return self._lib.map_gpu_buffer(runtime, memory)

    def unmap_buffer(self, runtime, memory):
        ptr_val = memory.value if hasattr(memory, "value") else memory
        if ptr_val is None or ptr_val not in self.allocated_pointers:
            return
        self._lib.unmap_gpu_buffer(runtime, memory)

    def copy_buffer(self, runtime, src, dst, size: int):
        src_val = src.value if hasattr(src, "value") else src
        dst_val = dst.value if hasattr(dst, "value") else dst
        if src_val is None or src_val not in self.allocated_pointers:
            return
        if dst_val is None or dst_val not in self.allocated_pointers:
            return
        self._lib.copy_gpu_buffer(runtime, src, dst, size)

    def sync(self, runtime):
        self._lib.sync_runtime(runtime)

    def cast_buffer(self, src_ptr, dst_ptr, num_elements: int, src_type: int, dst_type: int) -> bool:
        return self._lib.ti_cast_buffer(src_ptr, dst_ptr, num_elements, src_type, dst_type)

    def run_graph(self, runtime, module_ptr, graph_name: bytes, args_array, num_args: int):
        self._lib.run_aot_graph(runtime, module_ptr, graph_name, args_array, num_args)

    def clear_pipeline(self, module_ptr, pipeline_name: bytes):
        self._lib.clear_pipeline(module_ptr, pipeline_name)

    def add_to_pipeline(self, module_ptr, pipeline_name: bytes, graph_name: bytes, args_array, num_args: int):
        self._lib.add_to_pipeline(module_ptr, pipeline_name, graph_name, args_array, num_args)

    def run_pipeline(self, runtime, pipeline_name: bytes, old_handles, new_args, num_overrides: int):
        self._lib.run_pipeline(runtime, pipeline_name, old_handles, new_args, num_overrides)

    def imread(self, runtime, path: bytes, out_w, out_h, out_c, out_d) -> int:
        ptr = self._lib.ti_imread_to_gpu(runtime, path, out_w, out_h, out_c, out_d)
        ptr_val = ptr.value if hasattr(ptr, "value") else ptr
        if ptr_val:
            self.allocated_pointers.add(ptr_val)
        return ptr_val

    def imwrite(self, runtime, path: bytes, gpu_mem, w: int, h: int, c: int, d: int) -> bool:
        return self._lib.ti_imwrite_from_gpu(runtime, path, gpu_mem, w, h, c, d)
