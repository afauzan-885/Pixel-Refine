#include <cstring>
#include <iostream>
#include <string>
#include <taichi/cpp/taichi.hpp>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <mutex>
#include <immintrin.h>


#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#include <wincodec.h>
#include <windows.h>

#pragma comment(lib, "windowscodecs.lib")
#else
#define EXPORT
#endif

// Forward declaration for WIC factory (global for performance)
#ifdef _WIN32
static IWICImagingFactory *g_wic_factory = nullptr;
static void init_wic() {
  if (!g_wic_factory) {
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    CoCreateInstance(CLSID_WICImagingFactory, NULL, CLSCTX_INPROC_SERVER,
                     IID_PPV_ARGS(&g_wic_factory));
  }
}
#endif

extern "C" {

// -----------------------------------------------------------------------
// Dynamic Argument Structure
// -----------------------------------------------------------------------
struct DynamicArg {
  const char *name;
  int arg_type; // 0: ndarray, 1: scalar
  int dtype;    // 0: f32, 1: i32, 2: u8, 3: u16
  int dim_count;
  int32_t shape[8];
  int elem_dim_count;
  int32_t elem_shape[8];
  int is_vector;
  int vector_dim;
  uint64_t val_u64;
};

struct EngineContext;

// -----------------------------------------------------------------------
// Pipeline Structures (Global)
// -----------------------------------------------------------------------
struct GraphDispatch {
  void *module_ctx;
  std::string graph_name;
  std::vector<DynamicArg> args;
  std::vector<std::string> arg_names; // Storage for name pointers
};

struct Pipeline {
  std::vector<GraphDispatch> steps;
};

// Fallback store for legacy calls that do not provide an EngineContext.
static std::unordered_map<std::string, Pipeline> global_pipelines;
static std::mutex pipelines_mutex;

// -----------------------------------------------------------------------
// Internal Cache for Graphics Objects
// -----------------------------------------------------------------------
struct ModuleContext {
  EngineContext *owner;
  ti::AotModule *module;
  std::unordered_map<std::string, ti::ComputeGraph> graph_cache;
  std::mutex cache_mutex;
};

struct EngineContext {
  ti::Runtime *runtime;
  std::unordered_set<TiMemory> buffers;
  std::unordered_set<TiMemory> mapped_buffers;
  std::unordered_set<ModuleContext *> modules;
  std::unordered_map<std::string, Pipeline> pipelines;
  std::mutex mutex;
  std::string last_error;
  bool destroying;
  uint64_t session_id;
};

static std::unordered_set<EngineContext *> engine_contexts;
static std::mutex engine_contexts_mutex;
static uint64_t next_session_id = 1;

static EngineContext *as_engine(void *runtime) {
  return (EngineContext *)runtime;
}

static ti::Runtime *engine_runtime(EngineContext *ctx) {
  if (!ctx || ctx->destroying)
    return nullptr;
  return ctx->runtime;
}

static void set_engine_error(EngineContext *ctx, const std::string &message) {
  if (!ctx)
    return;
  std::lock_guard<std::mutex> lock(ctx->mutex);
  ctx->last_error = message;
}

static void clear_engine_error(EngineContext *ctx) {
  if (!ctx)
    return;
  std::lock_guard<std::mutex> lock(ctx->mutex);
  ctx->last_error.clear();
}

static std::string consume_ti_last_error() {
  std::string last_error;
  for (int attempt = 0; attempt < 16; ++attempt) {
    uint64_t msg_size = 0;
    ti_get_last_error(&msg_size, nullptr);
    if (msg_size <= 1)
      break;
    std::vector<char> msg(msg_size);
    ti_get_last_error(&msg_size, msg.data());
    if (!msg.empty() && msg[0] != '\0')
      last_error = std::string(msg.data());
  }
  return last_error;
}

// -----------------------------------------------------------------------
// Runtime & Module Management
// -----------------------------------------------------------------------
EXPORT const char *scan_vulkan_devices() {
  static std::string device_list;
  device_list = "";
#ifdef _WIN32
  FILE *pipe = _popen("vulkaninfo --summary", "r");
#else
  FILE *pipe = popen("vulkaninfo --summary", "r");
#endif
  if (!pipe)
    return "";
  char buffer[256];
  while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
    std::string line(buffer);
    if (line.find("deviceName") != std::string::npos) {
      size_t pos = line.find("=");
      if (pos != std::string::npos) {
        std::string name = line.substr(pos + 1);
        // Trim whitespace and newlines
        name.erase(0, name.find_first_not_of(" \t"));
        name.erase(name.find_last_not_of(" \t\n\r") + 1);
        if (!device_list.empty())
          device_list += ";";
        device_list += name;
      }
    }
  }
#ifdef _WIN32
  _pclose(pipe);
#else
  pclose(pipe);
#endif
  return device_list.c_str();
}

EXPORT void *init_aot_engine(int arch_id, int device_id) {
  try {
    TiArch arch = TI_ARCH_VULKAN;
    if (arch_id == 1)
      arch = TI_ARCH_CUDA;
    else if (arch_id == 2)
      arch = TI_ARCH_X64;

    // Use specified device_id
    EngineContext *ctx = new EngineContext();
    ctx->runtime = new ti::Runtime(arch, (uint32_t)device_id);
    ctx->destroying = false;
    ctx->session_id = next_session_id++;
    {
      std::lock_guard<std::mutex> lock(engine_contexts_mutex);
      engine_contexts.insert(ctx);
    }
    return (void *)ctx;
  } catch (...) {
    // Fallback to CPU if GPU initialization fails
    try {
      EngineContext *ctx = new EngineContext();
      ctx->runtime = new ti::Runtime(TI_ARCH_X64, 0);
      ctx->destroying = false;
      ctx->session_id = next_session_id++;
      {
        std::lock_guard<std::mutex> lock(engine_contexts_mutex);
        engine_contexts.insert(ctx);
      }
      return (void *)ctx;
    } catch (...) {
      return nullptr;
    }
  }
}

EXPORT const char *get_last_engine_error(void *runtime) {
  EngineContext *ctx = as_engine(runtime);
  if (!ctx)
    return "";
  std::lock_guard<std::mutex> lock(ctx->mutex);
  return ctx->last_error.c_str();
}

EXPORT void clear_last_engine_error(void *runtime) {
  clear_engine_error(as_engine(runtime));
  consume_ti_last_error();
}

EXPORT void *load_aot_module(void *runtime, const char *tcm_path) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt)
    return nullptr;
  try {
    clear_engine_error(engine);
    consume_ti_last_error();
    ModuleContext *ctx = new ModuleContext();
    ctx->owner = engine;
    ctx->module = new ti::AotModule(rt->load_aot_module(tcm_path));
    std::string load_error = consume_ti_last_error();
    if (!load_error.empty()) {
      if (ctx->module)
        delete ctx->module;
      delete ctx;
      set_engine_error(engine, std::string("load_aot_module: ") + load_error);
      return nullptr;
    }
    {
      std::lock_guard<std::mutex> lock(engine->mutex);
      engine->modules.insert(ctx);
    }
    return (void *)ctx;
  } catch (const std::exception &e) {
    set_engine_error(engine, std::string("load_aot_module: ") + e.what());
    return nullptr;
  } catch (...) {
    set_engine_error(engine, "load_aot_module: unknown exception");
    return nullptr;
  }
}

EXPORT void destroy_aot_module(void *module_ctx) {
  ModuleContext *ctx = (ModuleContext *)module_ctx;
  if (ctx) {
    EngineContext *owner = ctx->owner;
    if (owner) {
      std::lock_guard<std::mutex> lock(owner->mutex);
      owner->modules.erase(ctx);
    }
    if (ctx->module)
      delete ctx->module;
    delete ctx;
  }
}

EXPORT void destroy_aot_engine(void *runtime) {
  EngineContext *ctx = as_engine(runtime);
  if (!ctx)
    return;

  {
    std::lock_guard<std::mutex> lock(engine_contexts_mutex);
    if (engine_contexts.find(ctx) == engine_contexts.end())
      return;
    engine_contexts.erase(ctx);
  }

  {
    std::lock_guard<std::mutex> lock(ctx->mutex);
    ctx->destroying = true;
  }

  try {
    if (ctx->runtime)
      ctx->runtime->wait();
  } catch (...) {
  }

  std::vector<ModuleContext *> modules;
  std::vector<TiMemory> buffers;
  {
    std::lock_guard<std::mutex> lock(ctx->mutex);
    for (auto *mod : ctx->modules)
      modules.push_back(mod);
    for (auto mem : ctx->buffers)
      buffers.push_back(mem);
    ctx->modules.clear();
    ctx->buffers.clear();
    ctx->mapped_buffers.clear();
    ctx->pipelines.clear();
  }

  for (auto *mod : modules) {
    try {
      if (mod && mod->module)
        delete mod->module;
      delete mod;
    } catch (...) {
    }
  }

  for (auto mem : buffers) {
    try {
      if (ctx->runtime && mem)
        ti_free_memory(ctx->runtime->runtime(), mem);
    } catch (...) {
    }
  }

  try {
    if (ctx->runtime)
      delete ctx->runtime;
  } catch (...) {
  }
  ctx->runtime = nullptr;
  delete ctx;
}

// -----------------------------------------------------------------------
// Memory Management
// -----------------------------------------------------------------------
EXPORT void *allocate_gpu_buffer(void *runtime, uint64_t size,
                                 int host_accessible) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt)
    return nullptr;
  TiMemoryAllocateInfo allocate_info = {};
  allocate_info.size = size;
  allocate_info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
  if (host_accessible) {
    allocate_info.host_write = true;
    allocate_info.host_read = true;
  }
  TiMemory mem = ti_allocate_memory(rt->runtime(), &allocate_info);
  if (mem) {
    std::lock_guard<std::mutex> lock(engine->mutex);
    engine->buffers.insert(mem);
  }
  return (void *)mem;
}

EXPORT void free_gpu_buffer(void *runtime, void *memory) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (rt && memory) {
    {
      std::lock_guard<std::mutex> lock(engine->mutex);
      engine->mapped_buffers.erase((TiMemory)memory);
      engine->buffers.erase((TiMemory)memory);
    }
    ti_free_memory(rt->runtime(), (TiMemory)memory);
  }
}

EXPORT void write_to_gpu_buffer(void *runtime, void *memory, void *data,
                                uint64_t size) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !memory || !data)
    return;
  void *ptr = ti_map_memory(rt->runtime(), (TiMemory)memory);
  if (ptr) {
    memcpy(ptr, data, size);
    ti_unmap_memory(rt->runtime(), (TiMemory)memory);
  }
}

EXPORT void read_from_gpu_buffer(void *runtime, void *memory, void *data,
                                 uint64_t size) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !memory || !data)
    return;
  rt->wait(); // Ensure all kernels are done before reading
  void *ptr = ti_map_memory(rt->runtime(), (TiMemory)memory);
  if (ptr) {
    memcpy(data, ptr, size);
    ti_unmap_memory(rt->runtime(), (TiMemory)memory);
  }
}

EXPORT void *map_gpu_buffer(void *runtime, void *memory) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !memory)
    return nullptr;
  void *ptr = ti_map_memory(rt->runtime(), (TiMemory)memory);
  if (ptr) {
    std::lock_guard<std::mutex> lock(engine->mutex);
    engine->mapped_buffers.insert((TiMemory)memory);
  }
  return ptr;
}

EXPORT void unmap_gpu_buffer(void *runtime, void *memory) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (rt && memory) {
    ti_unmap_memory(rt->runtime(), (TiMemory)memory);
    std::lock_guard<std::mutex> lock(engine->mutex);
    engine->mapped_buffers.erase((TiMemory)memory);
  }
}

EXPORT void copy_gpu_buffer(void *runtime, void *src, void *dst,
                            uint64_t size) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !src || !dst)
    return;

  TiMemorySlice src_slice = {};
  src_slice.memory = (TiMemory)src;
  src_slice.offset = 0;
  src_slice.size = size;

  TiMemorySlice dst_slice = {};
  dst_slice.memory = (TiMemory)dst;
  dst_slice.offset = 0;
  dst_slice.size = size;

  ti_copy_memory_device_to_device(rt->runtime(), &dst_slice, &src_slice);
  rt->wait(); // Synchronize to prevent race conditions
}

EXPORT void sync_runtime(void *runtime) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (rt)
    rt->wait();
}

// -----------------------------------------------------------------------
// High-Performance Image IO (Smart Loader)
// -----------------------------------------------------------------------
EXPORT void *ti_imread_to_gpu(void *runtime, const char *path, int *out_width,
                              int *out_height, int *out_channels,
                              int *out_bit_depth) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !path)
    return nullptr;

#ifdef _WIN32
  init_wic();
  if (!g_wic_factory)
    return nullptr;

  IWICBitmapDecoder *decoder = nullptr;
  wchar_t w_path[MAX_PATH];
  MultiByteToWideChar(CP_UTF8, 0, path, -1, w_path, MAX_PATH);

  if (FAILED(g_wic_factory->CreateDecoderFromFilename(
          w_path, NULL, GENERIC_READ, WICDecodeMetadataCacheOnDemand,
          &decoder))) {
    return nullptr;
  }

  IWICBitmapFrameDecode *frame = nullptr;
  decoder->GetFrame(0, &frame);

  UINT w, h;
  frame->GetSize(&w, &h);
  *out_width = (int)w;
  *out_height = (int)h;

  WICPixelFormatGUID pixel_format;
  frame->GetPixelFormat(&pixel_format);

  // Determine channels and bit depth
  int channels = 1;
  int bit_depth = 8;
  WICPixelFormatGUID target_format = GUID_WICPixelFormat8bppGray;

  if (pixel_format == GUID_WICPixelFormat8bppGray) {
    channels = 1;
    bit_depth = 8;
    target_format = GUID_WICPixelFormat8bppGray;
  } else if (pixel_format == GUID_WICPixelFormat16bppGray) {
    channels = 1;
    bit_depth = 16;
    target_format = GUID_WICPixelFormat16bppGray;
  } else if (pixel_format == GUID_WICPixelFormat24bppBGR ||
             pixel_format == GUID_WICPixelFormat32bppBGRA) {
    channels = 3;
    bit_depth = 8;
    target_format = GUID_WICPixelFormat24bppBGR;
  } else if (pixel_format == GUID_WICPixelFormat48bppBGR ||
             pixel_format == GUID_WICPixelFormat64bppBGRA) {
    channels = 3;
    bit_depth = 16;
    target_format = GUID_WICPixelFormat48bppBGR;
  } else {
    // Default fallback to 8-bit BGR
    channels = 3;
    bit_depth = 8;
    target_format = GUID_WICPixelFormat24bppBGR;
  }

  *out_channels = channels;
  *out_bit_depth = bit_depth;

  // Allocate GPU memory
  uint64_t size_bytes = (uint64_t)w * h * channels * (bit_depth / 8);
  TiMemoryAllocateInfo allocate_info = {};
  allocate_info.size = size_bytes;
  allocate_info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
  allocate_info.host_write = true; // Required for CopyPixels map path

  TiMemory gpu_mem = ti_allocate_memory(rt->runtime(), &allocate_info);
  if (!gpu_mem) {
    frame->Release();
    decoder->Release();
    return nullptr;
  }
  {
    std::lock_guard<std::mutex> lock(engine->mutex);
    engine->buffers.insert(gpu_mem);
  }

  // Copy pixels directly to GPU (using mapped memory if possible, or
  // intermediate buffer)
  void *gpu_ptr = ti_map_memory(rt->runtime(), gpu_mem);
  if (gpu_ptr) {
    if (pixel_format != target_format) {
      // Need conversion
      IWICFormatConverter *converter = nullptr;
      g_wic_factory->CreateFormatConverter(&converter);
      converter->Initialize(frame, target_format, WICBitmapDitherTypeNone, NULL,
                            0.0, WICBitmapPaletteTypeCustom);
      converter->CopyPixels(NULL, (UINT)(w * channels * (bit_depth / 8)),
                            (UINT)size_bytes, (BYTE *)gpu_ptr);
      converter->Release();
    } else {
      frame->CopyPixels(NULL, (UINT)(w * channels * (bit_depth / 8)),
                        (UINT)size_bytes, (BYTE *)gpu_ptr);
    }
    ti_unmap_memory(rt->runtime(), gpu_mem);
  }

  frame->Release();
  decoder->Release();
  return (void *)gpu_mem;

#else
  // TODO: Implement for Linux/Android using stb_image or similar
  return nullptr;
#endif
}

EXPORT bool ti_imwrite_from_gpu(void *runtime, const char *path, void *gpu_mem,
                                int width, int height, int channels,
                                int bit_depth) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt || !path || !gpu_mem)
    return false;

#ifdef _WIN32
  init_wic();
  if (!g_wic_factory)
    return false;

  IWICStream *stream = nullptr;
  g_wic_factory->CreateStream(&stream);

  wchar_t w_path[MAX_PATH];
  MultiByteToWideChar(CP_UTF8, 0, path, -1, w_path, MAX_PATH);

  if (FAILED(stream->InitializeFromFilename(w_path, GENERIC_WRITE))) {
    stream->Release();
    return false;
  }

  IWICBitmapEncoder *encoder = nullptr;
  // Auto-detect encoder based on extension
  GUID encoder_guid = GUID_ContainerFormatPng;
  std::string s_path = path;
  if (s_path.find(".jpg") != std::string::npos ||
      s_path.find(".jpeg") != std::string::npos) {
    encoder_guid = GUID_ContainerFormatJpeg;
  } else if (s_path.find(".tif") != std::string::npos) {
    encoder_guid = GUID_ContainerFormatTiff;
  }

  if (FAILED(g_wic_factory->CreateEncoder(encoder_guid, NULL, &encoder))) {
    stream->Release();
    return false;
  }

  encoder->Initialize(stream, WICBitmapEncoderNoCache);

  IWICBitmapFrameEncode *frame = nullptr;
  encoder->CreateNewFrame(&frame, NULL);
  frame->Initialize(NULL);
  frame->SetSize(width, height);

  WICPixelFormatGUID format_guid = GUID_WICPixelFormat8bppGray;
  if (bit_depth == 8) {
    format_guid = (channels == 1) ? GUID_WICPixelFormat8bppGray
                                  : GUID_WICPixelFormat24bppBGR;
  } else {
    format_guid = (channels == 1) ? GUID_WICPixelFormat16bppGray
                                  : GUID_WICPixelFormat48bppBGR;
  }

  frame->SetPixelFormat(&format_guid);

  void *gpu_ptr = ti_map_memory(rt->runtime(), (TiMemory)gpu_mem);
  if (gpu_ptr) {
    UINT stride = width * channels * (bit_depth / 8);
    UINT size = stride * height;
    frame->WritePixels(height, stride, size, (BYTE *)gpu_ptr);
    ti_unmap_memory(rt->runtime(), (TiMemory)gpu_mem);
  }

  frame->Commit();
  encoder->Commit();

  frame->Release();
  encoder->Release();
  stream->Release();
  return true;
#else
  return false;
#endif
}

EXPORT bool ti_cast_buffer(void *src_ptr, void *dst_ptr,
                           int num_elements, int src_type, int dst_type) {
  if (!src_ptr || !dst_ptr)
    return false;

  if (src_type == 0 && dst_type == 2) { // f32 -> u8
    float *s = (float *)src_ptr;
    uint8_t *d = (uint8_t *)dst_ptr;
    int i = 0;
    __m256 scale = _mm256_set1_ps(255.0f);
    __m256 half = _mm256_set1_ps(0.5f);
    for (; i <= num_elements - 8; i += 8) {
      __m256 f = _mm256_loadu_ps(s + i);
      f = _mm256_mul_ps(f, scale);
      f = _mm256_add_ps(f, half);
      __m256i i32 = _mm256_cvttps_epi32(f);
      __m128i lo = _mm256_castsi256_si128(i32);
      __m128i hi = _mm256_extracti128_si256(i32, 1);
      __m128i packed = _mm_packus_epi32(lo, hi);
      __m128i packed_bytes = _mm_packus_epi16(packed, _mm_setzero_si128());
      uint64_t val = _mm_cvtsi128_si64(packed_bytes);
      std::memcpy(d + i, &val, 8);
    }
    for (; i < num_elements; ++i)
      d[i] = (uint8_t)(s[i] * 255.0f + 0.5f);
  } else if (src_type == 2 && dst_type == 0) { // u8 -> f32
    uint8_t *s = (uint8_t *)src_ptr;
    float *d = (float *)dst_ptr;
    int i = 0;
    __m256 scale = _mm256_set1_ps(1.0f / 255.0f);
    for (; i <= num_elements - 8; i += 8) {
      uint64_t val;
      std::memcpy(&val, s + i, 8);
      __m128i u8_vec = _mm_cvtsi64_si128(val);
      __m256i i32 = _mm256_cvtepu8_epi32(u8_vec);
      __m256 f = _mm256_cvtepi32_ps(i32);
      f = _mm256_mul_ps(f, scale);
      _mm256_storeu_ps(d + i, f);
    }
    for (; i < num_elements; ++i)
      d[i] = (float)s[i] / 255.0f;
  } else if (src_type == 0 && dst_type == 3) { // f32 -> u16
    float *s = (float *)src_ptr;
    uint16_t *d = (uint16_t *)dst_ptr;
    int i = 0;
    __m256 scale = _mm256_set1_ps(65535.0f);
    __m256 half = _mm256_set1_ps(0.5f);
    for (; i <= num_elements - 8; i += 8) {
      __m256 f = _mm256_loadu_ps(s + i);
      f = _mm256_mul_ps(f, scale);
      f = _mm256_add_ps(f, half);
      __m256i i32 = _mm256_cvttps_epi32(f);
      __m128i lo = _mm256_castsi256_si128(i32);
      __m128i hi = _mm256_extracti128_si256(i32, 1);
      __m128i packed = _mm_packus_epi32(lo, hi);
      _mm_storeu_si128((__m128i*)(d + i), packed);
    }
    for (; i < num_elements; ++i)
      d[i] = (uint16_t)(s[i] * 65535.0f + 0.5f);
  } else if (src_type == 3 && dst_type == 0) { // u16 -> f32
    uint16_t *s = (uint16_t *)src_ptr;
    float *d = (float *)dst_ptr;
    int i = 0;
    __m256 scale = _mm256_set1_ps(1.0f / 65535.0f);
    for (; i <= num_elements - 8; i += 8) {
      __m128i u16_vec = _mm_loadu_si128((const __m128i*)(s + i));
      __m256i i32 = _mm256_cvtepu16_epi32(u16_vec);
      __m256 f = _mm256_cvtepi32_ps(i32);
      f = _mm256_mul_ps(f, scale);
      _mm256_storeu_ps(d + i, f);
    }
    for (; i < num_elements; ++i)
      d[i] = (float)s[i] / 65535.0f;
  } else if (src_type == 1 && dst_type == 3) { // i32 -> u16
    int32_t *s = (int32_t *)src_ptr;
    uint16_t *d = (uint16_t *)dst_ptr;
    for (int i = 0; i < num_elements; ++i)
      d[i] = (uint16_t)s[i];
  } else if (src_type == 1 && dst_type == 2) { // i32 -> u8
    int32_t *s = (int32_t *)src_ptr;
    uint8_t *d = (uint8_t *)dst_ptr;
    for (int i = 0; i < num_elements; ++i)
      d[i] = (uint8_t)s[i];
  }
  return true;
}

// -----------------------------------------------------------------------
// Internal Helper for Argument Mapping
// -----------------------------------------------------------------------
static void _fill_ti_arg(TiNamedArgument &arg, const DynamicArg &dyn_arg,
                         int i) {
  arg.name = dyn_arg.name;
  /*
  if (dyn_arg.elem_dim_count > 0) {
      printf("[C++ Engine] Arg %s: type=%d, dtype=%d, dim_count=%d,
  elem_dim_count=%d, elem_shape[0]=%d\n", dyn_arg.name, dyn_arg.arg_type,
  dyn_arg.dtype, dyn_arg.dim_count, dyn_arg.elem_dim_count,
  dyn_arg.elem_shape[0]); } else { printf("[C++ Engine] Arg %s: type=%d,
  dtype=%d, dim_count=%d, elem_dim_count=%d\n", dyn_arg.name, dyn_arg.arg_type,
  dyn_arg.dtype, dyn_arg.dim_count, dyn_arg.elem_dim_count);
  }
  */

  if (dyn_arg.arg_type == 1) { // Scalar
    if (dyn_arg.dtype == 0) {  // f32
      arg.argument.type = TI_ARGUMENT_TYPE_F32;
      union {
        uint64_t u;
        float f;
      } converter;
      converter.u = dyn_arg.val_u64;
      arg.argument.value.f32 = converter.f;

      FILE *f = fopen("engine_debug.log", "a");
      if (f) {
        fprintf(f, "  [Arg %d] Scalar F32: %f (raw 0x%llx)\n", i, converter.f,
                (unsigned long long)dyn_arg.val_u64);
        fclose(f);
      }
    } else { // i32 or others
      arg.argument.type = TI_ARGUMENT_TYPE_I32;
      arg.argument.value.i32 = (int32_t)dyn_arg.val_u64;

      FILE *f = fopen("engine_debug.log", "a");
      if (f) {
        fprintf(f, "  [Arg %d] Scalar I32: %d (raw 0x%llx)\n", i,
                arg.argument.value.i32, (unsigned long long)dyn_arg.val_u64);
        fclose(f);
      }
    }
  } else { // NDArray
    arg.argument.type = TI_ARGUMENT_TYPE_NDARRAY;
    arg.argument.value.ndarray.memory = (TiMemory)dyn_arg.val_u64;

    TiDataType ti_dt = TI_DATA_TYPE_F32;
    if (dyn_arg.dtype == 1)
      ti_dt = TI_DATA_TYPE_I32;
    else if (dyn_arg.dtype == 2)
      ti_dt = TI_DATA_TYPE_U8;
    else if (dyn_arg.dtype == 3)
      ti_dt = TI_DATA_TYPE_U16;

    arg.argument.value.ndarray.elem_type = ti_dt;
    arg.argument.value.ndarray.shape.dim_count = dyn_arg.dim_count;
    for (int d = 0; d < dyn_arg.dim_count; d++) {
      arg.argument.value.ndarray.shape.dims[d] = dyn_arg.shape[d];
    }
    arg.argument.value.ndarray.elem_shape.dim_count = dyn_arg.elem_dim_count;
    for (int d = 0; d < dyn_arg.elem_dim_count; d++) {
      arg.argument.value.ndarray.elem_shape.dims[d] = dyn_arg.elem_shape[d];
    }
  }
}

// -----------------------------------------------------------------------
// Generic Graph Execution with Fast Cache
// -----------------------------------------------------------------------
EXPORT void run_aot_graph(void *runtime, void *module_ctx,
                          const char *graph_name, DynamicArg *args_array,
                          int num_args) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  ModuleContext *ctx = (ModuleContext *)module_ctx;
  if (!rt || !ctx || !ctx->module || !args_array)
    return;

  try {
    clear_engine_error(engine);
    std::lock_guard<std::mutex> lock(ctx->cache_mutex);
    std::string gname(graph_name);
    auto it = ctx->graph_cache.find(gname);
    if (it == ctx->graph_cache.end()) {
      ti::ComputeGraph g = ctx->module->get_compute_graph(graph_name);
      it = ctx->graph_cache.emplace(std::move(gname), std::move(g)).first;
    }
    ti::ComputeGraph &graph = it->second;

    std::vector<TiNamedArgument> ti_args;
    ti_args.reserve(num_args);
    for (int i = 0; i < num_args; i++) {
      TiNamedArgument arg = {};
      _fill_ti_arg(arg, args_array[i], i);
      ti_args.push_back(arg);
    }

    // Clear any stale errors before launch
    uint64_t junk_size = 0;
    ti_get_last_error(&junk_size, nullptr);

    {
      FILE *f = fopen("engine_debug.log", "a");
      if (f) {
        fprintf(f, "[C++ Engine] Launching graph '%s' with %d args...\n",
                graph_name, num_args);
        fclose(f);
      }
    }

    graph.launch(ti_args);

    {
      FILE *f = fopen("engine_debug.log", "a");
      if (f) {
        fprintf(f, "[C++ Engine] Graph '%s' launched successfully.\n",
                graph_name);
        fclose(f);
      }
    }

    // Check for launch errors
    uint64_t msg_size = 0;
    ti_get_last_error(&msg_size, nullptr);
    if (msg_size > 1) { // 1 because sometimes it might be just \0
      std::vector<char> msg(msg_size);
      ti_get_last_error(&msg_size, msg.data());
      if (msg[0] != '\0') {
        set_engine_error(engine, std::string("run_aot_graph: ") + msg.data());
        printf("[C++ Engine] ERROR in run_aot_graph launch: %s\n", msg.data());
      }
    }
    fflush(stdout);
  } catch (const std::exception &e) {
    set_engine_error(engine, std::string("run_aot_graph exception: ") + e.what());
    printf("[C++ Engine] EXCEPTION in run_aot_graph: %s\n", e.what());
    fflush(stdout);
  } catch (...) {
    set_engine_error(engine, "run_aot_graph unknown exception");
    printf("[C++ Engine] UNKNOWN EXCEPTION in run_aot_graph\n");
    fflush(stdout);
  }
}

// -----------------------------------------------------------------------
// Pipeline Recording & Execution
// -----------------------------------------------------------------------

EXPORT void clear_pipeline(void *module_ctx, const char *pipeline_name) {
  ModuleContext *mod = (ModuleContext *)module_ctx;
  if (mod && mod->owner) {
    std::lock_guard<std::mutex> lock(mod->owner->mutex);
    mod->owner->pipelines.erase(pipeline_name);
    return;
  }

  {
    std::lock_guard<std::mutex> lock(pipelines_mutex);
    global_pipelines.erase(pipeline_name);
  }
  std::lock_guard<std::mutex> lock(engine_contexts_mutex);
  for (auto *ctx : engine_contexts) {
    if (!ctx)
      continue;
    std::lock_guard<std::mutex> ctx_lock(ctx->mutex);
    ctx->pipelines.erase(pipeline_name);
  }
}

EXPORT void add_to_pipeline(void *module_ctx, const char *pipeline_name,
                            const char *graph_name, DynamicArg *args_array,
                            int num_args) {
  ModuleContext *mod = (ModuleContext *)module_ctx;
  if (!args_array || !mod)
    return;

  GraphDispatch dispatch;
  dispatch.module_ctx = module_ctx;
  dispatch.graph_name = graph_name;
  dispatch.args.reserve(num_args);
  dispatch.arg_names.reserve(num_args);

  for (int i = 0; i < num_args; i++) {
    DynamicArg arg = args_array[i];
    // Allocate storage for name string to keep it alive
    dispatch.arg_names.push_back(args_array[i].name);
    arg.name = dispatch.arg_names.back().c_str();
    dispatch.args.push_back(arg);
  }

  if (mod->owner) {
    std::lock_guard<std::mutex> lock(mod->owner->mutex);
    mod->owner->pipelines[pipeline_name].steps.push_back(std::move(dispatch));
  } else {
    std::lock_guard<std::mutex> lock(pipelines_mutex);
    global_pipelines[pipeline_name].steps.push_back(std::move(dispatch));
  }
}

EXPORT void run_pipeline(void *runtime, const char *pipeline_name,
                         uint64_t *old_handles, DynamicArg *new_args,
                         int num_overrides) {
  EngineContext *engine = as_engine(runtime);
  ti::Runtime *rt = engine_runtime(engine);
  if (!rt)
    return;

  Pipeline pipe;
  {
    bool found = false;
    if (engine) {
      std::lock_guard<std::mutex> lock(engine->mutex);
      auto it_pipe = engine->pipelines.find(pipeline_name);
      if (it_pipe != engine->pipelines.end()) {
        pipe = it_pipe->second;
        found = true;
      }
    }
    if (!found) {
      std::lock_guard<std::mutex> lock(pipelines_mutex);
      auto it_pipe = global_pipelines.find(pipeline_name);
      if (it_pipe != global_pipelines.end()) {
        pipe = it_pipe->second;
        found = true;
      }
    }
    if (!found) {
      set_engine_error(engine, std::string("Pipeline not found: ") + pipeline_name);
      printf("[C++ Engine] ERROR: Pipeline '%s' not found!\n", pipeline_name);
      fflush(stdout);
      return;
    }
  }
  if (pipe.steps.empty()) {
    printf("[C++ Engine] WARNING: Pipeline '%s' has 0 steps.\n", pipeline_name);
    fflush(stdout);
    return;
  }

  try {
    clear_engine_error(engine);
    for (auto &step : pipe.steps) {
      ModuleContext *ctx = (ModuleContext *)step.module_ctx;
      if (!ctx)
        continue;

      std::lock_guard<std::mutex> lock(ctx->cache_mutex);
      auto it_g = ctx->graph_cache.find(step.graph_name);
      if (it_g == ctx->graph_cache.end()) {
        ti::ComputeGraph g =
            ctx->module->get_compute_graph(step.graph_name.c_str());
        it_g = ctx->graph_cache.emplace(step.graph_name, std::move(g)).first;
      }
      ti::ComputeGraph &graph = it_g->second;

      std::vector<TiNamedArgument> ti_args;
      ti_args.reserve(step.args.size());

      int arg_idx = 0;
      for (const auto &base_arg : step.args) {
        TiNamedArgument arg = {};

        // Check for overrides by memory handle identity
        const DynamicArg *final_arg = &base_arg;
        if (base_arg.arg_type == 0) {
          uint64_t current_handle = base_arg.val_u64;
          for (int j = 0; j < num_overrides; j++) {
            if (old_handles[j] == current_handle) {
              final_arg = &new_args[j];
              break;
            }
          }
        }
        _fill_ti_arg(arg, *final_arg, arg_idx++);

        // CRITICAL: Always use the original name from the recorded step.
        // The override argument from Python might have a generic name like
        // "override".
        arg.name = base_arg.name;

        ti_args.push_back(arg);
      }

      graph.launch(ti_args);
    }

    // Final synchronization is optional, but we'll remove it to allow
    // pipelining. rt->wait();

    // Check for error once after the whole pipeline launch
    uint64_t msg_size = 0;
    ti_get_last_error(&msg_size, nullptr);
    if (msg_size > 1) {
      std::vector<char> msg(msg_size);
      ti_get_last_error(&msg_size, msg.data());
      if (msg[0] != '\0') {
        set_engine_error(engine, std::string("run_pipeline: ") + msg.data());
        printf("[C++ Engine] ERROR in pipeline '%s': %s\n", pipeline_name,
               msg.data());
      }
    }
    fflush(stdout);
  } catch (const std::exception &e) {
    set_engine_error(engine, std::string("run_pipeline exception: ") + e.what());
    printf("[C++ Engine] EXCEPTION in run_pipeline: %s\n", e.what());
    fflush(stdout);
  } catch (...) {
    set_engine_error(engine, "run_pipeline unknown exception");
    printf("[C++ Engine] UNKNOWN EXCEPTION in run_pipeline\n");
    fflush(stdout);
  }
}

} // extern "C"
