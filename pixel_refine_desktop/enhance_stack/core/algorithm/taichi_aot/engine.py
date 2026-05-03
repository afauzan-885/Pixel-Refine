import ctypes
import os
import sys
import numpy as np

# -------------------------------------------------------------------------
# Dynamic Argument Structure for C++ Engine
# -------------------------------------------------------------------------
class DynamicArg(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("is_ndarray", ctypes.c_int), # 0=Int32, 1=Float32, 2=NDArray
        
        # Scalar values
        ("val_i32", ctypes.c_int32),
        ("val_f32", ctypes.c_float),
        
        # NDArray values
        ("ndarray_memory", ctypes.c_void_p),
        ("elem_type", ctypes.c_int), # TiDataType enum value
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_uint32 * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_uint32 * 8),
    ]

# -------------------------------------------------------------------------
# Global State
# -------------------------------------------------------------------------
_LIB = None
_RUNTIME = None

def _init_aot_bridge():
    global _LIB, _RUNTIME
    if _LIB is not None:
        return
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Locate taichi_aot_engine.dll (in taichi_algorithm/aot_py/aot_dll)
    aot_dll_dir = os.path.abspath(os.path.join(script_dir, "../taichi_algorithm/aot_py/aot_dll"))
    engine_dll_path = os.path.join(aot_dll_dir, "taichi_aot_engine.dll")
    
    # Path to ui/data for production taichi_c_api.dll
    ui_data_bin = os.path.abspath(os.path.join(script_dir, "../../../../../ui/data"))
    
    # Add directories to search path on Windows
    if os.name == 'nt':
        if os.path.exists(aot_dll_dir):
            os.add_dll_directory(aot_dll_dir)
            
        taichi_c_api_bin = ui_data_bin
        if os.path.exists(taichi_c_api_bin):
            os.add_dll_directory(taichi_c_api_bin)
        else:
            # Fallback to dev venv path
            venv_bin = r"e:\APP Developer\Pixel Refine\venv\Lib\site-packages\taichi\_lib\c_api\bin"
            if os.path.exists(venv_bin):
                os.add_dll_directory(venv_bin)
                
    # Set TI_LIB_DIR for Taichi C-API internal use (fixes "invalid state" error)
    if "TI_LIB_DIR" not in os.environ:
        try:
            import taichi as ti
            ti_path = os.path.dirname(ti.__file__)
            ti_lib_dir = os.path.join(ti_path, "_lib", "runtime")
            if os.path.exists(ti_lib_dir):
                os.environ["TI_LIB_DIR"] = ti_lib_dir
        except:
            pass

    try:
        _LIB = ctypes.CDLL(engine_dll_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load Generic AOT Engine DLL at {engine_dll_path}\nError: {e}")

    # Setup argument types
    _LIB.init_aot_engine.argtypes = [ctypes.c_int, ctypes.c_int]
    _LIB.init_aot_engine.restype = ctypes.c_void_p
    
    _LIB.scan_vulkan_devices.argtypes = []
    _LIB.scan_vulkan_devices.restype = ctypes.c_char_p
    
    _LIB.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _LIB.load_aot_module.restype = ctypes.c_void_p
    
    _LIB.destroy_aot_module.argtypes = [ctypes.c_void_p]
    _LIB.destroy_aot_module.restype = None

    _LIB.allocate_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_int]
    _LIB.allocate_gpu_buffer.restype = ctypes.c_void_p

    _LIB.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.free_gpu_buffer.restype = None

    _LIB.write_to_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64]
    _LIB.write_to_gpu_buffer.restype = None

    _LIB.read_from_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64]
    _LIB.read_from_gpu_buffer.restype = None

    _LIB.run_aot_graph.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(DynamicArg), ctypes.c_int]
    _LIB.run_aot_graph.restype = None

    _LIB.sync_runtime.argtypes = [ctypes.c_void_p]
    _LIB.sync_runtime.restype = None

    # Backend selection: 0=Vulkan, 1=CUDA, 2=CPU
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()
    arch_id = 0
    if arch_str == "cuda": arch_id = 1
    elif arch_str == "cpu": arch_id = 2
    
    device_id = int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", "0"))
    
    _RUNTIME = _LIB.init_aot_engine(arch_id, device_id)
    if not _RUNTIME:
        raise RuntimeError(f"Failed to initialize {arch_str.upper()} AOT Runtime (Device {device_id}) in Engine.")
    
    # Store active arch for filename matching
    AOTEngine._active_arch = arch_str

# -------------------------------------------------------------------------
# GPU Buffer Manager (Zero-Overhead Memory)
# -------------------------------------------------------------------------
class BufferPool:
    def __init__(self):
        self.free_buffers = {} # size_bytes -> list of handles

    def acquire(self, size_bytes):
        if size_bytes in self.free_buffers and self.free_buffers[size_bytes]:
            return self.free_buffers[size_bytes].pop()
        return None

    def release(self, size_bytes, handle):
        if size_bytes not in self.free_buffers:
            self.free_buffers[size_bytes] = []
        self.free_buffers[size_bytes].append(handle)

    def clear(self):
        global _LIB, _RUNTIME
        if _LIB and _RUNTIME:
            for size, handles in self.free_buffers.items():
                for h in handles:
                    try:
                        _LIB.free_gpu_buffer(_RUNTIME, h)
                    except: pass
        self.free_buffers = {}


class TaichiGPUBuffer:
    def __init__(self, size_bytes, handle, shape, dtype=np.float32, is_vec2=False, engine=None):
        self.size_bytes = size_bytes
        self.handle = handle  # void* pointer from C++ bridge
        self.shape = shape
        self.dtype = dtype
        self.is_vec2 = is_vec2
        self.engine = engine # Reference to AOTEngine to access its pool

    def __del__(self):
        """Automatically return handle to pool or free VRAM."""
        if self.handle is not None:
            if self.engine and hasattr(self.engine, 'buffer_pool'):
                self.engine.buffer_pool.release(self.size_bytes, self.handle)
            elif _LIB is not None and _RUNTIME is not None:
                try:
                    _LIB.free_gpu_buffer(_RUNTIME, self.handle)
                except:
                    pass
            self.handle = None

    def to_numpy(self) -> np.ndarray:
        """Download data from VRAM back to a NumPy array."""
        _init_aot_bridge()
        
        actual_shape = self.shape
        # Restore trailing '2/3/4' for vector buffers if missing in shape attribute
        # Note: In our current implementation, we keep the full shape in self.shape
        res = np.zeros(actual_shape, dtype=self.dtype)
        _LIB.read_from_gpu_buffer(_RUNTIME, self.handle, res.ctypes.data_as(ctypes.c_void_p), self.size_bytes)
        return res

    def view_as_vector(self, is_vector: bool = True) -> 'TaichiGPUBuffer':
        """Return a view of this buffer with a different vector flag."""
        return TaichiGPUBuffer(self.size_bytes, self.handle, self.shape, self.dtype, is_vec2=is_vector, engine=self.engine)

# -------------------------------------------------------------------------
# The Generic AOT Engine Class
# -------------------------------------------------------------------------
class AOTModuleWrapper:
    def __init__(self, module_ptr):
        self.module_ptr = module_ptr
        
    def __del__(self):
        if self.module_ptr is not None and _LIB is not None:
            try:
                _LIB.destroy_aot_module(self.module_ptr)
            except:
                pass
            self.module_ptr = None

    def run(self, graph_name: str, **kwargs):
        """
        Executes an AOT graph by dynamically parsing kwargs into C++ DynamicArgs.
        Args:
            graph_name: The name of the graph in the .tcm file.
            **kwargs: Can be int, float, TaichiGPUBuffer.
        """
        if not self.module_ptr:
            raise RuntimeError("AOT Module is destroyed.")
            
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        
        for i, (key, value) in enumerate(kwargs.items()):
            args_array[i].name = key.encode('utf-8')
            
            if isinstance(value, int):
                args_array[i].is_ndarray = 0
                args_array[i].val_i32 = value
            elif isinstance(value, float):
                args_array[i].is_ndarray = 1
                args_array[i].val_f32 = value
            elif isinstance(value, TaichiGPUBuffer):
                args_array[i].is_ndarray = 2
                
                # Map numpy dtype to TiDataType enum
                if value.dtype == np.int32:
                    args_array[i].elem_type = 5 # TI_DATA_TYPE_I32
                elif value.dtype == np.uint8:
                    args_array[i].elem_type = 7 # TI_DATA_TYPE_U8
                elif value.dtype == np.uint16:
                    args_array[i].elem_type = 8 # TI_DATA_TYPE_U16
                else:
                    args_array[i].elem_type = 1 # TI_DATA_TYPE_F32
                
                args_array[i].ndarray_memory = value.handle
                
                # Logic to split field shape and vector shape
                # Support vec2, vec3, vec4 automatically based on shape
                shape = value.shape
                dim_count = len(shape)
                
                # Check if it's a vector field (is_vector or last dim is 2, 3, 4)
                is_vector = getattr(value, 'is_vector', False) or getattr(value, 'is_vec2', False)
                vec_size = shape[-1] if (dim_count > 0 and shape[-1] in [2, 3, 4]) else 1
                
                if is_vector and vec_size > 1:
                    dim_count -= 1
                    args_array[i].elem_dim_count = 1
                    args_array[i].elem_shape[0] = vec_size
                else:
                    args_array[i].elem_dim_count = 0
                
                args_array[i].dim_count = dim_count
                for d in range(dim_count):
                    args_array[i].shape[d] = shape[d]
            else:
                raise TypeError(f"Unsupported argument type for '{key}': {type(value)}. Must be int, float, or TaichiGPUBuffer.")
                
        # Launch the generic graph
        _LIB.run_aot_graph(_RUNTIME, self.module_ptr, graph_name.encode('utf-8'), args_array, num_args)


class AOTEngine:
    """The Singleton Generic AOT Engine for Taichi."""
    _instance = None
    _active_arch = "vulkan"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AOTEngine, cls).__new__(cls)
            _init_aot_bridge()
            cls._instance.modules = {}
            cls._instance.buffer_pool = BufferPool()
        return cls._instance
        
    def get_vulkan_devices(self):
        """Returns a list of available Vulkan device names."""
        _init_aot_bridge()
        devices_raw = _LIB.scan_vulkan_devices()
        if not devices_raw:
            return []
        return [d.strip() for d in devices_raw.decode('utf-8').split(';') if d.strip()]
        
    def reinit(self, device_id=0):
        """Re-initializes the Taichi AOT Runtime on a specific device index."""
        global _RUNTIME
        arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()
        arch_id = 0
        if arch_str == "cuda": arch_id = 1
        elif arch_str == "cpu": arch_id = 2
        
        # Update environment for persistence
        os.environ["PIXEL_REFINE_AOT_DEVICE"] = str(device_id)
        
        # Clear pool and modules
        if hasattr(self, 'buffer_pool'):
            self.buffer_pool.clear()
        
        new_runtime = _LIB.init_aot_engine(arch_id, device_id)
        if not new_runtime:
            raise RuntimeError(f"Failed to re-initialize {arch_str.upper()} AOT Runtime on Device {device_id}")
            
        _RUNTIME = new_runtime
        self.modules = {} # Clear cached modules as they are tied to the old runtime
        print(f"[TaichiAOT] Runtime switched to Device {device_id} ({arch_str.upper()})")

    def sync(self):
        """Manually synchronize the GPU (wait for all kernels to finish)."""
        if _RUNTIME:
            _LIB.sync_runtime(_RUNTIME)

    def load(self, tcm_path: str) -> AOTModuleWrapper:
        """Loads a TCM file and caches the module. Automatically handles architecture suffixes."""
        # 1. Resolve path with architecture suffix if needed
        base, ext = os.path.splitext(tcm_path)
        
        # If the path already has a suffix, use it. Otherwise, try to find the arch-specific one.
        potential_paths = [
            tcm_path,
            f"{base}_{self._active_arch}{ext}"
        ]
        
        resolved_path = None
        for p in potential_paths:
            if os.path.exists(p):
                resolved_path = p
                break
        
        if not resolved_path:
            raise FileNotFoundError(f"TCM file not found (tried {potential_paths})")
            
        if resolved_path in self.modules:
            return self.modules[resolved_path]
            
        module_ptr = _LIB.load_aot_module(_RUNTIME, resolved_path.encode('utf-8'))
        if not module_ptr:
            raise RuntimeError(f"Failed to load AOT Module: {resolved_path}")
            
        wrapper = AOTModuleWrapper(module_ptr)
        self.modules[resolved_path] = wrapper
        return wrapper

    def upload(self, arr: np.ndarray, is_vector: bool = False, is_vec2: bool = False) -> TaichiGPUBuffer:
        """Upload a NumPy array to GPU VRAM and return a smart buffer handle."""
        arr_dtype = arr.dtype
        if arr_dtype not in [np.float32, np.int32, np.uint8, np.uint16]:
            raise ValueError(f"Unsupported dtype: {arr_dtype}")
            
        arr_contiguous = np.ascontiguousarray(arr, dtype=arr_dtype)
        size_bytes = arr_contiguous.nbytes
        
        # Check pool first
        handle = self.buffer_pool.acquire(size_bytes)
        if not handle:
            handle = _LIB.allocate_gpu_buffer(_RUNTIME, size_bytes, 1)
        
        if not handle:
            raise MemoryError("Failed to allocate GPU Buffer.")
        
        _LIB.write_to_gpu_buffer(_RUNTIME, handle, arr_contiguous.ctypes.data_as(ctypes.c_void_p), size_bytes)
        
        # Standardize on is_vector
        vector_flag = is_vector or is_vec2
            
        return TaichiGPUBuffer(size_bytes, handle, arr.shape, dtype=arr_dtype, is_vec2=vector_flag, engine=self)

    def allocate(self, shape, dtype=np.float32, is_vector: bool = False, is_vec2: bool = False) -> TaichiGPUBuffer:
        """Allocate an empty GPU buffer."""
        if isinstance(shape, int):
            shape = (shape,)
            
        # Standardize on is_vector
        vector_flag = is_vector or is_vec2
        
        # Auto-detect removed to prevent conflicts with 3D scalar kernels
        if not vector_flag and is_vec2:
            if len(shape) > 0 and shape[-1] != 2:
                shape = shape + (2,)
            vector_flag = True
            
        elements = 1
        for s in shape: elements *= s
        
        dtype_obj = np.dtype(dtype)
        size_bytes = int(elements * dtype_obj.itemsize)
            
        # Check pool first
        handle = self.buffer_pool.acquire(size_bytes)
        if not handle:
            handle = _LIB.allocate_gpu_buffer(_RUNTIME, size_bytes, 1)
            
        if not handle:
            raise MemoryError("Failed to allocate GPU Buffer.")
            
        return TaichiGPUBuffer(size_bytes, handle, shape, dtype=dtype_obj.type, is_vec2=vector_flag, engine=self)
