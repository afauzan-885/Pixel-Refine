import taichi as ti
import numpy as np
import os
import sys

# Tambahkan project root ke sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@ti.kernel
def compute_laplacian_energy_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), 
                                   energy: ti.types.ndarray(dtype=ti.f32, ndim=2)):
    """
    Menghitung energi Laplacian (sum of squares) untuk estimasi noise.
    """
    for i, j in src:
        if i > 0 and i < src.shape[0] - 1 and j > 0 and j < src.shape[1] - 1:
            center = src[i, j]
            neighbor_sum = src[i-1, j] + src[i+1, j] + src[i, j-1] + src[i, j+1]
            lap = neighbor_sum - 4.0 * center
            energy[i, j] = lap * lap
        else:
            energy[i, j] = 0.0

def compile_noise_estimation():
    ti.init(arch=ti.vulkan)
    
    module = ti.aot.Module(ti.vulkan)
    
    # Argumen simbolik untuk Graph
    sym_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'src', dtype=ti.f32, ndim=2)
    sym_energy = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'energy', dtype=ti.f32, ndim=2)
    
    g_builder = ti.graph.GraphBuilder()
    g_builder.dispatch(compute_laplacian_energy_kernel, sym_src, sym_energy)
    graph = g_builder.compile()
    
    module.add_graph('compute_laplacian_energy', graph)
    
    # Save path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets/noise_estimation"))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    module.save(output_dir) 
    print(f"Noise estimation kernel compiled as GRAPH to: {output_dir}")

if __name__ == "__main__":
    compile_noise_estimation()
