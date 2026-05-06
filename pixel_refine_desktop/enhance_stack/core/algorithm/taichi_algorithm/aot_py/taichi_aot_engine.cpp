#include <taichi/cpp/taichi.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <unordered_map>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {

// -----------------------------------------------------------------------
// Dynamic Argument Structure
// -----------------------------------------------------------------------
struct DynamicArg {
    const char* name;
    int is_ndarray; // 0=Int32, 1=Float32, 2=NDArray
    int32_t val_i32;
    float val_f32;
    TiMemory ndarray_memory;
    int elem_type; // TiDataType enum value
    int dim_count;
    uint32_t shape[8];
    int elem_dim_count;
    uint32_t elem_shape[8];
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

EXPORT void sync_runtime(void* runtime) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (rt) rt->wait();
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
        
        // If not in cache, create and MOVE into map
        if (it == ctx->graph_cache.end()) {
            ti::ComputeGraph g = ctx->module->get_compute_graph(graph_name);
            it = ctx->graph_cache.emplace(std::move(gname), std::move(g)).first;
        }
        
        // Use reference to the cached graph
        ti::ComputeGraph& graph = it->second;

        std::vector<TiNamedArgument> ti_args;
        ti_args.reserve(num_args);
        
        for (int i = 0; i < num_args; i++) {
            TiNamedArgument arg = {};
            arg.name = args_array[i].name;
            
            if (args_array[i].is_ndarray == 0) {
                arg.argument.type = TI_ARGUMENT_TYPE_I32;
                arg.argument.value.i32 = args_array[i].val_i32;
            } else if (args_array[i].is_ndarray == 1) {
                arg.argument.type = TI_ARGUMENT_TYPE_F32;
                arg.argument.value.f32 = args_array[i].val_f32;
            } else if (args_array[i].is_ndarray == 2) {
                arg.argument.type = TI_ARGUMENT_TYPE_NDARRAY;
                arg.argument.value.ndarray.memory = args_array[i].ndarray_memory;
                arg.argument.value.ndarray.elem_type = (TiDataType)args_array[i].elem_type;
                
                arg.argument.value.ndarray.shape.dim_count = args_array[i].dim_count;
                for (int d = 0; d < args_array[i].dim_count; d++) {
                    arg.argument.value.ndarray.shape.dims[d] = args_array[i].shape[d];
                }
                
                arg.argument.value.ndarray.elem_shape.dim_count = args_array[i].elem_dim_count;
                for (int d = 0; d < args_array[i].elem_dim_count; d++) {
                    arg.argument.value.ndarray.elem_shape.dims[d] = args_array[i].elem_shape[d];
                }
            }
            ti_args.push_back(arg);
        }

        graph.launch(ti_args);
        // rt->wait(); // Removed for extreme performance!
    } catch (...) {}
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
        dispatch.arg_names.push_back(args_array[i].name);
        DynamicArg arg = args_array[i];
        arg.name = dispatch.arg_names.back().c_str(); // Point to stable memory
        dispatch.args.push_back(arg);
    }
    
    global_pipelines[pipeline_name].steps.push_back(std::move(dispatch));
}

EXPORT void run_pipeline(
    void* runtime, void* dummy_module_ctx, const char* pipeline_name,
    DynamicArg* overrides, int num_overrides
) {
    ti::Runtime* rt = (ti::Runtime*)runtime;
    if (!rt) return;

    auto it_pipe = global_pipelines.find(pipeline_name);
    if (it_pipe == global_pipelines.end()) return;

    Pipeline& pipe = it_pipe->second;

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
                arg.name = base_arg.name;

                // Check for overrides by name
                const DynamicArg* final_arg = &base_arg;
                for (int j = 0; j < num_overrides; j++) {
                    if (strcmp(overrides[j].name, base_arg.name) == 0) {
                        final_arg = &overrides[j];
                        break;
                    }
                }

                if (final_arg->is_ndarray == 0) {
                    arg.argument.type = TI_ARGUMENT_TYPE_I32;
                    arg.argument.value.i32 = final_arg->val_i32;
                } else if (final_arg->is_ndarray == 1) {
                    arg.argument.type = TI_ARGUMENT_TYPE_F32;
                    arg.argument.value.f32 = final_arg->val_f32;
                } else if (final_arg->is_ndarray == 2) {
                    arg.argument.type = TI_ARGUMENT_TYPE_NDARRAY;
                    arg.argument.value.ndarray.memory = final_arg->ndarray_memory;
                    arg.argument.value.ndarray.elem_type = (TiDataType)final_arg->elem_type;
                    arg.argument.value.ndarray.shape.dim_count = final_arg->dim_count;
                    for (int d = 0; d < final_arg->dim_count; d++) {
                        arg.argument.value.ndarray.shape.dims[d] = final_arg->shape[d];
                    }
                    arg.argument.value.ndarray.elem_shape.dim_count = final_arg->elem_dim_count;
                    for (int d = 0; d < final_arg->elem_dim_count; d++) {
                        arg.argument.value.ndarray.elem_shape.dims[d] = final_arg->elem_shape[d];
                    }
                }
                ti_args.push_back(arg);
            }
            graph.launch(ti_args);
        }
        rt->wait();
    } catch (...) {}
}

} // extern "C"
