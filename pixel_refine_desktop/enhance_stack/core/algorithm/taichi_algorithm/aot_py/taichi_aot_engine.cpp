#include <taichi/cpp/taichi.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <unordered_map>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#include <windows.h>
#include <wincodec.h>
#pragma comment(lib, "windowscodecs.lib")
#else
#define EXPORT
#endif

// Forward declaration for WIC factory (global for performance)
#ifdef _WIN32
static IWICImagingFactory* g_wic_factory = nullptr;
static void init_wic() {
    if (!g_wic_factory) {
        CoInitializeEx(NULL, COINIT_MULTITHREADED);
        CoCreateInstance(CLSID_WICImagingFactory, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&g_wic_factory));
    }
}
#endif

extern "C" {

// -----------------------------------------------------------------------
// Dynamic Argument Structure
// -----------------------------------------------------------------------
struct DynamicArg {
    const char* name;
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

// -----------------------------------------------------------------------
// Pipeline Structures (Global)
// -----------------------------------------------------------------------
struct GraphDispatch {
    void* module_ctx;
    std::string graph_name;
    std::vector<DynamicArg> args;
    std::vector<std::string> arg_names; // Storage for name pointers
};

struct Pipeline {
    std::vector<GraphDispatch> steps;
};

static std::unordered_map<std::string, Pipeline> global_pipelines;

// -----------------------------------------------------------------------
// Internal Cache for Graphics Objects
// -----------------------------------------------------------------------
struct ModuleContext {
    ti::AotModule* module;
    std::unordered_map<std::string, ti::ComputeGraph> graph_cache;
};

// -----------------------------------------------------------------------
// Runtime & Module Management
// -----------------------------------------------------------------------
EXPORT const char* scan_vulkan_devices() {
    static std::string device_list;
    device_list = "";
#ifdef _WIN32
    FILE* pipe = _popen("vulkaninfo --summary", "r");
#else
    FILE* pipe = popen("vulkaninfo --summary", "r");
#endif
    if (!pipe) return "";
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
                if (!device_list.empty()) device_list += ";";
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

EXPORT void* init_aot_engine(int arch_id, int device_id) {
    try {
        TiArch arch = TI_ARCH_VULKAN;
        if (arch_id == 1) arch = TI_ARCH_CUDA;
        else if (arch_id == 2) arch = TI_ARCH_X64;
        
        // Use specified device_id
        return (void*)(new ti::Runtime(arch, (uint32_t)device_id));
    } catch (...) { 
        // Fallback to CPU if GPU initialization fails
        try {
            return (void*)(new ti::Runtime(TI_ARCH_X64, 0));
        } catch (...) {
            return nullptr; 
        }
    }
}

EXPORT void* load_aot_module(void* runtime, const char* tcm_path) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt) return nullptr;
    try {
        ModuleContext* ctx = new ModuleContext();
        ctx->module = new ti::AotModule(rt->load_aot_module(tcm_path));
        return (void*)ctx;
    } catch (...) { return nullptr; }
}

EXPORT void destroy_aot_module(void* module_ctx) {
    ModuleContext* ctx = (ModuleContext*)module_ctx;
    if (ctx) {
        if (ctx->module) delete ctx->module;
        delete ctx;
    }
}

// -----------------------------------------------------------------------
// Memory Management
// -----------------------------------------------------------------------
EXPORT void* allocate_gpu_buffer(void* runtime, uint64_t size, int host_accessible) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt) return nullptr;
    TiMemoryAllocateInfo allocate_info = {};
    allocate_info.size = size;
    allocate_info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
    if (host_accessible) {
        allocate_info.host_write = true;
        allocate_info.host_read = true;
    }
    return (void*)ti_allocate_memory(rt->runtime(), &allocate_info);
}

EXPORT void free_gpu_buffer(void* runtime, void* memory) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (rt && memory) {
        ti_free_memory(rt->runtime(), (TiMemory)memory);
    }
}

EXPORT void write_to_gpu_buffer(void* runtime, void* memory, void* data, uint64_t size) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !memory || !data) return;
    void* ptr = ti_map_memory(rt->runtime(), (TiMemory)memory);
    if (ptr) {
        memcpy(ptr, data, size);
        ti_unmap_memory(rt->runtime(), (TiMemory)memory);
    }
}

EXPORT void read_from_gpu_buffer(void* runtime, void* memory, void* data, uint64_t size) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !memory || !data) return;
    rt->wait(); // Ensure all kernels are done before reading
    void* ptr = ti_map_memory(rt->runtime(), (TiMemory)memory);
    if (ptr) {
        memcpy(data, ptr, size);
        ti_unmap_memory(rt->runtime(), (TiMemory)memory);
    }
}

EXPORT void* map_gpu_buffer(void* runtime, void* memory) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !memory) return nullptr;
    return ti_map_memory(rt->runtime(), (TiMemory)memory);
}

EXPORT void unmap_gpu_buffer(void* runtime, void* memory) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (rt && memory) {
        ti_unmap_memory(rt->runtime(), (TiMemory)memory);
    }
}

EXPORT void copy_gpu_buffer(void* runtime, void* src, void* dst, uint64_t size) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !src || !dst) return;
    
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

EXPORT void sync_runtime(void* runtime) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (rt) rt->wait();
}

// -----------------------------------------------------------------------
// High-Performance Image IO (Smart Loader)
// -----------------------------------------------------------------------
EXPORT void* ti_imread_to_gpu(
    void* runtime, const char* path, 
    int* out_width, int* out_height, int* out_channels, int* out_bit_depth
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !path) return nullptr;

#ifdef _WIN32
    init_wic();
    if (!g_wic_factory) return nullptr;

    IWICBitmapDecoder* decoder = nullptr;
    wchar_t w_path[MAX_PATH];
    MultiByteToWideChar(CP_UTF8, 0, path, -1, w_path, MAX_PATH);

    if (FAILED(g_wic_factory->CreateDecoderFromFilename(w_path, NULL, GENERIC_READ, WICDecodeMetadataCacheOnDemand, &decoder))) {
        return nullptr;
    }

    IWICBitmapFrameDecode* frame = nullptr;
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
        channels = 1; bit_depth = 8; target_format = GUID_WICPixelFormat8bppGray;
    } else if (pixel_format == GUID_WICPixelFormat16bppGray) {
        channels = 1; bit_depth = 16; target_format = GUID_WICPixelFormat16bppGray;
    } else if (pixel_format == GUID_WICPixelFormat24bppBGR || pixel_format == GUID_WICPixelFormat32bppBGRA) {
        channels = 3; bit_depth = 8; target_format = GUID_WICPixelFormat24bppBGR;
    } else if (pixel_format == GUID_WICPixelFormat48bppBGR || pixel_format == GUID_WICPixelFormat64bppBGRA) {
        channels = 3; bit_depth = 16; target_format = GUID_WICPixelFormat48bppBGR;
    } else {
        // Default fallback to 8-bit BGR
        channels = 3; bit_depth = 8; target_format = GUID_WICPixelFormat24bppBGR;
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
        frame->Release(); decoder->Release(); return nullptr;
    }

    // Copy pixels directly to GPU (using mapped memory if possible, or intermediate buffer)
    void* gpu_ptr = ti_map_memory(rt->runtime(), gpu_mem);
    if (gpu_ptr) {
        if (pixel_format != target_format) {
            // Need conversion
            IWICFormatConverter* converter = nullptr;
            g_wic_factory->CreateFormatConverter(&converter);
            converter->Initialize(frame, target_format, WICBitmapDitherTypeNone, NULL, 0.0, WICBitmapPaletteTypeCustom);
            converter->CopyPixels(NULL, (UINT)(w * channels * (bit_depth / 8)), (UINT)size_bytes, (BYTE*)gpu_ptr);
            converter->Release();
        } else {
            frame->CopyPixels(NULL, (UINT)(w * channels * (bit_depth / 8)), (UINT)size_bytes, (BYTE*)gpu_ptr);
        }
        ti_unmap_memory(rt->runtime(), gpu_mem);
    }

    frame->Release();
    decoder->Release();
    return (void*)gpu_mem;

#else
    // TODO: Implement for Linux/Android using stb_image or similar
    return nullptr;
#endif
}

EXPORT bool ti_imwrite_from_gpu(
    void* runtime, const char* path, void* gpu_mem,
    int width, int height, int channels, int bit_depth
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !path || !gpu_mem) return false;

#ifdef _WIN32
    init_wic();
    if (!g_wic_factory) return false;

    IWICStream* stream = nullptr;
    g_wic_factory->CreateStream(&stream);
    
    wchar_t w_path[MAX_PATH];
    MultiByteToWideChar(CP_UTF8, 0, path, -1, w_path, MAX_PATH);

    if (FAILED(stream->InitializeFromFilename(w_path, GENERIC_WRITE))) {
        stream->Release(); return false;
    }

    IWICBitmapEncoder* encoder = nullptr;
    // Auto-detect encoder based on extension
    GUID encoder_guid = GUID_ContainerFormatPng;
    std::string s_path = path;
    if (s_path.find(".jpg") != std::string::npos || s_path.find(".jpeg") != std::string::npos) {
        encoder_guid = GUID_ContainerFormatJpeg;
    } else if (s_path.find(".tif") != std::string::npos) {
        encoder_guid = GUID_ContainerFormatTiff;
    }

    if (FAILED(g_wic_factory->CreateEncoder(encoder_guid, NULL, &encoder))) {
        stream->Release(); return false;
    }

    encoder->Initialize(stream, WICBitmapEncoderNoCache);

    IWICBitmapFrameEncode* frame = nullptr;
    encoder->CreateNewFrame(&frame, NULL);
    frame->Initialize(NULL);
    frame->SetSize(width, height);

    WICPixelFormatGUID format_guid = GUID_WICPixelFormat8bppGray;
    if (bit_depth == 8) {
        format_guid = (channels == 1) ? GUID_WICPixelFormat8bppGray : GUID_WICPixelFormat24bppBGR;
    } else {
        format_guid = (channels == 1) ? GUID_WICPixelFormat16bppGray : GUID_WICPixelFormat48bppBGR;
    }

    frame->SetPixelFormat(&format_guid);

    void* gpu_ptr = ti_map_memory(rt->runtime(), (TiMemory)gpu_mem);
    if (gpu_ptr) {
        UINT stride = width * channels * (bit_depth / 8);
        UINT size = stride * height;
        frame->WritePixels(height, stride, size, (BYTE*)gpu_ptr);
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

EXPORT bool ti_cast_buffer(
    void* runtime, void* src_mem, void* dst_mem, 
    int num_elements, int src_type, int dst_type
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt || !src_mem || !dst_mem) return false;

    void* src_ptr = ti_map_memory(rt->runtime(), (TiMemory)src_mem);
    void* dst_ptr = ti_map_memory(rt->runtime(), (TiMemory)dst_mem);

    if (src_ptr && dst_ptr) {
        // Simple and fast C++ casting loop (can be optimized with SIMD)
        if (src_type == 0 && dst_type == 2) { // f32 -> u8
            float* s = (float*)src_ptr;
            uint8_t* d = (uint8_t*)dst_ptr;
            for (int i = 0; i < num_elements; ++i) d[i] = (uint8_t)(s[i] * 255.0f + 0.5f);
        } else if (src_type == 2 && dst_type == 0) { // u8 -> f32
            uint8_t* s = (uint8_t*)src_ptr;
            float* d = (float*)dst_ptr;
            for (int i = 0; i < num_elements; ++i) d[i] = (float)s[i] / 255.0f;
        } else if (src_type == 0 && dst_type == 3) { // f32 -> u16
            float* s = (float*)src_ptr;
            uint16_t* d = (uint16_t*)dst_ptr;
            for (int i = 0; i < num_elements; ++i) d[i] = (uint16_t)(s[i] * 65535.0f + 0.5f);
        } else if (src_type == 3 && dst_type == 0) { // u16 -> f32
            uint16_t* s = (uint16_t*)src_ptr;
            float* d = (float*)dst_ptr;
            for (int i = 0; i < num_elements; ++i) d[i] = (float)s[i] / 65535.0f;
        }
        ti_unmap_memory(rt->runtime(), (TiMemory)src_mem);
        ti_unmap_memory(rt->runtime(), (TiMemory)dst_mem);
        return true;
    }
    return false;
}

// -----------------------------------------------------------------------
// Internal Helper for Argument Mapping
// -----------------------------------------------------------------------
static void _fill_ti_arg(TiNamedArgument& arg, const DynamicArg& dyn_arg) {
    arg.name = dyn_arg.name;
    /*
    if (dyn_arg.elem_dim_count > 0) {
        printf("[C++ Engine] Arg %s: type=%d, dtype=%d, dim_count=%d, elem_dim_count=%d, elem_shape[0]=%d\n", 
               dyn_arg.name, dyn_arg.arg_type, dyn_arg.dtype, dyn_arg.dim_count, dyn_arg.elem_dim_count, dyn_arg.elem_shape[0]);
    } else {
        printf("[C++ Engine] Arg %s: type=%d, dtype=%d, dim_count=%d, elem_dim_count=%d\n", 
               dyn_arg.name, dyn_arg.arg_type, dyn_arg.dtype, dyn_arg.dim_count, dyn_arg.elem_dim_count);
    }
    */

    if (dyn_arg.arg_type == 1) { // Scalar
        if (dyn_arg.dtype == 0) { // f32
            arg.argument.type = TI_ARGUMENT_TYPE_F32;
            union { uint64_t u; float f; } converter;
            converter.u = dyn_arg.val_u64;
            arg.argument.value.f32 = converter.f;
        } else { // i32 or others
            arg.argument.type = TI_ARGUMENT_TYPE_I32;
            arg.argument.value.i32 = (int32_t)dyn_arg.val_u64;
        }
    } else { // NDArray
        arg.argument.type = TI_ARGUMENT_TYPE_NDARRAY;
        arg.argument.value.ndarray.memory = (TiMemory)dyn_arg.val_u64;
        
        TiDataType ti_dt = TI_DATA_TYPE_F32;
        if (dyn_arg.dtype == 1) ti_dt = TI_DATA_TYPE_I32;
        else if (dyn_arg.dtype == 2) ti_dt = TI_DATA_TYPE_U8;
        else if (dyn_arg.dtype == 3) ti_dt = TI_DATA_TYPE_U16;
        
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
EXPORT void run_aot_graph(
    void* runtime, void* module_ctx, const char* graph_name,
    DynamicArg* args_array, int num_args
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    ModuleContext* ctx = (ModuleContext*)module_ctx;
    if (!rt || !ctx || !ctx->module || !args_array) return;

    try {
        std::string gname(graph_name);
        auto it = ctx->graph_cache.find(gname);
        if (it == ctx->graph_cache.end()) {
            ti::ComputeGraph g = ctx->module->get_compute_graph(graph_name);
            it = ctx->graph_cache.emplace(std::move(gname), std::move(g)).first;
        }
        ti::ComputeGraph& graph = it->second;

        std::vector<TiNamedArgument> ti_args;
        ti_args.reserve(num_args);
        for (int i = 0; i < num_args; i++) {
            TiNamedArgument arg = {};
            _fill_ti_arg(arg, args_array[i]);
            ti_args.push_back(arg);
        }
        
        // Clear any stale errors before launch
        uint64_t junk_size = 0;
        ti_get_last_error(&junk_size, nullptr);
        
        graph.launch(ti_args);
        
        // Check for launch errors
        uint64_t msg_size = 0;
        ti_get_last_error(&msg_size, nullptr);
        if (msg_size > 1) { // 1 because sometimes it might be just \0
            std::vector<char> msg(msg_size);
            ti_get_last_error(&msg_size, msg.data());
            if (msg[0] != '\0') {
                printf("[C++ Engine] ERROR in run_aot_graph launch: %s\n", msg.data());
            }
        }
        fflush(stdout);
    } catch (const std::exception& e) {
        printf("[C++ Engine] EXCEPTION in run_aot_graph: %s\n", e.what());
        fflush(stdout);
    } catch (...) {
        printf("[C++ Engine] UNKNOWN EXCEPTION in run_aot_graph\n");
        fflush(stdout);
    }
}

// -----------------------------------------------------------------------
// Pipeline Recording & Execution
// -----------------------------------------------------------------------

EXPORT void clear_pipeline(void* module_ctx, const char* pipeline_name) {
    global_pipelines.erase(pipeline_name);
}

EXPORT void add_to_pipeline(
    void* module_ctx, const char* pipeline_name, const char* graph_name,
    DynamicArg* args_array, int num_args
) {
    if (!args_array) return;

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
    
    global_pipelines[pipeline_name].steps.push_back(std::move(dispatch));
}

EXPORT void run_pipeline(
    void* runtime, const char* pipeline_name,
    uint64_t* old_handles, DynamicArg* new_args, int num_overrides
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt) return;

    auto it_pipe = global_pipelines.find(pipeline_name);
    if (it_pipe == global_pipelines.end()) {
        printf("[C++ Engine] ERROR: Pipeline '%s' not found!\n", pipeline_name);
        fflush(stdout);
        return;
    }

    Pipeline& pipe = it_pipe->second;
    if (pipe.steps.empty()) {
        printf("[C++ Engine] WARNING: Pipeline '%s' has 0 steps.\n", pipeline_name);
        fflush(stdout);
        return;
    }

    try {
        for (auto& step : pipe.steps) {
            ModuleContext* ctx = (ModuleContext*)step.module_ctx;
            if (!ctx) continue;

            auto it_g = ctx->graph_cache.find(step.graph_name);
            if (it_g == ctx->graph_cache.end()) {
                ti::ComputeGraph g = ctx->module->get_compute_graph(step.graph_name.c_str());
                it_g = ctx->graph_cache.emplace(step.graph_name, std::move(g)).first;
            }
            ti::ComputeGraph& graph = it_g->second;

            std::vector<TiNamedArgument> ti_args;
            ti_args.reserve(step.args.size());

            for (const auto& base_arg : step.args) {
                TiNamedArgument arg = {};
                
                // Check for overrides by memory handle identity
                const DynamicArg* final_arg = &base_arg;
                if (base_arg.arg_type == 0) {
                    uint64_t current_handle = base_arg.val_u64;
                    for (int j = 0; j < num_overrides; j++) {
                        if (old_handles[j] == current_handle) {
                            final_arg = &new_args[j];
                            break;
                        }
                    }
                }
                _fill_ti_arg(arg, *final_arg);
                
                // CRITICAL: Always use the original name from the recorded step.
                // The override argument from Python might have a generic name like "override".
                arg.name = base_arg.name;
                
                ti_args.push_back(arg);
            }

            graph.launch(ti_args);
        }
        
        // Final synchronization is optional, but we'll remove it to allow pipelining.
        // rt->wait(); 
        
        // Check for error once after the whole pipeline launch
        uint64_t msg_size = 0;
        ti_get_last_error(&msg_size, nullptr);
        if (msg_size > 1) {
            std::vector<char> msg(msg_size);
            ti_get_last_error(&msg_size, msg.data());
            if (msg[0] != '\0') {
                printf("[C++ Engine] ERROR in pipeline '%s': %s\n", pipeline_name, msg.data());
            }
        }
        fflush(stdout);
    } catch (const std::exception& e) {
        printf("[C++ Engine] EXCEPTION in run_pipeline: %s\n", e.what());
        fflush(stdout);
    } catch (...) {
        printf("[C++ Engine] UNKNOWN EXCEPTION in run_pipeline\n");
        fflush(stdout);
    }
}

} // extern "C"
