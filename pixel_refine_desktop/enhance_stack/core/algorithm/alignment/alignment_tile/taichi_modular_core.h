#ifndef TAICHI_MODULAR_CORE_H
#define TAICHI_MODULAR_CORE_H

#include <taichi/taichi.h>
#include <vector>
#include <string>
#include <map>

// Shared Context structure to be passed between DLLs
struct TaichiContext {
    TiRuntime runtime;
    std::map<std::string, TiAotModule> modules;
    std::map<std::string, TiComputeGraph> graphs;
    bool initialized = false;
};

// Helper for error checking
#define TI_CHECK(cond) \
    if (!(cond)) return -1;

#endif // TAICHI_MODULAR_CORE_H
