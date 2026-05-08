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
# Dynamic Argument Population Helper
# -------------------------------------------------------------------------
def _populate_dynamic_arg(arg: DynamicArg, key: str, value):
    """Internal helper to fill DynamicArg metadata consistently."""
    arg.name = key.encode('utf-8')
    
    if isinstance(value, int):
        arg.is_ndarray = 0
        arg.val_i32 = value
    elif isinstance(value, float):
        arg.is_ndarray = 1
        arg.val_f32 = value
    elif isinstance(value, (TaichiGPUBuffer, TaichiPlaceholder)):
        arg.is_ndarray = 2
        
        # Map numpy dtype to TiDataType enum
        dtype_map = {np.int32: 5, np.uint8: 7, np.uint16: 8, np.float32: 1}
        arg.elem_type = dtype_map.get(value.dtype, 1)
        arg.ndarray_memory = value.handle
        
        shape = value.shape
        dim_count = len(shape)
        
        # AOT Convention: 3-channel images are Vector fields (ndim=2, elem_shape=3)
        if dim_count == 3 and shape[2] == 3:
            arg.dim_count = 2
            arg.shape[0] = shape[0]
            arg.shape[1] = shape[1]
            arg.elem_dim_count = 1
            arg.elem_shape[0] = 3
        else:
            arg.dim_count = dim_count
            for d in range(dim_count):
                arg.shape[d] = shape[d]
            arg.elem_dim_count = 0
    else:
        # Backward compatibility for direct Taichi NDArrays (if any)
        if hasattr(value, "ptr"):
            arg.is_ndarray = 2
            arg.ndarray_memory = value.ptr
            # Fallback metadata mapping
            arg.elem_type = 1
            arg.dim_count = len(value.shape)
            for d, s in enumerate(value.shape): arg.shape[d] = s
            arg.elem_dim_count = 0
        else:
            raise TypeError(f"Unsupported argument type for '{key}': {type(value)}")

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
    aot_dll_dir = os.path.abspath(os.path.join(script_dir, "../taichi_algorithm/aot_py/aot_dll"))
    engine_dll_path = os.path.join(aot_dll_dir, "taichi_aot_engine.dll")
    
    if os.name == 'nt' and os.path.exists(aot_dll_dir):
        os.add_dll_directory(aot_dll_dir)
        
        # Add Taichi runtime bin for DLL resolution
        try:
            import taichi as ti
            ti_bin = os.path.join(os.path.dirname(ti.__file__), "_lib", "c_api", "bin")
            if os.path.exists(ti_bin): os.add_dll_directory(ti_bin)
        except: pass

    try:
        _LIB = ctypes.CDLL(engine_dll_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load Generic AOT Engine DLL at {engine_dll_path}\nError: {e}")

    # Setup C-API Function Prototypes
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

    _LIB.map_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.map_gpu_buffer.restype = ctypes.c_void_p

    _LIB.unmap_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.unmap_gpu_buffer.restype = None

    _LIB.copy_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64]
    _LIB.copy_gpu_buffer.restype = None

    _LIB.run_aot_graph.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(DynamicArg), ctypes.c_int]
    _LIB.run_aot_graph.restype = None

    _LIB.sync_runtime.argtypes = [ctypes.c_void_p]
    _LIB.sync_runtime.restype = None

    _LIB.clear_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _LIB.clear_pipeline.restype = None

    _LIB.add_to_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(DynamicArg), ctypes.c_int]
    _LIB.add_to_pipeline.restype = None

    _LIB.run_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(DynamicArg), ctypes.c_int]
    _LIB.run_pipeline.restype = None

    _LIB.ti_imread_to_gpu.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    _LIB.ti_imread_to_gpu.restype = ctypes.c_void_p

    _LIB.ti_imwrite_from_gpu.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    _LIB.ti_imwrite_from_gpu.restype = ctypes.c_bool

    _LIB.ti_cast_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    _LIB.ti_cast_buffer.restype = ctypes.c_bool

    # Initialization
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()
    arch_id = {"vulkan": 0, "cuda": 1, "cpu": 2}.get(arch_str, 0)
    device_id = int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", "0"))
    
    _RUNTIME = _LIB.init_aot_engine(arch_id, device_id)
    if not _RUNTIME:
        raise RuntimeError(f"Failed to initialize {arch_str.upper()} AOT Runtime.")
    AOTEngine._active_arch = arch_str

# -------------------------------------------------------------------------
# GPU Buffer Manager
# -------------------------------------------------------------------------
class BufferPool:
    def __init__(self):
        self.free_buffers = {} # size -> list of handles
    def acquire(self, size):
        if size in self.free_buffers and self.free_buffers[size]: return self.free_buffers[size].pop()
        return None
    def release(self, size, handle):
        if size not in self.free_buffers: self.free_buffers[size] = []
        self.free_buffers[size].append(handle)
    def clear(self):
        global _LIB, _RUNTIME
        if _LIB and _RUNTIME:
            for size, handles in self.free_buffers.items():
                for h in handles: _LIB.free_gpu_buffer(_RUNTIME, h)
        self.free_buffers = {}

class TaichiGPUBuffer:
    def __init__(self, size_bytes, handle, shape, dtype=np.float32, is_vector=False, engine=None, is_owner=True, host_accessible=False):
        self.size_bytes = size_bytes
        self.handle = handle
        self.shape = shape
        self.dtype = dtype
        self.is_vector = is_vector
        self.is_vec2 = is_vector
        self.engine = engine
        self.is_owner = is_owner
        self.host_accessible = host_accessible

    def __del__(self):
        if self.handle is not None and self.is_owner:
            if self.engine: self.engine.buffer_pool.release(self.size_bytes, self.handle)
            elif _LIB: _LIB.free_gpu_buffer(_RUNTIME, self.handle)
            self.handle = None

    @property
    def nbytes(self): return self.size_bytes

    def to_numpy(self):
        """Read GPU data. Automatically handles staging for VRAM-only buffers."""
        out = np.zeros(self.shape, dtype=self.dtype)
        if self.host_accessible:
            _LIB.read_from_gpu_buffer(_RUNTIME, self.handle, out.ctypes.data, self.size_bytes)
        elif self.engine:
            staging = self.engine.get_staging_buffer(self.shape, self.dtype)
            _LIB.copy_gpu_buffer(_RUNTIME, self.handle, staging.handle, self.size_bytes)
            _LIB.read_from_gpu_buffer(_RUNTIME, staging.handle, out.ctypes.data, self.size_bytes)
        else:
            raise RuntimeError("VRAM-only read requires engine for staging.")
        return out

    def map(self): return _LIB.map_gpu_buffer(_RUNTIME, self.handle)
    def unmap(self): _LIB.unmap_gpu_buffer(_RUNTIME, self.handle)
    
    def cast(self, target_dtype):
        target_dtype = np.dtype(target_dtype).type
        if self.dtype == target_dtype: return self
        dtype_map = {np.float32: 0, np.int32: 1, np.uint8: 2, np.uint16: 3}
        if self.dtype not in dtype_map or target_dtype not in dtype_map:
            return self.engine.upload(self.to_numpy().astype(target_dtype))
        dst = self.engine.allocate(self.shape, dtype=target_dtype)
        num_elements = np.prod(self.shape)
        _LIB.ti_cast_buffer(_RUNTIME, self.handle, dst.handle, int(num_elements), dtype_map[self.dtype], dtype_map[target_dtype])
        return dst

    def view_as_vector(self, is_vector=True):
        return TaichiGPUBuffer(self.size_bytes, self.handle, self.shape, self.dtype, is_vector, self.engine, False, self.host_accessible)

class TaichiPlaceholder(TaichiGPUBuffer):
    def __init__(self, placeholder_id, shape, dtype, is_vector=False):
        super().__init__(0, placeholder_id, shape, dtype, is_vector, None, False, False)

# -------------------------------------------------------------------------
# AOT Engine and Wrappers
# -------------------------------------------------------------------------
class AOTModuleWrapper:
    def __init__(self, module_ptr): self.module_ptr = module_ptr
    def __del__(self):
        if self.module_ptr: _LIB.destroy_aot_module(self.module_ptr)
    def run(self, graph_name, **kwargs):
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        for i, (k, v) in enumerate(kwargs.items()): _populate_dynamic_arg(args_array[i], k, v)
        engine = AOTEngine()
        if engine.current_pipeline:
            _LIB.add_to_pipeline(self.module_ptr, engine.current_pipeline.encode('utf-8'), graph_name.encode('utf-8'), args_array, num_args)
        else:
            _LIB.run_aot_graph(_RUNTIME, self.module_ptr, graph_name.encode('utf-8'), args_array, num_args)

class AOTEngine:
    _instance = None
    _active_arch = "vulkan"
    _placeholder_id_counter = -1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AOTEngine, cls).__new__(cls)
            _init_aot_bridge()
            cls._instance.modules = {}
            cls._instance.buffer_pool = BufferPool()
            cls._instance.current_pipeline = None
            cls._instance._staging_pool = {}
        return cls._instance

    def placeholder(self, shape, dtype=np.float32, is_vector=False):
        p = TaichiPlaceholder(self._placeholder_id_counter, shape, dtype, is_vector)
        self._placeholder_id_counter -= 1
        return p

    def rec_pipeline(self, name):
        class Recorder:
            def __init__(self, engine, name): self.engine, self.name = engine, name
            def __enter__(self):
                module = next(iter(self.engine.modules.values())) if self.engine.modules else None
                _LIB.clear_pipeline(module.module_ptr if module else None, self.name.encode('utf-8'))
                self.engine.current_pipeline = self.name
                return self
            def __exit__(self, *args): self.engine.current_pipeline = None
        return Recorder(self, name)

    def use_pipeline(self, name, overrides=None):
        _init_aot_bridge()
        ovr = overrides or {}
        n = len(ovr)
        handles = (ctypes.c_uint64 * n)()
        args = (DynamicArg * n)()
        for i, (p, b) in enumerate(ovr.items()):
            handles[i] = ctypes.c_uint64(p.handle)
            _populate_dynamic_arg(args[i], "override", b)
        _LIB.run_pipeline(_RUNTIME, name.encode('utf-8'), handles, args, n)

    def allocate(self, shape, dtype=np.float32, is_vector=False, host_accessible=False):
        size = int(np.prod(shape) * np.dtype(dtype).itemsize)
        handle = self.buffer_pool.acquire(size) if not host_accessible else None
        if not handle: handle = _LIB.allocate_gpu_buffer(_RUNTIME, size, 1 if host_accessible else 0)
        return TaichiGPUBuffer(size, handle, shape, dtype, is_vector, self, host_accessible=host_accessible)

    def get_staging_buffer(self, shape, dtype):
        size = int(np.prod(shape) * np.dtype(dtype).itemsize)
        key = (size, np.dtype(dtype).name)
        if key not in self._staging_pool: self._staging_pool[key] = self.allocate(shape, dtype, host_accessible=True)
        return self._staging_pool[key]

    def _is_external_gpu_obj(self, data):
        if hasattr(data, "is_cuda") and data.is_cuda: return "pytorch"
        if type(data).__name__ == "UMat": return "opencv"
        if type(data).__name__ == "OrtValue": return "onnx"
        if hasattr(data, "__cuda_array_interface__"): return "cuda"
        return None

    def _upload_fast_interop(self, data) -> TaichiGPUBuffer:
        """Universal Fast-Copy bridge using Pinned Memory DMA."""
        obj_type = self._is_external_gpu_obj(data)
        shape = getattr(data, "shape", (1,))
        dtype = np.float32 
        
        if obj_type == "pytorch":
            import torch
            dtype_map = {torch.float32: np.float32, torch.uint8: np.uint8, torch.int32: np.int32}
            dtype = dtype_map.get(data.dtype, np.float32)
        elif hasattr(data, "dtype"):
            dtype = data.dtype

        staging = self.get_staging_buffer(shape, dtype)
        ptr = staging.map()
        
        if obj_type == "pytorch":
            import torch
            target_view = torch.from_blob(ptr, shape, dtype=data.dtype, device='cpu')
            target_view.copy_(data.detach(), non_blocking=False) 
        elif hasattr(data, "__cuda_array_interface__"):
            src_ptr = data.__cuda_array_interface__['data'][0]
            ctypes.memmove(ptr, src_ptr, staging.nbytes)
        else:
            temp = np.ascontiguousarray(data)
            ctypes.memmove(ptr, temp.ctypes.data, temp.nbytes)
            
        staging.unmap()
        vram_target = self.allocate(shape, dtype)
        _LIB.copy_gpu_buffer(_RUNTIME, staging.handle, vram_target.handle, staging.nbytes)
        return vram_target

    def upload(self, data, is_vector=False):
        _init_aot_bridge()
        ext_type = self._is_external_gpu_obj(data)
        if ext_type:
            return self._upload_fast_interop(data)
        
        arr = np.ascontiguousarray(data)
        buf = self.allocate(arr.shape, arr.dtype, is_vector=is_vector, host_accessible=True)
        _LIB.write_to_gpu_buffer(_RUNTIME, buf.handle, arr.ctypes.data, buf.nbytes)
        return buf

    def load(self, path):
        base, ext = os.path.splitext(path)
        p = f"{base}_{self._active_arch}{ext}" if os.path.exists(f"{base}_{self._active_arch}{ext}") else path
        if p in self.modules: return self.modules[p]
        ptr = _LIB.load_aot_module(_RUNTIME, p.encode('utf-8'))
        if not ptr: raise RuntimeError(f"Failed to load TCM: {p}")
        self.modules[p] = AOTModuleWrapper(ptr)
        return self.modules[p]

    def imread(self, path):
        _init_aot_bridge()
        w, h, c, d = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        handle = _LIB.ti_imread_to_gpu(_RUNTIME, path.encode('utf-8'), ctypes.byref(w), ctypes.byref(h), ctypes.byref(c), ctypes.byref(d))
        if not handle: raise RuntimeError(f"Failed to load image: {path}")
        dtype = np.uint8 if d.value == 8 else np.uint16
        shape = (h.value, w.value) if c.value == 1 else (h.value, w.value, c.value)
        return TaichiGPUBuffer(w.value*h.value*c.value*(d.value//8), handle, shape, dtype, engine=self, host_accessible=False)

    def imwrite(self, path, buf):
        _init_aot_bridge()
        h, w = buf.shape[0], buf.shape[1]
        c = 1 if len(buf.shape) == 2 else buf.shape[2]
        d = 8 if buf.dtype == np.uint8 else 16
        if not _LIB.ti_imwrite_from_gpu(_RUNTIME, path.encode('utf-8'), buf.handle, w, h, c, d):
            raise RuntimeError(f"Failed to save image: {path}")

    def sync(self): _LIB.sync_runtime(_RUNTIME)
    def reinit(self, device_id=0):
        global _RUNTIME
        _RUNTIME = _LIB.init_aot_engine({"vulkan":0,"cuda":1,"cpu":2}.get(self._active_arch, 0), device_id)
        self.modules = {}

engine = AOTEngine()
