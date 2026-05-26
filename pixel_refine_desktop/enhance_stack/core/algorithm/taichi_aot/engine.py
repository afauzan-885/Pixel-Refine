import ctypes
import os
import sys
import numpy as np

# -------------------------------------------------------------------------
# OpenCV-style Constants for Standardization
# -------------------------------------------------------------------------
INTER_NEAREST = 0
INTER_LINEAR  = 1
INTER_CUBIC   = 2
INTER_AREA    = 3

COLOR_BGR2GRAY = 6
COLOR_RGB2GRAY = 7
COLOR_GRAY2BGR = 8

# -------------------------------------------------------------------------
# Dynamic Argument Structure for C++ Engine
# -------------------------------------------------------------------------
class DynamicArg(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("arg_type", ctypes.c_int), # 0: ndarray, 1: scalar
        ("dtype", ctypes.c_int),    # 0: f32, 1: i32, 2: u8, 3: u16
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_int * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_int * 8),
        ("is_vector", ctypes.c_int),
        ("vector_dim", ctypes.c_int),
        ("val_u64", ctypes.c_uint64)
    ]

dtype_map = {
    np.float32: 0,
    np.int32: 1,
    np.uint8: 2,
    np.uint16: 3,
    np.float64: 0, # Fallback
}

# -------------------------------------------------------------------------
# Dynamic Argument Population Helper
# -------------------------------------------------------------------------
def _populate_dynamic_arg(arg: DynamicArg, name_bytes, value, context_name="Unknown"):
    """Internal helper to fill DynamicArg metadata consistently."""
    arg.name = name_bytes
    
    if isinstance(value, (int, np.integer)):
        arg.arg_type = 1
        arg.dtype = 1 # i32
        arg.val_u64 = int(value)
    elif isinstance(value, (float, np.floating)):
        arg.arg_type = 1
        arg.dtype = 0 # f32
        arg.val_u64 = ctypes.cast(ctypes.pointer(ctypes.c_float(float(value))), ctypes.POINTER(ctypes.c_uint64)).contents.value
    elif isinstance(value, (TaichiGPUBuffer, TaichiPlaceholder)):
        arg.arg_type = 0
        
        # Strict Metadata Alignment for AOT
        is_vec = getattr(value, "is_vector", False)
        v_dim = getattr(value, "vector_dim", 1)
        
        val_dtype = value.dtype if hasattr(value, 'dtype') else np.float32
        if hasattr(val_dtype, 'type'):
            val_dtype = val_dtype.type
        arg.dtype = dtype_map.get(val_dtype, 0)
        arg.is_vector = 1 if is_vec else 0
        arg.vector_dim = v_dim

        shape = value.shape
        dim_count = len(shape)
        
        if is_vec:
            # Vector field: Distinguish between spatial and vector components
            if dim_count >= 2 and shape[-1] == v_dim:
                # Shape explicitly includes vector dim (e.g. H, W, 3) -> Strip it for Taichi
                arg.dim_count = dim_count - 1
                for d in range(dim_count - 1): arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
            else:
                # Shape is implicitly a grid of vectors (e.g. gn, gm, gl containing vec2)
                arg.dim_count = dim_count
                for d in range(dim_count): arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
        else:
            # Scalar field
            arg.dim_count = dim_count
            for d in range(dim_count): arg.shape[d] = shape[d]
            arg.elem_dim_count = 0
            
        arg.val_u64 = ctypes.c_uint64(value.handle)
    else:
        # Backward compatibility for direct Taichi NDArrays (if any)
        if hasattr(value, "ptr"):
            arg.arg_type = 0
            arg.val_u64 = value.ptr
            arg.dtype = 0 # Assume f32
            arg.dim_count = len(value.shape)
            for d, s in enumerate(value.shape): arg.shape[d] = s
            arg.elem_dim_count = 0
        else:
            name_str = name_bytes.decode('utf-8') if isinstance(name_bytes, bytes) else str(name_bytes)
            raise TypeError(
                f"\n[AOTEngine Error] {context_name}: Unsupported object type for argument '{name_str}'.\n"
                f"  EXPECTED: TaichiGPUBuffer, TaichiPlaceholder, int, or float.\n"
                f"  ACTUAL  : {type(value)}\n"
                f"  HINT    : If using NumPy, ensure you upload it via 'InputArray(data)' first."
            )

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
            ti_root = os.path.dirname(ti.__file__)
            ti_bin = os.path.join(ti_root, "_lib", "c_api", "bin")
            if os.path.exists(ti_bin): os.add_dll_directory(ti_bin)
            
            # CRITICAL: Set TI_LIB_DIR for the C++ Engine to find SPIR-V/CUDA runtimes
            ti_runtime = os.path.join(ti_root, "_lib", "runtime")
            if os.path.exists(ti_runtime):
                os.environ["TI_LIB_DIR"] = ti_runtime
        except: pass

    try:
        _LIB = ctypes.CDLL(engine_dll_path)
        print(f"[AOTEngine] Successfully loaded backend bridge: {os.path.basename(engine_dll_path)}")
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
    arch_str = "vulkan"
    arch_id = 0
    device_id = int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", "0"))
    
    _RUNTIME = _LIB.init_aot_engine(arch_id, device_id)
    if not _RUNTIME:
        raise RuntimeError(f"Failed to initialize {arch_str.upper()} AOT Runtime.")
    print(f"[AOTEngine] Runtime initialized on '{arch_str.upper()}' (Device {device_id})")
    AOTEngine._active_arch = arch_str

# -------------------------------------------------------------------------
# GPU Buffer Manager
# -------------------------------------------------------------------------
class BufferPool:
    """Lightweight pool: tracks handles for potential reuse by exact size match."""
    def __init__(self):
        self.free_buffers = {}  # size -> list of handles
        import threading
        self._lock = threading.Lock()

    def acquire(self, size):
        with self._lock:
            if size in self.free_buffers and self.free_buffers[size]:
                return self.free_buffers[size].pop()
            return None

    def store(self, size, handle):
        """Store a handle for reuse (caller decides if reuse or free)."""
        with self._lock:
            if size not in self.free_buffers:
                self.free_buffers[size] = []
            self.free_buffers[size].append(handle)

    def clear(self):
        """Force-free all pooled handles from VRAM."""
        global _LIB, _RUNTIME
        with self._lock:
            if _LIB and _RUNTIME:
                for handles in self.free_buffers.values():
                    for h in handles:
                        _LIB.free_gpu_buffer(_RUNTIME, h)
            self.free_buffers = {}

class TaichiGPUBuffer:
    def __init__(self, size_bytes, handle, shape, dtype=np.float32, is_vector=False, engine=None, is_owner=True, host_accessible=False, vector_dim=3):
        self.size_bytes = size_bytes
        self.handle = handle
        self.shape = shape
        self.dtype = dtype
        self.is_vector = is_vector
        self.vector_dim = vector_dim
        self.engine = engine
        self.is_owner = is_owner
        self.host_accessible = host_accessible

    def destroy(self):
        """Immediately release GPU VRAM. Does NOT use buffer pool reuse."""
        if self.handle is not None and self.is_owner:
            global _LIB, _RUNTIME
            if _LIB and _RUNTIME:
                if self.engine and hasattr(self.engine, "_lock"):
                    with self.engine._lock:
                        _LIB.free_gpu_buffer(_RUNTIME, self.handle)
                else:
                    _LIB.free_gpu_buffer(_RUNTIME, self.handle)
            self.handle = None
            self.is_owner = False

    def __del__(self):
        self.destroy()

    @property
    def nbytes(self): return self.size_bytes

    def to_numpy(self):
        """Read GPU data. Automatically handles staging for VRAM-only buffers."""
        out = np.zeros(self.shape, dtype=self.dtype)
        if self.host_accessible:
            if self.engine and hasattr(self.engine, "_lock"):
                with self.engine._lock:
                    _LIB.read_from_gpu_buffer(_RUNTIME, self.handle, out.ctypes.data, self.size_bytes)
            else:
                _LIB.read_from_gpu_buffer(_RUNTIME, self.handle, out.ctypes.data, self.size_bytes)
        elif self.engine:
            with self.engine._lock:
                staging = self.engine.get_staging_buffer(self.shape, self.dtype)
                _LIB.copy_gpu_buffer(_RUNTIME, self.handle, staging.handle, self.size_bytes)
                _LIB.read_from_gpu_buffer(_RUNTIME, staging.handle, out.ctypes.data, self.size_bytes)
        else:
            raise RuntimeError("VRAM-only read requires engine for staging.")
        return out

    def map(self):
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                return _LIB.map_gpu_buffer(_RUNTIME, self.handle)
        return _LIB.map_gpu_buffer(_RUNTIME, self.handle)

    def unmap(self):
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                _LIB.unmap_gpu_buffer(_RUNTIME, self.handle)
        else:
            _LIB.unmap_gpu_buffer(_RUNTIME, self.handle)
    
    def cast(self, target_dtype, host_accessible=False):
        target_dtype = np.dtype(target_dtype).type
        if self.dtype == target_dtype: return self
        dtype_map = {np.float32: 0, np.int32: 1, np.uint8: 2, np.uint16: 3}
        if self.dtype not in dtype_map or target_dtype not in dtype_map:
            return self.engine.upload(self.to_numpy().astype(target_dtype))
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                dst = self.engine.allocate(self.shape, dtype=target_dtype, host_accessible=host_accessible)
                num_elements = np.prod(self.shape)
                _LIB.ti_cast_buffer(_RUNTIME, self.handle, dst.handle, int(num_elements), dtype_map[self.dtype], dtype_map[target_dtype])
                return dst
        else:
            dst = self.engine.allocate(self.shape, dtype=target_dtype, host_accessible=host_accessible)
            num_elements = np.prod(self.shape)
            _LIB.ti_cast_buffer(_RUNTIME, self.handle, dst.handle, int(num_elements), dtype_map[self.dtype], dtype_map[target_dtype])
            return dst

    def view_as_vector(self, is_vector=True, vector_dim=3):
        return TaichiGPUBuffer(self.size_bytes, self.handle, self.shape, self.dtype, is_vector, self.engine, False, self.host_accessible, vector_dim)

class TaichiPlaceholder(TaichiGPUBuffer):
    def __init__(self, placeholder_id, shape, dtype, is_vector=False, vector_dim=3):
        super().__init__(0, placeholder_id, shape, dtype, is_vector, None, False, False, vector_dim)

# -------------------------------------------------------------------------
# AOT Engine and Wrappers
# -------------------------------------------------------------------------
class AOTModuleWrapper:
    def __init__(self, module_ptr): self.module_ptr = module_ptr
    def __del__(self):
        if self.module_ptr: _LIB.destroy_aot_module(self.module_ptr)
    def run(self, graph_name, **kwargs):
        """Menjalankan grafik Taichi AOT dengan validasi argumen yang informatif."""
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        # CRITICAL: Keep names alive during the C++ call to prevent dangling pointers
        arg_names = [k.encode('utf-8') for k in kwargs.keys()]
        
        for i, (k, v) in enumerate(kwargs.items()): 
            try:
                _populate_dynamic_arg(args_array[i], arg_names[i], v, context_name=graph_name)
            except Exception as e:
                # Wrap error with clearer context
                raise ValueError(f"Failed to prepare argument '{k}' for kernel '{graph_name}':\n{str(e)}")
            
        engine = AOTEngine()
        with engine._lock:
            if engine.current_pipeline:
                _LIB.add_to_pipeline(self.module_ptr, engine.current_pipeline.encode('utf-8'), graph_name.encode('utf-8'), args_array, num_args)
            else:
                try:
                    _LIB.run_aot_graph(_RUNTIME, self.module_ptr, graph_name.encode('utf-8'), args_array, num_args)
                except Exception as e:
                    raise RuntimeError(
                        f"\n[AOTEngine Execution Error] Kernel '{graph_name}' gagal dijalankan!\n"
                        f"  ERROR: {str(e)}\n"
                        f"  HINT : Periksa apakah ukuran (shape) dan tipe data input sudah sesuai dengan definisi kernel di C++."
                    )

    def _dummy_run(self): pass # For keeping refs if needed

class AOTEngine:
    _instance = None
    _active_arch = "vulkan"
    _placeholder_id_counter = 0xFFFFFF00

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AOTEngine, cls).__new__(cls)
            _init_aot_bridge()
            cls._instance.modules = {}
            cls._instance.buffer_pool = BufferPool()
            cls._instance.current_pipeline = None
            cls._instance._staging_pool = {}
            import threading
            cls._instance._lock = threading.RLock()
        return cls._instance

    def placeholder(self, shape, dtype=np.float32, is_vector=False, vector_dim=3):
        p = TaichiPlaceholder(self._placeholder_id_counter, shape, dtype, is_vector, vector_dim)
        self._placeholder_id_counter += 1
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
        # Keep names alive
        arg_names = [b"override"] * n
        for i, (p, b) in enumerate(ovr.items()):
            handles[i] = ctypes.c_uint64(p.handle)
            _populate_dynamic_arg(args[i], arg_names[i], b)
        with self._lock:
            _LIB.run_pipeline(_RUNTIME, name.encode('utf-8'), handles, args, n)

    def allocate(self, shape, dtype=np.float32, is_vector=False, host_accessible=False, vector_dim=None):
        with self._lock:
            size = int(np.prod(shape) * np.dtype(dtype).itemsize)
            v_dim = vector_dim if vector_dim is not None else (shape[-1] if is_vector and len(shape) >= 2 else 1)
            handle = self.buffer_pool.acquire(size) if not host_accessible else None
            if not handle: 
                handle = _LIB.allocate_gpu_buffer(_RUNTIME, size, 1 if host_accessible else 0)
            
            if handle is None or handle == 0:
                arch = getattr(self, "_active_arch", "unknown")
                raise RuntimeError(
                    f"\n[AOTEngine Memory Error] Failed to allocate {size/1024/1024:.2f} MB on GPU ({arch}).\n"
                    f"  HINT: VRAM might be exhausted. Try calling 'engine.buffer_pool.clear()' or 'gc.collect()' to free idle buffers."
                )
            
            # print(f"[AOTEngine] New VRAM allocation: {size/1024/1024:.2f} MB ({dtype})")
            return TaichiGPUBuffer(size, handle, shape, dtype, is_vector, self, host_accessible=host_accessible, vector_dim=v_dim)

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

    def _upload_fast_interop(self, data, is_vector=False, vector_dim=3) -> TaichiGPUBuffer:
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

        with self._lock:
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
            vram_target = self.allocate(shape, dtype, is_vector=is_vector, vector_dim=vector_dim)
            _LIB.copy_gpu_buffer(_RUNTIME, staging.handle, vram_target.handle, staging.nbytes)
        return vram_target

    def upload(self, data, is_vector=False, vector_dim=3):
        _init_aot_bridge()

        # Short-circuit: if already a TaichiGPUBuffer, return as-is (zero-copy passthrough)
        if isinstance(data, TaichiGPUBuffer):
            return data

        ext_type = self._is_external_gpu_obj(data)
        
        # Auto-detect Vector Fields (RGB=3, Flow=2)
        if not is_vector and hasattr(data, "shape"):
            if len(data.shape) == 3:
                if data.shape[2] == 3:
                    is_vector = True
                    vector_dim = 3
                elif data.shape[2] == 2:
                    is_vector = True
                    vector_dim = 2

        if ext_type:
            return self._upload_fast_interop(data, is_vector=is_vector, vector_dim=vector_dim)
        
        arr = np.ascontiguousarray(data)
        buf = self.allocate(arr.shape, arr.dtype, is_vector=is_vector, host_accessible=True, vector_dim=vector_dim)
        _LIB.write_to_gpu_buffer(_RUNTIME, buf.handle, arr.ctypes.data, buf.nbytes)
        return buf


    def load(self, path):
        with self._lock:
            base, ext = os.path.splitext(path)
            p = f"{base}_{self._active_arch}{ext}" if os.path.exists(f"{base}_{self._active_arch}{ext}") else path
            if p in self.modules: return self.modules[p]
            ptr = _LIB.load_aot_module(_RUNTIME, p.encode('utf-8'))
            if not ptr: 
                raise RuntimeError(
                    f"\n[AOTEngine Load Error] Failed to load TCM module at: {p}\n"
                    f"  HINT: Ensure the .tcm file exists and is compatible with the active GPU backend ({self._active_arch})."
                )
            print(f"[AOTEngine] Loaded TCM module: {os.path.basename(p)}")
            self.modules[p] = AOTModuleWrapper(ptr)
            return self.modules[p]

    def imread(self, path):
        _init_aot_bridge()
        w, h, c, d = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        with self._lock:
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
        with self._lock:
            res = _LIB.ti_imwrite_from_gpu(_RUNTIME, path.encode('utf-8'), buf.handle, w, h, c, d)
        if not res:
            raise RuntimeError(f"Failed to save image: {path}")

    def sync(self):
        with self._lock:
            _LIB.sync_runtime(_RUNTIME)
    def reinit(self, device_id=0):
        with self._lock:
            global _RUNTIME
            _RUNTIME = _LIB.init_aot_engine({"vulkan":0,"cuda":1,"cpu":2}.get(self._active_arch, 0), device_id)
            self.modules = {}

engine = AOTEngine()

# -------------------------------------------------------------------------
# OpenCV-style Data Unification (InputArray / OutputArray)
# -------------------------------------------------------------------------
def InputArray(data, is_vector=False, vector_dim=None) -> TaichiGPUBuffer:
    """
    OpenCV-style Data Input Unification.
    Automatically handles NumPy arrays, PyTorch tensors, OpenCV UMats, 
    native Python lists, or existing TaichiGPUBuffer instances.
    """
    if isinstance(data, (TaichiGPUBuffer, TaichiPlaceholder)):
        return data
    
    # Auto-convert native Python structures
    if isinstance(data, (list, tuple, int, float)):
        data = np.array(data, dtype=np.float32)
        
    # Delegate to universal fast-interop bridge
    return engine.upload(data, is_vector=is_vector, vector_dim=vector_dim)

def OutputArray(shape, dtype=np.float32, is_vector=False, vector_dim=None) -> TaichiGPUBuffer:
    """
    OpenCV-style Data Output Allocation.
    Creates an empty GPU VRAM buffer ready for writing.
    """
    return engine.allocate(shape, dtype=dtype, is_vector=is_vector, vector_dim=vector_dim)
